import random
import threading
import time
from unittest import TestCase

from src.looper.sl_client import SLClient
from src.looper.tttruck import TTTruck
from src.osc.osc_client import OSCClient
from src.osc.osc_server import OSCServer


class TestTTTruck(TestCase):

    def test_loop_index(self):
        OSCServer.start(port=9952 , debug=False)
        t = threading.Thread(target=OSCClient.start(client_name='test'), daemon=True)
        t.start()
        SLClient.ping()
        time.sleep(0.3)
        TTTruck._delete_all_loops()

        self.assertEqual(0, TTTruck.loops)
        self.assertFalse(TTTruck.loop_index)

        # one loop
        TTTruck.loop_add()
        time.sleep(1)
        self.assertEqual(1, TTTruck.loops)
        self.assertTrue(TTTruck.loop_index)
        first_loop = TTTruck.loop_index[0]
        print(first_loop)

        # second loop
        TTTruck.loop_add()
        second_loop = TTTruck.loop_index[1]
        print(second_loop)
        time.sleep(1)
        self.assertEqual(2, TTTruck.loops)

        # third loop
        TTTruck.loop_add()
        time.sleep(1)
        self.assertEqual(3, TTTruck.loops)
        third_loop = TTTruck.loop_index[2]


        TTTruck.select_loop(1)
        time.sleep(1)
        TTTruck.loop_reverse()
        time.sleep(1)
        self.assertEqual(1, TTTruck.changes[second_loop]['reverse'])
        time.sleep(1)
        TTTruck.loop_reverse()
        time.sleep(1)
        self.assertEqual(0, TTTruck.changes[second_loop]['reverse'])
        TTTruck.delete_loop()
        time.sleep(1)
        #print(OSCServer.selected_loop, 's')

        # third loop should now be the second of two loops
        self.assertEqual(2, TTTruck.loops)
        self.assertEqual(third_loop, TTTruck.loop_index[1])

        # delete second loop again and ensure first loop is all that's left
        TTTruck.delete_loop()
        time.sleep(1)
        self.assertEqual(1, TTTruck.loops)
        self.assertEqual(first_loop, TTTruck.loop_index[0])
