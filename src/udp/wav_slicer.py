import sys
import os
import math
import time

from src.udp.peers import PeerClient

LIMIT = 5000


class WavSlicer:
    published_loops = {}

    @staticmethod
    def slice_and_send(name, file=None, chunk_number=None, peer=None):
        wait_time = 100
        count = 0
        while not os.path.exists(file):
            time.sleep(0.1)
            count += 1
            if count > wait_time:
                raise Exception(f'File {file} doesnt exist')

        if file is None:
            try:
                file = WavSlicer.published_loops[name]
            except Exception as e:
                print(f'Unable to send: {name} from file: {file} because {e}')
        try:
            count = 1
            size_in_bytes = os.path.getsize(file)
            number_of_chunks = math.ceil(size_in_bytes / LIMIT)
            WavSlicer.published_loops[name] = file
            with open(file, 'rb') as f:
                if chunk_number is not None:
                    f.seek(chunk_number * LIMIT)
                    chunk = f.read(LIMIT)
                    WavSlicer.format_and_send_wav_message(chunk, chunk_number, number_of_chunks, name, peer=peer)
                else:
                    while f.peek(LIMIT):
                        chunk = f.read(LIMIT)
                        WavSlicer.format_and_send_wav_message(chunk, count, number_of_chunks, name)
                        count += 1
        except Exception as e:
            print(e)

    @staticmethod
    def format_and_send_wav_message(chunk, count, number_of_chunks, name, peer=None):
        import json
        msg = {'action': 'loop_add',
               'message': {'loop_name': name,
                           'number_of_chunks': number_of_chunks,
                           'current_chunk': count,
                           'chunk_body': chunk.decode('latin1')}
               }
        if peer:
            PeerClient.send_msg(peer, json.dumps(msg))
        else:
            PeerClient.send_queue.append((json.dumps(msg), peer))