import time
import argparse
import logging
from sched import scheduler

from src.looper.tttruck import TTTruck
from src.osc.osc_client import OSCClient
from src.osc.osc_server import OSCServer
from src.udp.peers import PeerClient
import src.looper.midi as midi
from src.udp.wav_slicer import WavSlicer

PROCESS_LOOP_PERIOD = 1
PROCESS_INCOMING_PERIOD = 0.05
RESEND_PERIOD = 0.2

class BuTTTruck:
    scheduled_tasks = scheduler(time.time, time.sleep)
    sooperlooper = None
    from concurrent.futures import ThreadPoolExecutor
    pool = ThreadPoolExecutor()

    @staticmethod
    def main(config=None):
        logging.basicConfig(filename='log_file.log', level=logging.DEBUG, filemode='w+',
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', force=True)

        sl_host = '127.0.0.1'
        sl_port = 9951
        server_host = '192.168.0.38'
        server_port = 9999
        debug = False
        peers = None

        if config is not None:
            if config.sooperlooper_host is not None:
                sl_host = config.sooperlooper_host
            if config.sooperlooper_port is not None:
                sl_port = config.sooperlooper_port
            if config.server_host is not None:
                server_host = config.server_host
            if config.server_port is not None:
                server_port = config.server_port
            if config.peers is not None:
                peers = config.peers

        import subprocess
        BuTTTruck.sooperlooper = subprocess.Popen(['sooperlooper', '-l', '0'])

        if peers is not None:
            peer_list = peers.strip('\'').split(',')
            for i in peer_list:
                logging.info(f'Adding peer: {i}')
                ip, port = i.split(':')
                PeerClient.add_peer((ip, int(port)), server=False)
        else:
            logging.info(f'Adding server: {server_host}:{server_port}')
            PeerClient.add_peer((server_host, server_port), server=True)

        BuTTTruck.pool.submit(OSCClient.start(host=sl_host, port=sl_port, debug=debug))
        OSCServer.start()
        BuTTTruck.pool.submit(PeerClient.run)
        BuTTTruck.pool.submit(process_incoming)
        BuTTTruck.pool.submit(resend_missing_chunks)
        BuTTTruck.pool.submit(process_loops)
        BuTTTruck.pool.submit(midi.run)


        import jack
        with jack.Client('TTTruck') as jack_client:
            capture = jack_client.get_ports(is_physical=True, is_output=True)
            output = jack_client.get_ports(is_physical=True, is_input=True)

            sooperlooper_common_in = jack_client.get_ports(name_pattern='sooperlooper.*common.*in')
            sooperlooper_common_out = jack_client.get_ports(name_pattern='sooperlooper.*common.*out')

            for src, dest in zip(sooperlooper_common_out, output):
                logging.debug(f'Connecting {src} to: {dest}')
                jack_client.connect(src, dest)

            for src, dest in zip(capture, sooperlooper_common_in):
                logging.debug(f'Connecting {src} to: {dest}')
                jack_client.connect(src, dest)


        TTTruck.add_main_loop()
        TTTruck.loop_add()

    @classmethod
    def exit(cls):
        logging.info(f'Shutting down')
        if cls.sooperlooper:
            cls.sooperlooper.kill()
        PeerClient.exit()
        OSCClient.exit()
        for i in BuTTTruck.scheduled_tasks.queue:
            cls.scheduled_tasks.cancel(i)
        cls.pool.shutdown(wait=False)
        logging.info(f'Goddbye!')


loops = {}

def process_incoming():
    while True:
        while PeerClient.receive_queue:
            msg, peer = PeerClient.receive_queue.pop()
            try:
                print(msg)
                if msg['action']:
                    action = msg['action']
                    if action == 'ping':
                        state = msg['state']
                        peer.sending_status = state
                        logging.debug(f'Received ping from: {peer.get_address()}. Current state: {state}')
                    if action == 'loop_add':
                        message = msg['message']
                        loop_name = message['loop_name']
                        current_chunk = message['current_chunk']
                        if loops.get(loop_name, None) is None:
                            loops[loop_name] = {}
                            loops[loop_name]['chunks'] = ([None for i in range(message['number_of_chunks'])])
                            loops[loop_name]['sync_time'] = message[sync_time]
                            loops[loop_name]['chunks'].pop(current_chunk - 1)
                            loops[loop_name]['chunks'].insert(current_chunk - 1, message['chunk_body'].encode('latin1'))
                            logging.debug(f'Received chunk: {current_chunk} for {loop_name} from: {peer.get_address()}.')
                        else:
                            loops[loop_name]['chunks'].pop(current_chunk - 1)
                            loops[loop_name]['chunks'].insert(current_chunk - 1, message['chunk_body'].encode('latin1'))
                            logging.debug(f'Received chunk {current_chunk} from: {peer.get_address()}. ')

                    if action == 'loop_modify':
                        message = msg['message']
                        logging.debug(f'Modifying : {message} from: {peer.get_address()}.')
                        # {'action': 'loop_add', 'message': {'loop_name': name, {'param': value},
                        loop_name = message['loop_name']
                        for param, value in message.items():
                            if param == 'loop_name':
                                continue
                            TTTruck.set_parameter(loop_name, param, value)
            except Exception as e:
                logging.warning(f'Unable to receive data {msg} from: {peer.get_address()}')
        time.sleep(PROCESS_INCOMING_PERIOD)


def resend_missing_chunks():
    while True:
        for peer in PeerClient.outputs:
            status = peer.get_sending_status()
            if status:
                for name, chunks in status.items():
                    for chunk in chunks:
                        logging.debug(f'resending {peer}, {name}, {chunks}')
                        # TODO: sync_time
                        WavSlicer.slice_and_send(name, 0, chunk_number=chunk, peer=peer)
        time.sleep(RESEND_PERIOD)
#    BuTTTruck.scheduled_tasks.enter(0.5, 1, resend_missing_chunks)
    # for peer, state in resend_queue.items():
    #     for name, chunks in state.items():
    #         logging.debug(f'resending {peer}, {name}, {chunks}')
    #         for chunk in chunks:
    #             WavSlicer.slice_and_send(name, chunk_number=chunk, peer=peer)
    #             time.sleep(0.01)


def process_loops():
    while True:
        completed = []
        for k, v in loops.items():
            if not v['chunks'].__contains__(None):
            #if not v.__contains__(None):
                logging.debug(f'Received complete loop {k}')
                completed.append((k,v))
        while completed:
            name, msg = completed.pop()
            loops.pop(name)
            TTTruck._write_wav(name, msg)
        time.sleep(PROCESS_LOOP_PERIOD)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--sooperlooper-host',
                        help='HOST:PORT for sooperlooper. Default is 127.0.0.1:9951', nargs='?', const='127.0.0.1')
    parser.add_argument('--sooperlooper-port',
                        help='PORT for sooperlooper. Default is 9951', nargs='?', const=9951)
    parser.add_argument('--debug', action="store_true",
                        help='Enable debug logging')
    parser.add_argument('--server-host',
                        help='URL for public server. Default is localhost'
                        , nargs='?', const='localhost')
    parser.add_argument('--server-port',
                        help='URL for public server. Default is 9999'
                        , nargs='?', const=9999)
    parser.add_argument('--peers',
                        help='List of peer addresses as \'ip:port,ip:port\', . Default is None'
                        , nargs='?', const=None)

    args = parser.parse_args()

    ttt = BuTTTruck()
    ttt.main(args)
