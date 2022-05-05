import json
import logging
import math
import pickle
import select
import socket
import time
import json

from src.looper.tttruck import TTTruck
from src.udp.peer import Peer
from src.udp.messages import send_queue, receive_queue

PROCESS_INCOMING_PERIOD = 0.5
PROCESS_LOOP_PERIOD = 5
RESEND_PERIOD = 1

class PeerClient:
    """Needs to create a standard 'ping' message which conforms to shared data structure"""

    server = None
    data = b''
    inputs = []
    outputs = []
    current_peers = {}
    loops = {}

    @classmethod
    def add_peer(cls, addr, server=False):
        peer = Peer(addr, socket.AF_INET, socket.SOCK_DGRAM, server)
        peer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        peer.setblocking(False)

        if not server:
           peer.bind(('0.0.0.0', addr[1]))

        cls.inputs.append(peer)
        cls.outputs.append(peer)

    count = 100
    @classmethod
    def run(cls):
        while True:
            read, write, exception = select.select(cls.inputs, cls.outputs, [])
            try:
                if send_queue:
                    msg = send_queue.pop()
                    for peer in write:
                        if not peer.server:
                            cls.send_msg(peer, msg)
                for peer in read:
                    cls.receive_data(peer)
                time.sleep(0.01)
            except Exception as e:
                logging.warning(f'Unable to communicate with peers', e)
        logging.info(f'Shutting down peer service')

    @classmethod
    def receive_data(cls, peer):
        data, port = peer.recvfrom(8192)
        data = json.loads(data)
        if peer.is_server():
            cls.update_peers(data)
        else:
            receive_queue.append((data, peer))

    @classmethod
    def update_status(cls, data, peer):
        try:
            if data:
                if data['action'] == 'loop_add':
                    message = data['message']
                    loop_name = message['loop_name']
                    received = message['current_chunk']
                    total = message['number_of_chunks']
                    #                logging.debug(f'Updating status L: {loop_name}, R: {received}, T: {total}')

                    if peer.get_sending_status().get(loop_name, None) is not None:
                        logging.debug(f'removing chunk {received} from {peer.get_sending_status()[loop_name]}')
                        peer.update_sending_status(loop_name, received)
                        if len(peer.get_sending_status()[loop_name]) == 0:
                            logging.debug(f'removing finished status: {loop_name} from: {peer.get_sending_status()}')
                            peer.clear_sending_status(loop_name)
                            cls.process_loop(loop_name)
                    else:
                        peer.set_sending_status(loop_name, [i for i in range(1, total + 1)])
                        peer.update_sending_status(loop_name, received)
                        logging.debug(f'Created new status: {peer.sending_status}')
                if data['action'] == 'ping':
                    logging.debug(f'Received ping with state: {data}')
                    peer.update_receiving_status(loop_name, data['state'])
        except Exception as e:
            print(e)

    @classmethod
    def update_peers(cls, data):
        new_peers = data
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
            logging.warning(f"Unable to send_msg", error)

    @staticmethod
    def send_ping(peer):
        if peer.is_server():
            peer.sendto(b'', peer.get_address())
        else:
            import json
            status = peer.get_sending_status()
            if status:
                for k, v in status.items():
                    count = math.ceil(len(v) / 100)
                    if len(v) == 0:
                        peer.clear_sending_status(k)
                    for i in range(count):
                        message = json.dumps({'action': 'ping', 'message': {}, 'state': {k:v[i*100:i*100+100]}})
                        logging.debug(f'Pinging {peer.get_address()}. Current state is: {status}')
                        peer.sendto(message.encode(), peer.get_address())
            else:
                message = json.dumps({'action': 'ping', 'message': {}, 'state': {}})
                logging.debug(f'Pinging {peer.get_address()}. Current state is: {status}')
                peer.sendto(message.encode(), peer.get_address())

    @classmethod
    def process_incoming(cls):
        while True:
            while receive_queue:
                msg, peer = receive_queue.pop()
                try:
                    if msg['action']:
                        action = msg['action']
                        # if action == 'ping':
                        #     state = msg['state']
                        #     peer.receiving_status = state
                        #     logging.debug(f'Received ping from: {peer.get_address()}. Current state: {state}')
                        if action == 'loop_add':
                            message = msg['message']
                            loop_name = message['loop_name']
                            current_chunk = message['current_chunk']
                            if cls.loops.get(loop_name, None) is None:
                                cls.loops[loop_name] = {}
                                cls.loops[loop_name]['chunks'] = [None for i in range(message['number_of_chunks'])]
                                cls.loops[loop_name]['sync_time'] = message['sync_time']
                                cls.loops[loop_name]['chunks'].pop(current_chunk - 1)
                                cls.loops[loop_name]['chunks'].insert(current_chunk - 1, message['chunk_body'].encode('latin1'))
                                logging.debug(f'Received chunk: {current_chunk} for {loop_name} from: {peer.get_address()}.')
                            else:
                                cls.loops[loop_name]['chunks'].pop(current_chunk - 1)
                                cls.loops[loop_name]['chunks'].insert(current_chunk - 1, message['chunk_body'].encode('latin1'))
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

                        cls.update_status(msg, peer)
                except Exception as e:
                    logging.warning(f'Unable to receive data {msg} from: {peer.get_address()}', e)
                    import pdb;pdb.set_trace()
            for peer in cls.outputs:
                cls.send_ping(peer)

            time.sleep(PROCESS_INCOMING_PERIOD)


    @classmethod
    def process_loop(cls, loop_name):
        logging.debug(f'Received complete loop {loop_name}')
        loop = cls.loops.pop(loop_name)
        TTTruck.add_remote_loop(loop_name, loop)

    @classmethod
    def resend_missing_chunks(cls):
        while True:
            for peer in cls.outputs:
                status = peer.get_receiving_status()
                for name, chunks in status.items():
                    if chunks:
                        for chunk in chunks:
                            logging.debug(f'resending {peer}, {name}, {chunks}')
                            WavSlicer.slice_and_send(name, 0, chunk_number=chunk, peer=peer)
            time.sleep(RESEND_PERIOD)



    @classmethod
    def exit(cls):
        receive_queue = None
        send_queue = None
        cls.inputs = None
        cls.outputs = None
