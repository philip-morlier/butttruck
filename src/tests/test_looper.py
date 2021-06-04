import time
import unittest

from src.osc.osc_client import OSCClient
from src.osc.osc_server import OSCServer


class LooperTest(unittest.TestCase):
    ping = None

    def handler(self, x):
        self.ping = x

    def test_ping(self):
        OSCServer.start(debug=True, port=8852)
        OSCClient.start(port=8852, client_name='test')
        OSCServer.register_handler('/test', self.handler)
        OSCClient.send_message('/test', type=',s', args=['hello'])
        time.sleep(0.5)
        self.assertEqual(self.ping, 'hello')


if __name__ == '__main__':
    unittest.main()
