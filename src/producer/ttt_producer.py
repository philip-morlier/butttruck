import pika
from pika import BasicProperties
from pika.exceptions import StreamLostError


class TTTruckProducer:
    channel = None
    connection = None
    exchange = 'tttruck'

    @classmethod
    def _create_exchange(cls, name):
        cls.channel.exchange_declare(exchange=name, exchange_type='fanout')

    @classmethod
    def publish_msg(cls, msg, queue=''):
        try:
            if cls.connection is None:
                cls.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
                cls.channel = cls.connection.channel()
                cls._create_exchange(cls.exchange)

            cls.channel.basic_publish(exchange=cls.exchange, routing_key=queue, body=msg,
                                      properties=BasicProperties(content_type='application/json'))

        except Exception as e:
            if e.__class__ is StreamLostError:
                cls.connection = None
                cls.publish_msg(msg)
            print(e)

        @classmethod
        def close(cls):
            cls.connection.close()
            cls.connection = None
