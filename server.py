
# server.py

import socket
import threading
import os

# ================= CONFIG ================= #

HOST = "0.0.0.0"

PORT = int(
    os.environ.get("PORT", 18729)
)

BUFFER_SIZE = 4096

EOF_MARKER = b"<END_OF_MEDIA_CUSTOM_PROTOCOL_999>"

# ================= SERVER ================= #

server = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
)

server.bind((HOST, PORT))

server.listen()

print(f"Server running on port {PORT}...")

clients = []

# ================= SAVE FOLDER ================= #

RECEIVED_FOLDER = "received_files"

os.makedirs(
    RECEIVED_FOLDER,
    exist_ok=True
)

# ================= BROADCAST ================= #

def broadcast(data, sender=None):

    for client in clients[:]:

        if client != sender:

            try:

                client.sendall(data)

            except:

                try:
                    client.close()
                except:
                    pass

                if client in clients:
                    clients.remove(client)

# ================= HANDLE CLIENT ================= #

def handle_client(conn, addr):

    print(f"Client connected: {addr}")

    buffer = b""

    try:

        while True:

            data = conn.recv(BUFFER_SIZE)

            if not data:
                break

            buffer += data

            while EOF_MARKER in buffer:

                message_bytes, buffer = buffer.split(
                    EOF_MARKER,
                    1
                )

                # ================= TEXT ================= #

                if message_bytes.startswith(b"TEXT:"):

                    print(
                        "TEXT:",
                        message_bytes[:100]
                    )

                    broadcast(
                        message_bytes + EOF_MARKER,
                        conn
                    )

                # ================= IMAGE ================= #

                elif (
                    message_bytes.startswith(b"IMAGE:")
                    or
                    message_bytes.startswith(b"IMAGE_HD:")
                ):

                    try:

                        parts = message_bytes.split(
                            b":",
                            2
                        )

                        msg_type = parts[0].decode()

                        filename = parts[1].decode()

                        file_data = parts[2]

                        save_path = os.path.join(
                            RECEIVED_FOLDER,
                            filename
                        )

                        with open(
                            save_path,
                            "wb"
                        ) as f:

                            f.write(file_data)

                        print(
                            f"{msg_type} saved:",
                            save_path
                        )

                    except Exception as e:

                        print(
                            "Image Save Error:",
                            e
                        )

                    broadcast(
                        message_bytes + EOF_MARKER,
                        conn
                    )

                # ================= FILE ================= #

                elif message_bytes.startswith(b"FILE:"):

                    try:

                        parts = message_bytes.split(
                            b":",
                            2
                        )

                        filename = parts[1].decode()

                        file_data = parts[2]

                        save_path = os.path.join(
                            RECEIVED_FOLDER,
                            filename
                        )

                        with open(
                            save_path,
                            "wb"
                        ) as f:

                            f.write(file_data)

                        print(
                            "FILE saved:",
                            save_path
                        )

                    except Exception as e:

                        print(
                            "File Save Error:",
                            e
                        )

                    broadcast(
                        message_bytes + EOF_MARKER,
                        conn
                    )

    except Exception as e:

        print(
            "Client Error:",
            e
        )

    finally:

        print(
            f"Client disconnected: {addr}"
        )

        if conn in clients:
            clients.remove(conn)

        try:
            conn.close()
        except:
            pass

# ================= ACCEPT CLIENTS ================= #

def accept_clients():

    while True:

        conn, addr = server.accept()

        clients.append(conn)

        thread = threading.Thread(
            target=handle_client,
            args=(conn, addr)
        )

        thread.daemon = True

        thread.start()

# ================= START ================= #

accept_clients()

