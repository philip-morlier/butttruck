import json
from unittest import TestCase

from src.application import process_incoming
from src.udp.peers import PeerClient


class TestPeerClient(TestCase):
    #complete this test, two names two loops, status should show two users and two items. Will
    #always fail, needs code changes.
    def test_update_multiple_loop_statuses(self):
        self.fail("wRite me philllip")

    def test_update_status(self):
        PeerClient.add_peer(('0.0.0.0', 1111))
        PeerClient.add_peer(('0.0.0.0', 2222))
        peer = PeerClient.inputs[0]
        peer2 = PeerClient.inputs[1]

        self.assertEqual({}, peer2.receiving_status)
        msg = json.dumps({"action": "loop_add",
                          "message": {"loop_name": "loop2", "number_of_chunks": 3,
                                      "current_chunk": 2,
                                      "chunk_body": b'x00'.decode('latin1')}})
        peer.sendto(msg.encode(), peer2.address)
        PeerClient.receive_data(peer2)
#        process_incoming()

        self.assertEqual({'loop2': [1, 3]}, peer2.get_receiving_status())
        peer2.sendto(json.dumps({"action": "ping", "state": peer2.get_receiving_status()}).encode(), peer.address)
        PeerClient.receive_data(peer)
        process_incoming()

        msg = json.dumps({"action": "loop_add",
                          "message": {"loop_name": "loop2", "number_of_chunks": 3,
                                      "current_chunk": 1,
                                      "chunk_body": b'x00'.decode('latin1')}})
        peer.sendto(msg.encode(), peer2.address)
        PeerClient.receive_data(peer2)
        self.assertEqual({'loop2': [3]}, peer2.get_receiving_status())

        msg = json.dumps({"action": "loop_add",
                          "message": {"loop_name": "loop2", "number_of_chunks": 3,
                                      "current_chunk": 3,
                                      "chunk_body": b'x00'.decode('latin1')}})
        peer.sendto(msg.encode(), peer2.address)

        PeerClient.receive_data(peer2)
        self.assertEqual({}, peer2.get_receiving_status())

        peer.close()
        peer2.close()
