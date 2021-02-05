# msg = {'url': url,
#        'loop_name': name,
#        'parameters': []}

import pika
import json

from pika.exchange_type import ExchangeType

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
main_channel = connection.channel()


main_channel.exchange_declare(exchange='com.micex.sten', exchange_type=ExchangeType.direct)
# update according to consumer also eschange type - read docs - fanout



def publish(msg):
    main_channel.basic_publish(
        exchange='message',
        routing_key='example.txt',
        body=json.dumps(msg),
        properties=pika.BasicProperties(content_type='application/json'))

if __name__ == '__main__':
    publish(some_message)