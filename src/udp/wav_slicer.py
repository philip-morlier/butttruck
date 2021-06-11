import math
import os

from src.udp.peers import PeerClient

LIMIT = 1024


class WavSlicer:
    published_loops = {}

    @staticmethod
    def send_changes(changes, name=None, peer=None):
        import json
        if name is None:
            for k, v in changes.items():
                msg = {'action': 'loop_modify', 'message': {k: v}}
                PeerClient.send_queue.append((json.dumps(msg), peer))
        else:
            msg = {'action': 'loop_modify', 'message': {name: changes}}
            PeerClient.send_queue.append((json.dumps(msg), peer))

    @staticmethod
    def slice_and_send(name, file=None, chunk_number=None, peer=None):
        if file is None:
            try:
                file = WavSlicer.published_loops[name]
            except Exception as e:
                print(f'Unable to send: {name} from file: {file} because {e}')
        try:
            count = 1
            size_in_bytes = os.path.getsize(file)
            number_of_chunks = math.ceil(size_in_bytes / LIMIT)
            print(number_of_chunks)
            WavSlicer.published_loops[name] = file
            with open(file, 'rb') as f:
                if chunk_number is not None:
                    print('resending chunk ', chunk_number)
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
        msg = json.dumps({'action': 'loop_add',
                          'message': {'loop_name': name,
                                      'number_of_chunks': number_of_chunks,
                                      'current_chunk': count,
                                      'chunk_body': chunk.decode('latin1')}})
        if peer:
            PeerClient.send_msg(peer, msg)
        else:
            PeerClient.send_queue.append((msg, peer))
