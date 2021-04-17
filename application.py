import time
import argparse

from src.osc.osc_client import OSCClient
from src.osc.osc_server import OSCServer
from src.udp.Peers import PeerClient


class BuTTTruck:

    @staticmethod
    def main(config=None):
        sl_host = '127.0.0.1'
        sl_port = 9951
        osc_server_host = '127.0.0.1'
        osc_server_port = 9952
        server_host = '192.168.169.23'
        server_port = 9999
        debug = True

        if config is not None:
            if config.sooperlooper_host is not None:
                sl_host = config.sooperlooper_host
            if config.sooperlooper_host is not None:
                sl_port = config.sooperlooper_host
            if config.server_host is not None:
                server_host = config.server_host
            if config.server_port is not None:
                server_port = config.server_port

        from concurrent.futures import ThreadPoolExecutor
        executor = ThreadPoolExecutor(max_workers=5)

        # OSC for sooperlooper communication
        OSCServer.start(debug=debug)
        executor.submit(OSCClient.start(host=sl_host, port=sl_port, debug=debug))

        executor.submit(process_incoming)

        # Client for sending/receiving to peers and public server
        PeerClient.add_peer((server_host, server_port), server=True)
        executor.submit(PeerClient.run)

        # Main application interface. Midi and/or OSC control
        # TTTruck.start()


def process_incoming():
    while True:
        if PeerClient.receive_queue:
            try:
                msg = PeerClient.receive_queue.pop()
                import pickle
                print(pickle.loads(msg))
            except:
                pass
        time.sleep(0.5)


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

    args = parser.parse_args()

    ttt = BuTTTruck()
    ttt.main(args)
