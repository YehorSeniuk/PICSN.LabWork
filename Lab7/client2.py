import socket
import threading
from docx import Document

def send_data(conn):
    while True:
        filepath = input("Enter message: ")
        content = ""

        if filepath.endswith(".txt"):
            try:
                with open(filepath, encoding='utf-8') as file:
                    content = file.read()
            except FileNotFoundError:
                print("File not found. Please enter a valid path.")
                continue

        elif filepath.endswith(".docx"):
            try:
                doc = Document(filepath)
                content = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            except Exception as e:
                print(f"Error reading DOCX file: {e}")
                continue

        else:
            content = filepath

        conn.send(content.encode('utf-8'))

def start_client():
    username = input("Enter your name: ")
    client_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_conn.connect(('127.0.0.1', 5555))
    client_conn.send(username.encode('utf-8'))

    sender = threading.Thread(target=send_data, args=(client_conn,))
    sender.start()
    sender.join()

if __name__ == "__main__":
    start_client()

