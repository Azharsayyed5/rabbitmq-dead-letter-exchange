import uuid
import pika
import sys
sys.path.append('/root/files/python-scripts/')

# Create connection with rabbitMQ using pika client
credentials = pika.PlainCredentials("username", "password")
mq_connection = pika.BlockingConnection(
    pika.ConnectionParameters("localhost", virtual_host="virtual_host", credentials=credentials)
)
mq_channel = mq_connection.channel()

# Define :: normal and dead-letter exchange
xc = 'x-exchange'
xcx = 'x-exchange-delay'
expirty_time = '10000'

# Declare :: two exchange for normal and dead-letter queues each
mq_channel.exchange_declare(exchange=xc, durable=True, exchange_type="x-consistent-hash")
mq_channel.exchange_declare(exchange=xcx, durable=True, exchange_type="x-consistent-hash")

# Define queues to be used in the exchange
# Declare both type of queues
queues = ['queue_1', 'queue_2', 'queue_3']
for queue in queues:
    dead_letter_queue = "delay_" + queue # e.g "delay_queue_1"
    
    mq_channel.queue_declare(
        queue=queue,
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
    # Bind normal queue with normal first exchange
    mq_channel.queue_bind(exchange=xc, queue=queue, routing_key="1")
    # Bind dead letter queue with other exchange
    mq_channel.queue_bind(exchange=xcx, queue=dead_letter_queue, routing_key="1")

# Publish 20K messages to dead letter queue exchange with expiration of 10 seconds
for i in range(20000):
    mq_channel.basic_publish(
        exchange=xcx, routing_key=str(uuid.uuid4()), body='',
        properties=pika.BasicProperties(expiration=expirty_time, delivery_mode=2, priority=10)
    )
