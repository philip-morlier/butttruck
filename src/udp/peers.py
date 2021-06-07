import json
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
            try:
                if cls.send_queue:
                    msg, peer_resend = cls.send_queue.pop()
                    print(msg)
                    if peer_resend:
                        cls.send_msg(peer_resend, msg)
                    else:
                        for peer in write:
                            if msg is None or peer.is_server():
                                cls.send_ping(peer)
                            else:
                                cls.send_msg(peer, msg)
                for peer in read:
                    cls.receive_data(peer)
                time.sleep(0.1)
            except Exception as e:
                print(e, 'we are in peers dot run')

    @classmethod
    def receive_data(cls, peer):
        data, port = peer.recvfrom(55000)
        if peer.is_server():
            cls.update_peers(data)
        else:
            cls.receive_queue.append((data, peer))
            try:
                cls.update_status(data, peer)
            except Exception as e:
                print('Unable to update status: ', e)

    @classmethod
    def update_status(cls, data, peer):
        data = json.loads(data)
        if data['action'] == 'loop_add':
            message = data['message']
            loop_name = message['loop_name']
            received = message['current_chunk']
            total = message['number_of_chunks']
            if peer.status.get(loop_name, None) is None:
                peer.status[loop_name] = [i for i in range(1, total + 1)]
                peer.status[loop_name].remove(received)
            elif len(peer.status[loop_name]) == 0:
                peer.status.pop(loop_name)
            else:
                peer.status[loop_name].remove(received)
        if data['action'] == 'ping':
            if data['state']:
                print(data)


    @classmethod
    def update_peers(cls, data):
        new_peers = pickle.loads(data)
        if new_peers != cls.current_peers:
            diff = {key: new_peers[key] for key in set(new_peers) - set(cls.current_peers)}
            print('Adding peers: ', diff)
            for k, v in diff.items():
                cls.add_peer((k, v))
            cls.current_peers = new_peers

    @staticmethod
    def send_msg(peer, msg):
        try:
            peer.sendto(msg.encode(), peer.get_address())
        except Exception as error:
            print(f"Unable to send_msg {error}")

    @staticmethod
    def send_ping(peer):
        if peer.is_server():
            peer.sendto(b'', peer.get_address())
        else:
            import json
            status = peer.get_status()
            message = {'action': 'ping', 'message': {}, 'state': status}
            peer.sendto(json.dumps(message).encode(), peer.get_address())

    @classmethod
    def exit(cls):
        cls.receive_queue = None
        cls.send_queue = None
        cls.inputs = None
        cls.outputs = None

