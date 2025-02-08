import socket
import threading
import rsa

def listen_for_messages(conn):
    while True:
        try:
            data = conn.recv(1024).decode('utf-8')
            if not data:
                print("Server closed the connection.")
                break
            print(f"\nReceived message: {data}")
        except ConnectionResetError:
            print("Server closed the connection.")
            break

def start_client():
    username = input("Enter your name: ")
    client_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_conn.connect(('127.0.0.1', 5555))
    client_conn.send(username.encode('utf-8'))

    listener = threading.Thread(target=listen_for_messages, args=(client_conn,))
    listener.start()
    listener.join()

if __name__ == "__main__":
    start_client()

