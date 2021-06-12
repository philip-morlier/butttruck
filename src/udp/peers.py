import json
import logging
import pickle
import select
import socket
import time
from collections import deque


class Peer(socket.socket):
    def __init__(self, addr, x, y, server):
        super().__init__(x, y)
        self.address = addr
        self.server = server
        self.status = {}

    def get_address(self):
        return self.address

    def is_server(self):
        return self.server

    def get_status(self):
        return self.status


class PeerClient:
    """Needs to create a standard 'ping' message which conforms to shared data structure"""

    server = None
    data = b''
    receive_queue = deque()
    send_queue = deque()
    inputs = []
    outputs = []
    current_peers = {}

    @classmethod
    def add_peer(cls, addr, server=False):
        peer = Peer(addr, socket.AF_INET, socket.SOCK_DGRAM, server)
        peer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        peer.setblocking(False)

        # makes local testing easier
        if not server:
            peer.bind(('0.0.0.0', addr[1]))

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
                    if peer_resend:
                        logging.debug(f'resending to {peer_resend.get_address()}, {msg}')
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
        if peer.is_server():
            cls.update_peers(data)
        else:
            cls.receive_queue.append((data, peer))
            try:
                cls.update_status(data, peer)
            except Exception as e:
                logging.warning(f'Unable to update status: {e}')

    @classmethod
    def update_status(cls, data, peer):
        data = json.loads(data)
        if data['action'] == 'loop_add':
            message = data['message']
            loop_name = message['loop_name']
            received = message['current_chunk']
            total = message['number_of_chunks']
            logging.debug(f'Updating status M: {message}, L: {loop_name}, R: {received}, T: {total}')
            if peer.status.get(loop_name, None) is None:
                peer.status[loop_name] = [i for i in range(1, total + 1)]
                logging.debug(f'Created new status: {peer.status}')
                peer.status[loop_name].remove(received)
            elif len(peer.status[loop_name]) == 0:
                peer.status.pop(loop_name)
                logging.debug(f'removing finished status: {loop_name} from: {peer.status}')
            else:
                logging.debug(f'removing chunk {received} from {peer.status[loop_name]}')
                peer.status[loop_name].remove(received)
        if data['action'] == 'ping':
            if data['state']:
                # TODO: update state in resend_queue
                logging.debug(f'Received ping with state: {data}')
                pass
                #print(data)

    @classmethod
    def update_peers(cls, data):
        new_peers = pickle.loads(data)
        if new_peers != cls.current_peers:
            diff = {key: new_peers[key] for key in set(new_peers) - set(cls.current_peers)}
            for k, v in diff.items():
                cls.add_peer((k, v))
            cls.current_peers = new_peers
            logging.info(f'Adding peers: {diff}. Current is: {cls.current_peers}')

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
            status = peer.get_status()
            message = json.dumps({'action': 'ping', 'message': {}, 'state': status})
            logging.debug(f'Pinging {peer.get_address()}. Current state is: {status}')
            peer.sendto(message.encode(), peer.get_address())

    @classmethod
    def exit(cls):
        cls.receive_queue = None
        cls.send_queue = None
        cls.inputs = None
        cls.outputs = None
