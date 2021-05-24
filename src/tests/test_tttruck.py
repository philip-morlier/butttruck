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
        t = threading.Thread(target=OSCClient.start(client_name='test'), daemon=True)
        t.start()
        OSCServer.start(debug=True)
        SLClient.register_global_auto_update('selected_loop_num', OSCServer.return_url, '/loops', interval=1)

        SLClient.register_auto_update('reverse', OSCServer.return_url, '/loops', interval=1, loop_number=1)

        SLClient.ping()
        time.sleep(0.3)
        for i in range(OSCServer.loops):
            SLClient.loop_del(0)
            time.sleep(.5)
        # no loops, empty index
        self.assertEqual(0, TTTruck.loops)
        self.assertFalse(TTTruck.loop_index)

        # one loop
        TTTruck.new_loop()
        time.sleep(0.3)
        self.assertEqual(1, TTTruck.loops)
        self.assertTrue(TTTruck.loop_index)
        first_loop = TTTruck.loop_index[1]
        print(first_loop)

        # second loop
        TTTruck.new_loop()
        second_loop = TTTruck.loop_index[2]
        print(second_loop)
        time.sleep(0.3)
        self.assertEqual(2, TTTruck.loops)

        # third loop
        TTTruck.new_loop()
        time.sleep(0.3)
        self.assertEqual(3, TTTruck.loops)
        third_loop = TTTruck.loop_index[3]

        # Select second loop and delete it

        SLClient.set_selected_loop_num(1)
        time.sleep(0.3)
        TTTruck.loop_reverse()
        time.sleep(0.3)
        self.assertEqual(1, TTTruck.changes[second_loop]['reverse'])
        time.sleep(0.3)
        TTTruck.loop_reverse()
        time.sleep(0.3)
        self.assertEqual(0, TTTruck.changes[second_loop]['reverse'])
        TTTruck.delete_loop()
        time.sleep(0.3)
        print(OSCServer.selected_loop, 's')

        # third loop should now be the second of two loops
        self.assertEqual(2, TTTruck.loops)
        self.assertEqual(third_loop, TTTruck.loop_index[2])

        # delete second loop again and ensure first loop is all that's left
        TTTruck.delete_loop()
        time.sleep(0.3)
        self.assertEqual(1, TTTruck.loops)
        self.assertEqual(first_loop, TTTruck.loop_index[1])



