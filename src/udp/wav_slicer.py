import logging
import math
import os
import json
import time

from src.udp.messages import send_queue, receive_queue
from src.udp.peer import Peer

LIMIT = 1024

class WavSlicer:
    published_loops = {}

    @staticmethod
    def send_changes(changes, name=None, peer=None):
        if name is None:
            for k, v in changes.items():
                msg = {'action': 'loop_modify', 'message': {k: v}}
                send_queue.append(msg)
        else:
            msg = {'action': 'loop_modify', 'message': {name: changes}}
            send_queue.append(msg)

    @staticmethod
    def slice(loop, chunk_number=None, peer=None):
        if loop is None:
            logging.warning(f'Unable to slice loop')
            # TODO: inform peer we no longer have file
            return

        try:
            #FIXME
            WavSlicer.published_loops[loop.name] = []
            with open(loop.wav_file, 'rb') as f:
                while f.peek(LIMIT):
                    chunk = f.read(LIMIT)
                    WavSlicer.published_loops[loop.name].append(chunk)
        except Exception as e:
            logging.warning(f'Error slicing and sending {loop.name}: ', e)

    @staticmethod
    def send_ack(peer, loop_name):
        msg = json.dumps({'action': 'ack',
                          'message':  {'loop_name': loop_name}})
        peer.sendto(msg.encode(), peer.get_address())

    @staticmethod
    def send_new_loop_message(loop, peer=None):
        #TODO: only calculate the number_of_chunks if we havent done so for this loop
        size_in_bytes = os.path.getsize(loop.wav_file)
        number_of_chunks = math.ceil(size_in_bytes / LIMIT)

        msg = {'action': 'new_loop',
               'message':  {'loop_name': loop.name,
                            'number_of_chunks': number_of_chunks,
                            'sync_time': loop.sync_time}}
        if peer is not None:
            peer.sendto(json.dumps(msg).encode(), peer.get_address())
        else:
            send_queue.append(msg)
            logging.debug(f'Sending new loop {loop.name}, of size: {number_of_chunks}')
        WavSlicer.slice(loop)

    @staticmethod
    def send_request_new_loop_message(name, peer):
        msg = json.dumps({'action': 'request_new_loop',
                          'message': {'loop_name': name}})
        logging.debug(f'Request new_loop info from {peer.get_address()} for {name}')
        peer.sendto(msg.encode(), peer.get_address())


    @staticmethod
    def format_and_send_wav_message(peer, name, chunk_number, chunk=None):
        if chunk is None:
            chunk = WavSlicer.published_loops[name][chunk_number - 1]
        msg = json.dumps({'action': 'loop_add',
                          'message': {'loop_name': name,
                                      'current_chunk': chunk_number,
                                      'chunk_body': chunk.decode('latin1')}})
        peer.sendto(msg.encode(), peer.get_address())

    @staticmethod
    def send(peer, loop_name, chunk_number=None):
        if chunk_number is not None:
            WavSlicer.format_and_send_wav_message(peer, loop_name, chunk_number)
        else:
            for number, chunk in enumerate(WavSlicer.published_loops[loop_name]):
                WavSlicer.format_and_send_wav_message(peer, loop_name, number, chunk)
                time.sleep(0.01)
