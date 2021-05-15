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

    def get_address(self):
        return self.address

    def is_server(self):
        return self.server

class PeerClient:
    server = None
    data = b''
    id = int(77).to_bytes(3, 'little')
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
                for k,v in diff.items():
                    cls.add_peer((k, v))
                cls.current_peers = new_peers
        else:
            print('Received: ', data, 'From: ', port)
            cls.receive_queue.append(data)

    @staticmethod
    def send_msg(peer, msg):
        peer.sendto(msg, peer.get_address())

    @staticmethod
    def send_ping(peer):
        import json
        # m = {'command': 'new_loop', 'loop_id': 1234, 'sender_id':5678, 'wave_bytes': b'/x00x01'}
        # p = json.dumps(f'{m}').encode()
        peer.sendto('{}', peer.get_address())
