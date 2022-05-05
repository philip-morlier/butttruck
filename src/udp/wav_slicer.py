import logging
import math
import os

from src.udp.messages import send_queue, receive_queue
from src.udp.peer import Peer

LIMIT = 1024


class WavSlicer:
    published_loops = {}

    @staticmethod
    def send_changes(changes, name=None, peer=None):
        import json
        if name is None:
            for k, v in changes.items():
                msg = {'action': 'loop_modify', 'message': {k: v}}
                send_queue.append((json.dumps(msg), peer))
        else:
            msg = {'action': 'loop_modify', 'message': {name: changes}}
            send_queue.append((json.dumps(msg), peer))

    @staticmethod
    def slice_and_send(loop, chunk_number=None, peer=None):
        if loop is None:
            logging.warning(f'Unable to send loop')
            # TODO: inform peer we no longer have file
            return

        try:
            count = 1
            size_in_bytes = os.path.getsize(loop.wav_file)
            number_of_chunks = math.ceil(size_in_bytes / LIMIT)
            logging.debug(f'Sending {loop.name}, file: {loop.wav_file}, chunk: {chunk_number} to {peer}')
            WavSlicer.published_loops[loop.name] = loop.wav_file
            with open(loop.wav_file, 'rb') as f:
                if chunk_number is not None:
                    f.seek(chunk_number * LIMIT)
                    chunk = f.read(LIMIT)
                    WavSlicer.format_and_send_wav_message(chunk, chunk_number, number_of_chunks, loop.name, loop.sync_time, peer=peer)
                else:
                    while f.peek(LIMIT):
                        chunk = f.read(LIMIT)
                        WavSlicer.format_and_send_wav_message(chunk, count, number_of_chunks, loop.name, loop.sync_time)
                        count += 1
        except Exception as e:
            logging.warning(f'Error slicing and sending {loop.name}: ', e)

    @staticmethod
    def send_new_loop_message(loop, number_of_chunks, sync_time):
        #TODO: verify receipt
        # maybe in loop_add in PeerClient?
        import json
        msg = json.dumps({'action': 'new_loop',
                          'message':  {'loop_name': name,
                                      'number_of_chunks': number_of_chunks,
                                      'sync_time': sync_time}})
        send_queue.append(msg)
        WavSlicer.slice_and_send(loop)

    @staticmethod
    def request_new_loop_message(name, peer):
        import json
        msg = json.dumps({'action': 'request_new_loop',
                          'message': {'loop_name': name}})
        logging.debug(f'Request new_loop info from {peer.get_address()} for {name}')
        peer.sendto(msg.encode(), peer.get_address())


    @staticmethod
    def format_and_send_wav_message(chunk, count, number_of_chunks, name, sync_time, peer=None):
        import json
        msg = json.dumps({'action': 'loop_add',
                          'message': {'loop_name': name,
                                      'number_of_chunks': number_of_chunks,
                                      'current_chunk': count,
                                      'chunk_body': chunk.decode('latin1'),
                                      'sync_time': sync_time}})
        if peer is not None:
            logging.debug(f'Resend {name}:{count}to {peer.get_address()}')
            peer.sendto(msg.encode(), peer.get_address())
        else:
            logging.debug(f'Sending {name}:{count}')
            send_queue.append(msg)
