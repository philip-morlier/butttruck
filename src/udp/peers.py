import json
import logging
import math
import pickle
import select
import socket
import time
import json

from src.looper.tttruck import TTTruck
from src.udp.wav_slicer import WavSlicer
from src.udp.peer import Peer
from src.udp.messages import send_queue, receive_queue

PROCESS_INCOMING_PERIOD = 0.2
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
        peer.setblocking(True)

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
                    msg_json = json.dumps(msg)
                    for peer in write:
                        if not peer.server:
                            cls.send_msg(peer, msg, msg_json)
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
    def update_peers(cls, data):
        new_peers = data
        if new_peers != cls.current_peers:
            diff = {key: new_peers[key] for key in set(new_peers) - set(cls.current_peers)}
            for k, v in diff.items():
                cls.add_peer((k, v))
            cls.current_peers = new_peers
            logging.info(f'Adding peers: {diff}. Current is: {cls.current_peers}')

    @staticmethod
    def send_msg(peer, msg, json):
        try:
            if msg['action'] == 'new_loop':
                peer.waiting_ack.add(msg['message']['loop_name'])
            if msg['action'] == 'loop_add' and not peer.get_receiving_status().get(msg['message']['loop_name'], False):
                return
            peer.sendto(json.encode(), peer.get_address())
        except Exception as error:
            logging.warning(f"Unable to send_msg", error)

    @staticmethod
    def send_ping(peer):
        if peer.is_server():
            peer.sendto(b'', peer.get_address())
        else:
            import json
            status = peer.get_sending_status()
            if peer.waiting_ack:
                for loop_name in peer.waiting_ack:
                    logging.debug(f'Waiting ack for {loop_name} from {peer.get_address()}')
                    WavSlicer.send_new_loop_message(TTTruck._get_loop_by_name(loop_name)[0], peer=peer)
            if status:
                state = {}
                for k, v in status.items():
                    if len(v) == 0:
                        peer.clear_sending_status(k)
                    else:
                        state[k] = v[:100]
                        logging.debug(f'Pinging {peer.get_address()} with: {s}. Current state is: {status}')
                        break
                message = json.dumps({'action': 'ping', 'message': {}, 'state': state})
                peer.sendto(message.encode(), peer.get_address())
            else:
                message = json.dumps({'action': 'ping', 'message': {}, 'state': {}})
                logging.debug(f'Pinging {peer.get_address()}. Current state is: {status}')
                peer.sendto(message.encode(), peer.get_address())

    @classmethod
    def create_empty_loop(cls, peer, loop_name, total, message):
        cls.loops[loop_name]['chunks'] = [None for i in range(total)]
        cls.loops[loop_name]['sync_time'] = message['sync_time']
        peer.set_sending_status(loop_name, [i for i in range(1, total + 1)])

    @classmethod
    def accept_loop_chunk(cls, peer, loop_name, current_chunk, chunk_body):
        try:
            if not peer.get_sending_status().get(loop_name, False):
                logging.debug(f'Accepting chunk for completed loop. Ignoring')
                return
            cls.loops[loop_name]['chunks'].pop(current_chunk)
            cls.loops[loop_name]['chunks'].insert(current_chunk, chunk_body.encode('latin1'))
        except Exception as e:
            print('Accept ', e)
        if peer.update_sending_status(loop_name, current_chunk):
            cls.process_loop(loop_name)
            peer.clear_sending_status(loop_name)

    @classmethod
    def process_incoming(cls):
        while True:
            while receive_queue:
                msg, peer = receive_queue.pop()
                try:
                    if msg['action']:
                        action = msg['action']
                        if action == 'ping':
                            peer.update_receiving_status(msg['state'])
                            logging.debug(f"Received ping from: {peer.get_address()}. Current state: {msg['state']}")
                        elif action == 'ack':
                            message = msg['message']
                            loop_name = message['loop_name']
                            peer.waiting_ack.discard(loop_name)
                            logging.debug(f'new_loop {loop_name} acknowledged')
                            if peer.get_receiving_status().get(loop_name, False):
                                 print('Acking a loop thats been sent!')
                            else:
                                print('Sending first time ', peer.get_receiving_status())
                                WavSlicer.send(peer, loop_name)
                        elif action  == 'new_loop':
                            message = msg['message']
                            loop_name = message['loop_name']
                            total = message['number_of_chunks']
                            if cls.loops.get(loop_name, None) is not None:
                                if len(cls.loops[loop_name]['chunks']) == total:
                                    # FIXME: loop ops like insert and replace will fail here
                                    print('Attempting to replace loop with identical loop')
                                else:
                                    print(f'Replacing {loop_name}')
                                    cls.create_empty_loop(peer, loop_name, total, message)
                            else:
                                print(f'Creating new loop: {loop_name} of size: {total}')
                                cls.loops[loop_name] = {}
                                cls.create_empty_loop(peer, loop_name, total, message)
                            WavSlicer.send_ack(peer, loop_name)
                        elif action == 'request_new_loop':
                            loop_name = msg['message']['loop_name']
                            loop, loop_number = TTTruck._get_loop_by_name(loop_name)
                            WavSlicer.send_new_loop_message(loop)

                        elif action == 'loop_add':
                            message = msg['message']
                            loop_name = message['loop_name']
                            current_chunk = message['current_chunk']
                            if cls.loops.get(loop_name, None) is None:
                                WavSlicer.send_request_new_loop_message(name, peer)
                            else:
                                #TODO: use this to determine if we've received a repeat or replace of loop
                                cls.accept_loop_chunk(peer, loop_name, current_chunk, message['chunk_body'])
                                logging.debug(f'Received chunk {current_chunk} from: {peer.get_address()}. ')
                        elif action == 'loop_modify':
                            message = msg['message']
                            logging.debug(f'Modifying : {message} from: {peer.get_address()}.')
                            # {'action': 'loop_add', 'message': {'loop_name': name, {'param': value},
                            loop_name = message['loop_name']
                            for param, value in message.items():
                                if param == 'loop_name':
                                    continue
                                TTTruck.set_parameter(loop_name, param, value)
                except Exception as e:
                    #logging.warning(f'Unable to receive data {msg} from: {peer.get_address()}', e)
                    print('Incoming ', e)
                    #import pdb;pdb.set_trace()
            time.sleep(PROCESS_INCOMING_PERIOD)


    @classmethod
    def process_loop(cls, loop_name):
        logging.debug(f'Received complete loop {loop_name}')
        #TODO: to pop or not to pop? Storing all wav_bytes is faster but consumes memory
        loop = cls.loops[loop_name]
        TTTruck.add_remote_loop(loop_name, loop)

    @classmethod
    def resend_missing_chunks(cls):
        while True:
            for peer in cls.outputs:
                if peer.is_ready:
                    peer.is_ready = False
                    try:
                        #FIXME Concurrent modification of status
                        status = peer.get_receiving_status()
                        for name, chunks in status.items():
                            if chunks:
                                for chunk in chunks:
                                    loop, loop_number = TTTruck._get_loop_by_name(name)
                                    logging.debug(f'resending {peer.get_address()}, {name}, {chunks}')
                                    WavSlicer.send(peer, loop.name, chunk_number=chunk)
                            peer.clear_receiving_status(name)
                    except Exception as e:
                        print('Resending ', e)
                cls.send_ping(peer)
            time.sleep(RESEND_PERIOD)



    @classmethod
    def exit(cls):
        receive_queue = None
        send_queue = None
        cls.inputs = None
        cls.outputs = None
