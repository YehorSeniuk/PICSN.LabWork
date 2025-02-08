import socket
import threading
import rsa

users = {}

def process_client(conn, username):
    while True:
        (pub, priv) = rsa.newkeys(128)
        try:
            data = conn.recv(1024).decode('utf-8')
            if not data:
                print(f"[SMTP Server] {username} disconnected.")
                del users[username]
                break

            encrypted_msg = rsa.encrypt(data.encode('utf-8'), pub)
            print(f"[SMTP Server] Received message from {username}: {encrypted_msg}")

            decrypted_msg = rsa.decrypt(encrypted_msg, priv).decode('utf-8')
            for user, connection in users.items():
                send_to_all(decrypted_msg, user)

        except ConnectionResetError:
            print(f"[SMTP Server] Connection with {username} reset.")
            del users[username]
            break

    conn.close()

def send_to_all(msg, sender):
    for user, conn in list(users.items()):
        if user != sender:
            try:
                conn.send(f"{sender}: {msg}".encode('utf-8'))
            except BrokenPipeError:
                print(f"[SMTP Server] Error sending message to {user}. Removing {user} from users.")
                del users[user]

def run_server():
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.bind(('127.0.0.1', 5555))
    srv.listen(2)
    print("[SMTP Server] Listening on port 5555...")

    while True:
        conn, addr = srv.accept()
        username = conn.recv(1024).decode('utf-8')
        users[username] = conn

        print(f"[SMTP Server] Connection established with {username}")

        thread = threading.Thread(target=process_client, args=(conn, username))
        thread.start()

if __name__ == "__main__":
    run_server()

