from flask import Flask, request, jsonify
import redis
import pika
import json
import uuid
import os

app = Flask(__name__)

# Config from environment variables
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'localhost')

# Connect to Redis
r = redis.Redis(host=REDIS_HOST, port=6379, db=0, decode_responses=True)

def get_rabbitmq_channel():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue='calculations')
    return connection, channel

def push_calculation(op, a, b):
    op_id = str(uuid.uuid4())
    payload = {"id": op_id, "op": op, "a": a, "b": b}
    r.set(op_id, "PENDING")
    conn, ch = get_rabbitmq_channel()
    ch.basic_publish(exchange='', routing_key='calculations', body=json.dumps(payload))
    conn.close()
    return op_id

@app.route('/api/addition', methods=['POST'])
@app.route('/api/soustraction', methods=['POST'])
@app.route('/api/multiplication', methods=['POST'])
@app.route('/api/division', methods=['POST'])
def handle_calc():
    # Extract operator from path
    op_map = {
        'addition': 'add',
        'soustraction': 'sub',
        'multiplication': 'mul',
        'division': 'div'
    }
    op_key = request.path.split('/')[-1]
    op = op_map[op_key]
    
    data = request.json
    # Handle both JSON and form data if needed, but sticking to JSON for simplicity
    if not data or 'a' not in data or 'b' not in data:
        return jsonify({"error": "Missing parameters a or b"}), 400
    
    try:
        op_id = push_calculation(op, data['a'], data['b'])
        return jsonify({"id": op_id}), 202
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/result/<op_id>', methods=['GET'])
def get_result(op_id):
    result = r.get(op_id)
    if result is None:
        return jsonify({"error": "Not found"}), 404
    if result == "PENDING":
        return jsonify({"status": "PENDING"}), 200
    return jsonify({"id": op_id, "result": result}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
