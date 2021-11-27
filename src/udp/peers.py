import json
import logging
import math
import pickle
import select
import socket
import time
import json
from collections import deque

from src.looper.sl_client import SLClient


class Peer(socket.socket):
    def __init__(self, addr, x, y, server):
        super().__init__(x, y)
        self.address = addr
        self.server = server
        self.receiving_status = {}
        self.sending_status = {}

    def get_address(self):
        return self.address

    def is_server(self):
        return self.server

    def set_receiving_status(self, loop, status):
        self.receiving_status[loop] = status

    def update_receiving_status(self, loop, chunk):
        self.receiving_status[loop].remove(chunk)

    def clear_receiving_status(self, loop):
        self.receiving_status.pop(loop)

    def get_receiving_status(self):
        return self.receiving_status

    def get_sending_status(self):
        return self.sending_status


class PeerClient:
    """Needs to create a standard 'ping' message which conforms to shared data structure"""

    server = None
    data = b''
    receive_queue = deque()
    send_queue = deque()
    inputs = []
    outputs = []
    current_peers = {}
    global_time = 0

    @classmethod
    def add_peer(cls, addr, server=False):
        peer = Peer(addr, socket.AF_INET, socket.SOCK_DGRAM, server)
        peer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        peer.setblocking(False)

        # makes local testing easier
        # if not server:
        #    peer.bind(('0.0.0.0', addr[1]))

        cls.inputs.append(peer)
        cls.outputs.append(peer)

    count = 100
    @classmethod
    def run(cls):
        while cls.outputs:
            read, write, exception = select.select(cls.inputs, cls.outputs, cls.outputs)
            msg = None
            try:
                if cls.send_queue:
                    msg, peer_resend = cls.send_queue.pop()
                    if peer_resend is not None:
                        logging.debug(f'resending to {peer_resend.get_address()}')
                        cls.send_msg(peer_resend, msg)
                    else:
                        for peer in write:
                            if not peer.server:
                                cls.send_msg(peer, msg)
                if cls.count >= 100:
                    cls.count = 0
                    for peer in write:
                        cls.send_ping(peer)
                cls.count += 1
                for peer in read:
                    cls.receive_data(peer)
                time.sleep(0.01)
            except Exception as e:
                logging.warning(f'Unable to communicate with peers {e}')
        logging.info(f'Shutting down peer service')

    @classmethod
    def receive_data(cls, peer):
        data, port = peer.recvfrom(8192)
        data = pickle.loads(data)
        print(data)
        if peer.is_server():
            cls.update_peers(data[1])
            cls.update_time(data[0])
        else:
            cls.receive_queue.append((data, peer))
            try:
                cls.update_status(data, peer)
            except Exception as e:
                logging.warning(f'Unable to update status: {e}')

    @classmethod
    def update_status(cls, data, peer):
        data = data[1]
        if data:
            if data['action'] == 'loop_add':
                message = data['message']
                loop_name = message['loop_name']
                received = message['current_chunk']
                total = message['number_of_chunks']
                logging.debug(f'Updating status L: {loop_name}, R: {received}, T: {total}')

                if peer.get_receiving_status().get(loop_name, None) is not None:
                    logging.debug(f'removing chunk {received} from {peer.get_receiving_status()[loop_name]}')
                    peer.update_receiving_status(loop_name, received)
                    if len(peer.get_receiving_status()[loop_name]) == 0:
                        peer.clear_receiving_status(loop_name)
                        logging.debug(f'removing finished status: {loop_name} from: {peer.get_receiving_status()}')
                else:
                    peer.set_receiving_status(loop_name, [i for i in range(1, total + 1)])
                    logging.debug(f'Created new status: {peer.receiving_status}')
                    peer.update_receiving_status(loop_name, received)
            if data['action'] == 'ping':
                if data['state']:
                    # TODO: update state in resend_queue
                    logging.debug(f'Received ping with state: {data}')
                    peer.sending_status = data['state']
                    #cls.receive_queue.append(data)
                    #print(data)

    @classmethod
    def update_peers(cls, new_peers):
        if new_peers != cls.current_peers:
            diff = {key: new_peers[key] for key in set(new_peers) - set(cls.current_peers)}
            for k, v in diff.items():
                cls.add_peer((k, v))
            cls.current_peers = new_peers
            logging.info(f'Adding peers: {diff}. Current is: {cls.current_peers}')

    @classmethod
    def update_time(cls, global_time):
        cls.global_time = global_time
        logging.info(f'Server time is: {global_time}')
        # local_time = time.monotonic() * 1000
        # if local_time > global_time:
        #     cls.time_adjustment = local_time - global_time
        # if global_time < global_time:
        #     cls.time_adjustment = global_time - local_time

#        relative_loop_time =

    @staticmethod
    def send_msg(peer, msg):
        try:
            peer.sendto(msg.encode(), peer.get_address())
        except Exception as error:
            logging.warning(f"Unable to send_msg {error}")

    @staticmethod
    def send_ping(peer):
        if peer.is_server():
            peer.sendto(b'', peer.get_address())
        else:
            import json
            status = peer.get_receiving_status()
            if status:
                for k, v in status.items():
                    count = math.ceil(len(v) / 100)
                    if len(v) == 0:
                        print('Status done')
                        peer.receiving_status.pop(k)
                    for i in range(count):
                        message = json.dumps({'action': 'ping', 'message': {}, 'state': {k:v[i*100:i*100+100]}})
                        logging.debug(f'Pinging {peer.get_address()}. Current state is: {status}')
                        peer.sendto(message.encode(), peer.get_address())
            else:
                message = json.dumps({'action': 'ping', 'message': {}, 'state': {}})
                logging.debug(f'Pinging {peer.get_address()}. Current state is: {status}')
                peer.sendto(message.encode(), peer.get_address())

    @classmethod
    def exit(cls):
        cls.receive_queue = None
        cls.send_queue = None
        cls.inputs = None
        cls.outputs = None
