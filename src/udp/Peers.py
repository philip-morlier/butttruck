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

    @classmethod
    def run(cls):
        while cls.outputs:
            read, write, exception = select.select(cls.inputs, cls.outputs, cls.outputs)
            msg = None
            if cls.send_queue:
                msg = cls.send_queue.pop()

            for peer in write:
                if msg is None:
                    cls.send_ping(peer)
                elif not peer.is_server():
                    cls.send_msg(peer, msg)

            for peer in read:
                cls.receive_data(peer)
            time.sleep(0.5)

    @classmethod
    def receive_data(cls, peer):
        data, port = peer.recvfrom(55000)
        if peer.is_server():
            new_peers = pickle.loads(data)
            if new_peers != cls.current_peers:
                diff = {key: new_peers[key] for key in set(new_peers) - set(cls.current_peers)}
                print('Adding peers: ', diff)
                for k, v in diff.items():
                    cls.add_peer((k, v))
                cls.current_peers = new_peers
        else:
            cls.receive_queue.append(data)

            if data['action'] is 'loop_add':
                loop_name = data['message']['loop_name']
                cc = data['message']['current_chunk']

                if peer.status['loop_name'] is None:
                    peer.status[loop_name] = []
                else:
                    peer.status[loop_name].append(cc)

    @staticmethod
    def send_msg(peer, msg):
        try:
            peer.sendto(msg.encode(), peer.get_address())
        except Exception as error:
            print(error)

    @staticmethod
    def send_ping(peer):
        import json
        status = peer.get_status()
        message = {'action': 'ping', 'message': {}, 'state': status}
        peer.sendto(json.dumps(message).encode(), peer.get_address())
