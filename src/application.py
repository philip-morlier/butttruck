import time
import argparse
from sched import scheduler

from src.looper.tttruck import TTTruck
from src.osc.osc_client import OSCClient
from src.osc.osc_server import OSCServer
from src.udp.peers import PeerClient
import src.looper.midi as midi
from src.udp.wav_slicer import WavSlicer


class BuTTTruck:
    scheduled_tasks = scheduler(time.time, time.sleep)
    sooperlooper = None
    from concurrent.futures import ThreadPoolExecutor
    pool = ThreadPoolExecutor()

    @staticmethod
    def main(config=None):
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

        BuTTTruck.scheduled_tasks.enter(0, 1, periodic, (BuTTTruck.scheduled_tasks, 0.05, process_incoming))
        BuTTTruck.scheduled_tasks.enter(10, 2, periodic, (BuTTTruck.scheduled_tasks, 30, process_loops))
        BuTTTruck.scheduled_tasks.enter(30, 2, periodic, (BuTTTruck.scheduled_tasks, 60, resend_missing_chunks))

        if peers is not None:
            peer_list = peers.strip('\'').split(',')
            for i in peer_list:
                ip, port = i.split(':')
                PeerClient.add_peer((ip, int(port)), server=False)
        else:
            PeerClient.add_peer((server_host, server_port), server=True)

        BuTTTruck.pool.submit(OSCClient.start(host=sl_host, port=sl_port, debug=debug))
        BuTTTruck.pool.submit(BuTTTruck.scheduled_tasks.run)
        BuTTTruck.pool.submit(PeerClient.run)
        BuTTTruck.pool.submit(midi.run)
        OSCServer.start(debug=debug)

    @classmethod
    def exit(cls):
        if cls.sooperlooper:
            cls.sooperlooper.kill()
        PeerClient.exit()
        OSCClient.exit()
        for i in BuTTTruck.scheduled_tasks.queue:
            cls.scheduled_tasks.cancel(i)
        cls.pool.shutdown(cancel_futures=True, wait=False)


global loops
loops = {}
global resend_queue
resend_queue = {}


def periodic(scheduler, interval, action, actionargs=()):
    scheduler.enter(interval, 1, periodic,
                    (scheduler, interval, action, actionargs))
    action(*actionargs)


def process_incoming():
    while PeerClient.receive_queue:
        incoming_bytes, peer = PeerClient.receive_queue.pop()
        import json
        msg = json.loads(incoming_bytes)
        try:
            if msg['action']:
                action = msg['action']
                if action == 'ping':
                    state = msg['state']
                    resend_queue[peer] = state
                    print(f'Current state: {state}, resend_queue: {resend_queue[peer]}')
                if action == 'loop_add':
                    message = msg['message']
                    loop_name = message['loop_name']
                    if loops.get(loop_name, None) is not None:
                        loops[loop_name].pop(message['current_chunk'] - 1)
                        loops[loop_name].insert(message['current_chunk'] - 1, message['chunk_body'].encode('latin1'))
                    else:
                        loops[message['loop_name']] = [None for i in range(message['number_of_chunks'])]
                        loops[loop_name].pop(message['current_chunk'] - 1)
                        loops[loop_name].insert(message['current_chunk'] - 1, message['chunk_body'].encode('latin1'))
                if action == 'loop_modify':
                    message = msg['message']
                    loop = message['loop_name']
                    # TODO: apply {change:value} to loop
        except Exception as e:
            print(f'Unable to receive data {msg} from: {peer.get_address()}')


def resend_missing_chunks():
    for peer, state in resend_queue.items():
        for name, chunks in state.items():
            print(f'resending {peer}, {name}, {chunks}')
            for chunk in chunks:
                WavSlicer.slice_and_send(name, chunk, peer=peer)


def process_loops():
    completed = []
    for k, v in loops.items():
        if not v.__contains__(None):
            print('success')
            completed.append((k, v))
    while completed:
        c = completed.pop()
        TTTruck._write_wav(c)
        loops.pop(c[0])


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
