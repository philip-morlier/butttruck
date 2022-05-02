import logging
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
    def slice_and_send(name, sync_time, file=None, chunk_number=None, peer=None):
        if file is None:
            try:
                file = WavSlicer.published_loops[name]
            except Exception as e:
                logging.warning(f'Unable to send: {name} from file: {file} because {e}')
                # TODO: inform peer we no longer have file
                return

        try:
            count = 1
            size_in_bytes = os.path.getsize(file)
            number_of_chunks = math.ceil(size_in_bytes / LIMIT)
            logging.debug(f'Sending {name}, file: {file}, chunk: {chunk_number} to {peer}')
            WavSlicer.published_loops[name] = file
            with open(file, 'rb') as f:
                if chunk_number is not None:
                    f.seek(chunk_number * LIMIT)
                    chunk = f.read(LIMIT)
                    WavSlicer.format_and_send_wav_message(chunk, chunk_number, number_of_chunks, name, sync_time, peer=peer)
                else:
                    while f.peek(LIMIT):
                        chunk = f.read(LIMIT)
                        WavSlicer.format_and_send_wav_message(chunk, count, number_of_chunks, name, sync_time)
                        count += 1
        except Exception as e:
            logging.warning(f'Error slicing and sending {name} to {peer.get_address}: {e}')

    @staticmethod
    def format_and_send_wav_message(chunk, count, number_of_chunks, name, sync_time, peer=None):
        import json
        msg = json.dumps({'action': 'loop_add',
                          'message': {'loop_name': name,
                                      'number_of_chunks': number_of_chunks,
                                      'current_chunk': count,
                                      'chunk_body': chunk.decode('latin1')},
                          'sync_time': sync_time})
        if peer is not None:
            logging.debug(f'Resend {name}:{count}to {peer.get_address()}')
            PeerClient.send_msg(peer, msg)
        else:
            logging.debug(f'Sending {name}:{count}')
            PeerClient.send_queue.append(msg)
