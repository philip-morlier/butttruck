import sys
import os
import math
from src.udp.Peers import PeerClient

LIMIT = 5000


class WavSlicer:

    @staticmethod
    def slice_and_send(file, name, chunk_number=None):
        try:
            count = 1
            size_in_bytes = os.path.getsize(file)
            number_of_chunks = math.ceil(size_in_bytes / LIMIT)
            with open(file, 'rb') as f:
                if chunk_number is not None:
                    f.seek(chunk_number * LIMIT)
                    chunk = f.read(LIMIT)
                    WavSlicer.format_and_send_wav_message(chunk, chunk_number, number_of_chunks, name)
                else:
                    while f.peek(LIMIT):
                        chunk = f.read(LIMIT)
                        WavSlicer.format_and_send_wav_message(chunk, count, number_of_chunks, name)
                        count += 1
            print('did it')
        except Exception as e:
            print(e)
    @staticmethod
    def format_and_send_wav_message(chunk, count, number_of_chunks, name):
        import json
        msg = {'action': 'loop_add',
               'message': {'loop_name': name,
                           'number_of_chunks': number_of_chunks,
                           'current_chunk': count,
                           'chunk_body': chunk.decode('latin1')}
               }
        PeerClient.send_queue.append(json.dumps(msg))
