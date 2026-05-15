import socket
import threading

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server_socket.bind(("0.0.0.0", 18729))
server_socket.listen()

print("Server running...")

clients = {}

END_MARK = b"<END>"

#================ BROADCAST =================#

def broadcast(data, sender=None):
    for c in list(clients):
        try:
            if c != sender:
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

        print(f"{username} connected from {addr}")

        while True:

            data = conn.recv(1024)

            if not data:
                break

            #================ TEXT =================#

            if data.startswith(b"TEXT:"):
                broadcast(data, conn)

            #================ IMAGE / FILE / VIDEO =================#

            elif data.startswith(b"IMAGE:") or data.startswith(b"FILE:") or data.startswith(b"VIDEO:"):

                header = data  # مهم جدًا

                broadcast(header, conn)

                file_data = b""

                # استقبال الملف كامل
                while True:
                    chunk = conn.recv(4096)

                    if END_MARK in chunk:
                        file_data += chunk.replace(END_MARK, b"")
                        break

                    file_data += chunk

                # إرسال الملف لكل العملاء
                for c in list(clients):
                    try:
                        if c != conn:
                            c.send(file_data)
                            c.send(END_MARK)
                    except:
                        c.close()
                        if c in clients:
                            del clients[c]

            else:
                # fallback لأي نص عادي
                broadcast(data, conn)

    except:
        pass

    finally:
        if conn in clients:
            print(clients[conn], "disconnected")
            del clients[conn]

        conn.close()

#================ ACCEPT CONNECTIONS =================#

while True:
    conn, addr = server_socket.accept()
    threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
