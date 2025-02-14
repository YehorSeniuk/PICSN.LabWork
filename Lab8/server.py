from flask import Flask, request
from flask_socketio import SocketIO, emit
import json

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

clients = {}

@socketio.on('connect')
def handle_connect():
    emit('message', {'data': 'Connected to server'})

@socketio.on('register')
def handle_register(data):
    username = data.get("username")
    if username:
        clients[username] = request.sid
        emit('message', {'data': f'{username} зареєстрований'}, broadcast=True)

@socketio.on('send_file')
def handle_send_file(data):
    sender = data['sender']
    receiver = data['receiver']
    filename = data['filename']
    file_content = data['file_content']
    signature = data['signature']

    if receiver in clients:
        emit('receive_file', {
            'sender': sender,
            'filename': filename,
            'file_content': file_content,
            'signature': signature
        }, room=clients[receiver])
    else:
        emit('message', {'data': f'Користувач {receiver} не в мережі'})

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
