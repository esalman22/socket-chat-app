import socket
import threading
import os

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("0.0.0.0", 18729))
server_socket.listen()

print("Server running...")

clients = {}

END_MARK = b"<END>"

#================ BROADCAST =================#

def broadcast(data, sender=None):
    for c in list(clients):
        if c != sender:
            try:
                c.send(data)
            except:
                c.close()
                if c in clients:
                    del clients[c]

#================ HANDLE CLIENT =================#

def handle_client(conn, addr):

    try:
        username = conn.recv(1024).decode()
        clients[conn] = username

        print(username, "connected")

        while True:

            header = conn.recv(1024)

            if not header:
                break

            #================ IMAGE / FILE =================#

            if header.startswith(b"IMAGE:") or header.startswith(b"FILE:") or header.startswith(b"VIDEO:"):

                broadcast(header)  # ابعت النوع لكل الناس

                file_data = b""

                while True:
                    chunk = conn.recv(4096)

                    if END_MARK in chunk:
                        file_data += chunk.replace(END_MARK, b"")
                        break

                    file_data += chunk

                # ابعت الملف لكل الناس
                broadcast(file_data)

                # نهاية الملف
                broadcast(END_MARK)

            #================ TEXT =================#

            else:

                try:
                    msg = f"{username}: {header.decode()}"
                    broadcast(msg.encode(), conn)

                except:
                    pass

    except:
        pass

    finally:
        conn.close()
        if conn in clients:
            del clients[conn]

#================ ACCEPT =================#

while True:
    conn, addr = server_socket.accept()
    threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
