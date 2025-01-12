import secrets
import time
import threading
from flask import Flask, request, jsonify
from collections import deque

app = Flask(__name__)

message_queue = deque(maxlen=100)
message_lock = threading.Lock()

class Message:
    def __init__(self, data):
        self.data = data
        self.timestamp = time.time()
        self.id = secrets.token_hex(8)
        
@app.route("/fetch", methods=['GET'])
def fetch_messages():
    last_message_id = request.args.get("last_message_id")
    
    new_messages = []
    with message_lock:
        for message in message_queue:
            if not last_message_id or (last_message_id and message.id > last_message_id):
                new_messages.append({
                    'id': message.id,
                    'data': message.data,
                    'timestamp': message.timestamp
                })
    
    return jsonify({
        'messages': new_messages,
        'server_time': time.time()
    })

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'message_count': len(message_queue),
        'server_time': time.time()
    })

@app.route('/newmessage', methods=['POST'])
def new_message():
    if request.method == 'POST':
        data = request.get_json()
        
        message = Message(data)
        with message_lock:
            message_queue.append(message)
            return "success", 201

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=6920, debug=True)
