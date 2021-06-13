import socket
from unittest import TestCase
from src.application import process_incoming, loops, process_loops, resend_missing_chunks
from src.looper.tttruck import TTTruck
from src.udp.peers import PeerClient, Peer
import json

from src.udp.wav_slicer import WavSlicer


class Test(TestCase):

    def test_wav_slice(self):
        saved_loop = '../udp/test1.wav'
        name = 'test1'

        WavSlicer.slice_and_send(name=name, file=saved_loop)

        peer = Peer(('0.0.0.0', 1111), socket.AF_INET, socket.SOCK_DGRAM, False)
        while PeerClient.send_queue:
            x = PeerClient.send_queue.pop()
            PeerClient.receive_queue.append((x[0], peer))

        process_incoming()
        self.assertEqual(1139, len(loops[name]))
        process_loops()
        self.assertEqual(None, loops.get(name, None))
        file = TTTruck.loop_dir + '/' + name + '.wav'
        import os
        self.assertEqual(os.path.getsize(saved_loop), os.path.getsize(file), msg='File received not the same as sent')
        peer.close()

    def test_process_incoming(self):
        peer = Peer(('0.0.0.0', 1111), socket.AF_INET, socket.SOCK_DGRAM, False)
        PeerClient.receive_queue.append((json.dumps({"action": "loop_add",
                                                     "message": {"loop_name": "loop1", "number_of_chunks": 1,
                                                                 "current_chunk": 1,
                                                                 "chunk_body": b'x00'.decode('latin1')}}), peer))
        process_incoming()

        PeerClient.receive_queue.append((json.dumps({"action": "loop_add",
                                                     "message": {"loop_name": "loop2", "number_of_chunks": 5,
                                                                 "current_chunk": 3,
                                                                 "chunk_body": b'x00'.decode('latin1')}}), peer))
        process_incoming()

        self.assertEqual(2, len(loops))
        self.assertEqual([b'x00'], loops['loop1'])
        self.assertEqual([None, None, b'x00', None, None], loops['loop2'])

        process_loops()

        self.assertEqual(1, len(loops))
        self.assertEqual({'loop2': [None, None, b'x00', None, None]}, loops)
