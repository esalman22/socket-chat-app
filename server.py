import socket
import threading
import os

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

port = int(os.environ.get("PORT", 50000))
server_socket.bind(('0.0.0.0', port))

server_socket.listen()

print("Server is running...")

clients = {}  # conn -> username


def broadcast(message):
    for client in list(clients):
        try:
            client.send(message)
        except:
            client.close()
            clients.remove(client)


def handle_client(conn, addr):
    try:
        # أول رسالة = username
        username = conn.recv(1024).decode()
        clients[conn] = username

        print(f"{username} joined from {addr}")

        broadcast(f"{username} joined the chat".encode())

        while True:
            data = conn.recv(1024)
            if not data:
                break

            message = f"{username}: {data.decode()}"
            print(message)

            broadcast(message.encode())

    except:
        pass

    finally:
        if conn in clients:
            name = clients[conn]
            del clients[conn]
            broadcast(f"{name} left the chat".encode())

        conn.close()


def accept_connections():
    while True:
        conn, addr = server_socket.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()


accept_connections()
