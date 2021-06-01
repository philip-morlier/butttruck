import time
import argparse

from butttruck.src.looper.tttruck import TTTruck
from src.osc.osc_client import OSCClient
from src.osc.osc_server import OSCServer
from src.udp.Peers import PeerClient
import src.looper.midi as midi


class BuTTTruck:

    @staticmethod
    def main(config=None):
        sl_host = '127.0.0.1'
        sl_port = 9951
        osc_server_host = '127.0.0.1'
        osc_server_port = 9952
        server_host = '192.168.0.38'
        server_port = 9999
        debug = True

        if config is not None:
            if config.sooperlooper_host is not None:
                sl_host = config.sooperlooper_host
            if config.sooperlooper_port is not None:
                sl_port = config.sooperlooper_host
            if config.server_host is not None:
                server_host = config.server_host
            if config.server_port is not None:
                server_port = config.server_port

        from concurrent.futures import ThreadPoolExecutor
        executor = ThreadPoolExecutor(max_workers=5)

        import subprocess
        subprocess.Popen('sooperlooper')
        # OSC for sooperlooper communication
        OSCServer.start(debug=debug)
        executor.submit(OSCClient.start(host=sl_host, port=sl_port, debug=debug))

        executor.submit(process_incoming)


        # Client for sending/receiving to peers and public server
        PeerClient.add_peer((server_host, server_port), server=True)
        executor.submit(PeerClient.run)

        executor.submit(midi.run)

        # Main application interface. Midi and/or OSC control
        # TTTruck.start()



def process_incoming():
    loops = {}
    while True:
        if PeerClient.receive_queue:
            incoming_bytes = PeerClient.receive_queue.pop().decode()
            import json
            msg = json.loads(incoming_bytes)
            try:
                if msg['action']:
                    if msg['action'] == 'ping':
                        pass
                    if msg['action'] == 'loop_add':
                        loop_name = msg['message']['loop_name']
                        if loops.get(loop_name, None) is not None:
                            loops[loop_name].insert(msg['chunk_number'] - 1, msg['chunk'])
                        else:
                            loops[msg['loop_id']] = [None for i in range(msg('number_of_chunks'))]
                    else:
                        getattr(TTTruck, msg['action'])()
            except Exception as e:
                print("OMG ", e)

            # TODO Better solution for determining all wav file chunks have been received.
            for k, v in loops.items():
                if not v.__contains__(None):
                    print('success, write file and call load_loop')
                    loops.pop(msg['loop_name'])
        # PeerClient.send_queue.append(loops)
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
