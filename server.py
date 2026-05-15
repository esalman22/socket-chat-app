import socket
import threading
import os

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

port = int(os.environ.get("PORT", 50000))

server_socket.bind(('0.0.0.0', port))
server_socket.listen()

print("Server is running...")

clients = {}

END_MARK = b"<END>"

#================ BROADCAST =================#

def broadcast(message, sender=None):

    for client in list(clients):

        if client != sender:
            try:
                client.send(message)
            except:
                client.close()

                if client in clients:
                    del clients[client]

#================ HANDLE CLIENT =================#

def handle_client(conn, addr):

    try:

        username = conn.recv(1024).decode()
        clients[conn] = username

        print(f"{username} joined from {addr}")

        broadcast(f"{username} joined the chat".encode())

        while True:

            data = conn.recv(1024)

            if not data:
                break

            #================ FILES =================#

            if data.startswith(b"IMAGE:") or \
               data.startswith(b"VIDEO:") or \
               data.startswith(b"FILE:"):

                header = data.decode()

                print("Receiving:", header)

                file_data = b""

                while True:

                    chunk = conn.recv(4096)

                    if END_MARK in chunk:
                        file_data += chunk.replace(END_MARK, b"")
                        break

                    file_data += chunk

                print("File received size:", len(file_data))

                # broadcast file header فقط
                broadcast(f"{username} sent {header}".encode(), conn)

            #================ TEXT =================#

            else:

                try:
                    message = f"{username}: {data.decode()}"
                    print(message)

                    broadcast(message.encode(), conn)

                except:
                    print("Decode error")

    except Exception as e:
        print("ERROR:", e)

    finally:

        if conn in clients:

            name = clients[conn]
            del clients[conn]

            broadcast(f"{name} left the chat".encode())

        conn.close()

#================ ACCEPT =================#

def accept_connections():

    while True:

        conn, addr = server_socket.accept()

        thread = threading.Thread(
            target=handle_client,
            args=(conn, addr)
        )

        thread.daemon = True
        thread.start()

accept_connections()
