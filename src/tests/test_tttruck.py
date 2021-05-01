import random
import threading
import time
from unittest import TestCase

from osc4py3 import oscbuildparse
from osc4py3.as__common import osc_udp_client, osc_process, osc_send

from src.looper.sl_client import SLClient
from src.looper.tttruck import TTTruck
from src.osc.osc_client import OSCClient
from src.osc.osc_server import OSCServer


class TestTTTruck(TestCase):

    def test_loop_index(self):
        t = threading.Thread(target=OSCClient.start(client_name='test'), daemon=True)
        t.start()
        OSCServer.start(debug=True)
        SLClient.register_global_auto_update('selected_loop_num', OSCServer.return_url, '/loops', interval=1)

        SLClient.ping()
        time.sleep(1)
        for i in range(OSCServer.loops):
            SLClient.loop_del(-1)

        # no loops, empty index
        self.assertEqual(0, TTTruck.loops)
        self.assertFalse(TTTruck.loop_index)

        # one loop
        TTTruck.new_loop()
        self.assertEqual(1, TTTruck.loops)
        self.assertTrue(TTTruck.loop_index)
        first_loop = TTTruck.loop_index[1]

        # second loop
        TTTruck.new_loop()
        self.assertEqual(2, TTTruck.loops)

        # third loop
        TTTruck.new_loop()
        self.assertEqual(3, TTTruck.loops)
        third_loop = TTTruck.loop_index[3]

        # Select second loop and delete it
        SLClient.set_selected_loop_num(1)
        TTTruck.delete_loop()

        # third loop should now be the second of two loops
        self.assertEqual(2, TTTruck.loops)
        self.assertEqual(third_loop, TTTruck.loop_index[2])

        # delete second loop again and ensure first loop is all that's left
        TTTruck.delete_loop()
        self.assertEqual(1, TTTruck.loops)
        self.assertEqual(first_loop, TTTruck.loop_index[1])



