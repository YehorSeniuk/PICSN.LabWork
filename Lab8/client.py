import socketio
import json
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization, hashes
from base64 import b64encode, b64decode
import os

sio = socketio.Client()

username = input("Введіть ім'я користувача: ")

private_key_path = f"{username}_private.pem"
public_key_path = f"{username}_public.pem"

# Перевіряємо, чи існують ключі
if os.path.exists(private_key_path) and os.path.exists(public_key_path):
    print("🔑 Завантаження існуючих ключів...")
    
    with open(private_key_path, "rb") as f:
        private_key = serialization.load_pem_private_key(f.read(), password=None)

    with open(public_key_path, "rb") as f:
        public_key = serialization.load_pem_public_key(f.read())
else:
    print("🔑 Генерація нової пари ключів...")
    
    private_key = ec.generate_private_key(ec.SECP256R1())
    public_key = private_key.public_key()

    with open(private_key_path, "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ))

    with open(public_key_path, "wb") as f:
        f.write(public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ))

@sio.on('connect')
def on_connect():
    print("✅ Підключено до сервера")
    sio.emit('register', {"username": username})

@sio.on('message')
def on_message(data):
    print(data['data'])

@sio.on('receive_file')
def on_receive_file(data):
    sender = data['sender']
    filename = data['filename']
    file_content = b64decode(data['file_content'])
    signature = b64decode(data['signature'])

    with open(f"received_{filename}", "wb") as f:
        f.write(file_content)

    print(f"📥 Отримано файл {filename} від {sender}")

    # Перевірка підпису
    sender_public_key_path = f"{sender}_public.pem"
    if not os.path.exists(sender_public_key_path):
        print(f"⚠️ Публічний ключ {sender} відсутній. Перевірка неможлива.")
        return

    with open(sender_public_key_path, "rb") as f:
        sender_public_key = serialization.load_pem_public_key(f.read())

    try:
        sender_public_key.verify(signature, file_content, ec.ECDSA(hashes.SHA256()))
        print("✅ Цифровий підпис дійсний!")
    except:
        print("❌ ПОМИЛКА! Невірний цифровий підпис!")

def send_file(receiver, filename):
    if not os.path.exists(filename):
        print("❌ Файл не знайдено!")
        return

    with open(filename, "rb") as f:
        file_content = f.read()

    signature = private_key.sign(file_content, ec.ECDSA(hashes.SHA256()))

    sio.emit('send_file', {
        'sender': username,
        'receiver': receiver,
        'filename': filename,
        'file_content': b64encode(file_content).decode(),
        'signature': b64encode(signature).decode()
    })

sio.connect('http://localhost:5000')

while True:
    cmd = input("Команда (send [користувач] [файл] або exit): ")
    if cmd == "exit":
        break
    elif cmd.startswith("send "):
        _, receiver, filename = cmd.split()
        send_file(receiver, filename)

