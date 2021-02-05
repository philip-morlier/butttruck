import pika

from pika.adapters.asyncio_connection import AsyncioConnection
from pika.exchange_type import ExchangeType

from src.looper.sl_client import SLClient

"""https://github.com/pika/pika/blob/master/examples/asyncio_consumer_example.py"""

class TTTruckConsumer:

    EXCHANGE = 'message'
    EXCHANGE_TYPE = ExchangeType.topic
    QUEUE = 'text'
    ROUTING_KEY = 'example.text'

    def __init__(self, amqp_url):

        self.sl_client = SLClient()
        self._connection = None
        self._channel = None
        self._consumer_tag = None
        self._url = amqp_url

    def connect(self):
        return AsyncioConnection(
            parameters=pika.URLParameters(self._url))


    def close(self):
        if self._connection is not None:
            self._connection.close()

    def open_channel(self, channel):
        self._connection.channel()
        self._channel = channel
        self.setup_exchange(self.EXCHANGE)
        self.setup_queue(self.QUEUE)

    def setup_exchange(self, exchange):
        self._channel.exchange_declare(
            exchange=exchange,
            exchange_type=self.EXCHANGE_TYPE)

    def setup_queue(self, queue):
        self._channel.queue_declare(queue=queue)

    def start_consuming(self):
        self._consumer_tag = self._channel.basic_consume(
            self.QUEUE, self.on_message)

    def on_message(self, body):
        # parse the body for method calls to osc client, need to parse the url for the loop,
        # download from the url the loop, use client to tell sl to load the loop
        contents = self.parse_message()
        path = self.download_loop(contents.get('url'))
        self.sl_client.load_loop(-3, path)

        pass

    def parse_message(self, body):
        # return list of possible methods, parameters, etc.
        pass

    def download_loop(self, url):
        # return the path to the file, parsed from the message body
        pass

    def run(self):
        self._connection = self.connect()
        self._connection.ioloop.run_forever()

if __name__ == '__main__':
    ttt = TTTruckConsumer('amqp://guest:guest@localhost:5672/%2F')
    ttt.run()
