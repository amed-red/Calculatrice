import pika
import redis
import json
import os
import time

REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'localhost')

# Connect to Redis
r = redis.Redis(host=REDIS_HOST, port=6379, db=0, decode_responses=True)

def callback(ch, method, properties, body):
    data = json.loads(body)
    op_id = data['id']
    op = data['op']
    a = float(data['a'])
    b = float(data['b'])
    
    result = None
    try:
        if op == 'add':
            result = a + b
        elif op == 'sub':
            result = a - b
        elif op == 'mul':
            result = a * b
        elif op == 'div':
            result = a / b if b != 0 else "Error: Division by zero"
        else:
            result = "Error: Unknown operator"
    except Exception as e:
        result = f"Error: {str(e)}"
    
    # Store result in Redis
    r.set(op_id, str(result))
    print(f"Processed {op_id}: {a} {op} {b} = {result}")
    ch.basic_ack(delivery_tag=method.delivery_tag)

def main():
    while True:
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
            channel = connection.channel()
            channel.queue_declare(queue='calculations')
            channel.basic_consume(queue='calculations', on_message_callback=callback)
            print('Consumer waiting for messages...')
            channel.start_consuming()
        except Exception as e:
            print(f"Connection failed, retrying in 5s... ({e})")
            time.sleep(5)

if __name__ == '__main__':
    main()
