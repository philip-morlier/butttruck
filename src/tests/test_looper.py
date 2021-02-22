import time
import unittest

from src.looper.sl_client import OSCClient, OSCServer


class LooperTest(unittest.TestCase):
    ping = None

    def handler(self, x):
        self.ping = x

    def test_ping(self):
        OSCClient.start(port=1111, client_name='test')
        OSCServer.start(port=1111, debug=True)
        OSCServer.register_handler('/test', self.handler)
        OSCClient.send_message('/test', type=',s', args=['hello'])
        time.sleep(0.5)
        self.assertEqual(self.ping, 'hello')


if __name__ == '__main__':
    unittest.main()
