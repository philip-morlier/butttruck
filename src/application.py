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
        BuTTTruck.pool.submit(PeerClient.process_incoming)
        BuTTTruck.pool.submit(PeerClient.resend_missing_chunks)
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
