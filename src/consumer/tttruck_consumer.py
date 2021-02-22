import sys
import traceback

import pika

from threading import Thread
from src.looper.tttruck import TTTruck


class TTTruckConsumer(object):

    def __init__(self, addr='localhost', exchange='tttruck'):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(addr, heartbeat=0))
        self.channel = self.connection.channel()
        result = self.channel.queue_declare(queue='tttruck_queue')
        self.queue_name = result.method.queue
        self.exchange_name = exchange
        self.channel.queue_bind(exchange=exchange, queue=self.queue_name)

    @staticmethod
    def dispatch(ch, method, properties, body):
        try:
            print(f'Received message on channel: {ch}, method: {method}, with body: {body} and properties: {properties}')
            TTTruck.dispatch(body)
        except Exception as e:
            extype, ex, tb = sys.exc_info()
            print(ex, traceback.print_tb(tb))

    def close(self):
        self.connection.close()

    def start(self):
        self.channel.basic_consume(queue=self.queue_name,
                                   auto_ack=True,
                                   on_message_callback=self.dispatch)
        thread = Thread(target=self.channel.start_consuming, daemon=True)
        thread.start()
