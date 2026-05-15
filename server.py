```python
import socket
import threading
import os
import time

# ================= SERVER ================= #

server_socket = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
)

port = int(
    os.environ.get("PORT", 50000)
)

server_socket.bind(
    ("0.0.0.0", port)
)

server_socket.listen()

print(f"Server running on {port}...")

clients = {}

END_MARK = b"<END>"

HEADER_END = b"<HEADER_END>"

# ================= BROADCAST ================= #

def broadcast(message, sender=None):

    for client in list(clients):

        if client != sender:

            try:

                client.send(message)

            except:

                client.close()

                if client in clients:
                    del clients[client]

# ================= HANDLE CLIENT ================= #

def handle_client(conn, addr):

    try:

        username = conn.recv(
            1024
        ).decode()

        clients[conn] = username

        print(
            f"{username} joined from {addr}"
        )

        broadcast(
            f"{username} joined the chat".encode()
        )

        while True:

            # ================= RECEIVE HEADER ================= #

            data = b""

            while HEADER_END not in data:

                chunk = conn.recv(1024)

                if not chunk:
                    return

                data += chunk

                # NORMAL TEXT MESSAGE
                if (
                    b"IMAGE:" not in data and
                    b"VIDEO:" not in data and
                    b"FILE:" not in data
                ):

                    try:

                        message = (
                            f"{username}: "
                            f"{data.decode()}"
                        )

                        print(message)

                        broadcast(
                            message.encode(),
                            conn
                        )

                    except:

                        print("Decode Error")

                    data = b""
                    break

            if not data:
                continue

            # ================= SPLIT HEADER ================= #

            header_data, remaining = data.split(
                HEADER_END,
                1
            )

            header = header_data.decode()

            print("Receiving:", header)

            # ================= RECEIVE FILE ================= #

            file_data = remaining

            while True:

                chunk = conn.recv(4096)

                if END_MARK in chunk:

                    file_data += chunk.replace(
                        END_MARK,
                        b""
                    )

                    break

                file_data += chunk

            # ================= SAVE FILE ================= #

            try:

                save_folder = "received_files"

                os.makedirs(
                    save_folder,
                    exist_ok=True
                )

                file_name = header.split(":")[1]

                timestamp = str(
                    int(time.time())
                )

                name = os.path.splitext(
                    file_name
                )[0]

                ext = os.path.splitext(
                    file_name
                )[1]

                new_name = (
                    f"{name}_{timestamp}{ext}"
                )

                save_path = os.path.join(
                    save_folder,
                    new_name
                )

                with open(
                    save_path,
                    "wb"
                ) as f:

                    f.write(file_data)

                print(
                    "Saved:",
                    save_path
                )

                broadcast(
                    f"{username} sent {new_name}".encode(),
                    conn
                )

            except Exception as e:

                print(
                    "Save Error:",
                    e
                )

    except Exception as e:

        print(
            "Client Error:",
            e
        )

    finally:

        if conn in clients:

            name = clients[conn]

            del clients[conn]

            broadcast(
                f"{name} left the chat".encode()
            )

        conn.close()

# ================= ACCEPT ================= #

def accept_connections():

    while True:

        conn, addr = server_socket.accept()

        thread = threading.Thread(
            target=handle_client,
            args=(conn, addr)
        )

        thread.daemon = True

        thread.start()

# ================= START ================= #

accept_connections()
```
