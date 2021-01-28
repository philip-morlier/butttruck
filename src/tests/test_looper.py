import unittest

from src.looper.sl_client import OSCClient, OSCServer


class LooperTest(unittest.TestCase):
    ping = None

    def handler(self, x):
        self.ping = x

    def test_ping(self):
        client = OSCClient(port=1111, client_name='test')
        server = OSCServer(port=1111, debug=True)
        server.register_handler('/test', self.handler)
        client.sends_message('/test', type=',s', args=['hello'])
        self.assertEqual(self.ping, 'hello')


if __name__ == '__main__':
    unittest.main()
