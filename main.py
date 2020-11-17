import uuid
import pika
import sys
sys.path.append('/root/files/python-scripts/')
credentials = pika.PlainCredentials("username", "password")
mq_connection = pika.BlockingConnection(
    pika.ConnectionParameters("localhost", virtual_host="virtual_host", credentials=credentials)
)
mq_channel = mq_connection.channel()

xc = 'x-exchange'
xcx = 'x-exchange-delay'

mq_channel.exchange_declare(exchange=xc, durable=True, exchange_type="x-consistent-hash")
mq_channel.exchange_declare(exchange=xcx, durable=True, exchange_type="x-consistent-hash")
queues = ['queue_1', 'queue_2', 'queue_3']
for queue in queues:
    parent_queue = queue
    dead_letter_queue = "delay_" + queue
    mq_channel.queue_declare(
        queue=parent_queue,
        durable=True,
        arguments={'x-max-priority': 10}
    )
    mq_channel.queue_declare(
        queue=dead_letter_queue,
        durable=True,
        arguments={
            'x-dead-letter-exchange': xc, 'x-max-priority': 10
        }
    )
    mq_channel.queue_bind(exchange=xc, queue=parent_queue, routing_key="1")
    mq_channel.queue_bind(exchange=xcx, queue=dead_letter_queue, routing_key="1")
for i in range(20000):
    mq_channel.basic_publish(
        exchange=xcx, routing_key=str(uuid.uuid4()), body='',
        properties=pika.BasicProperties(expiration=str(10000), delivery_mode=2, priority=10)
    )
