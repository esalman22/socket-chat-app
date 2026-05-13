import socket
import threading

# إنشاء السيرفر
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# السماح بأي جهاز يتصل
server_socket.bind(('0.0.0.0', 50000))

server_socket.listen()

print("Server is running and waiting for connections...")

clients = []


# إرسال رسالة لكل العملاء
def broadcast(message, sender_conn):
    for client in clients:
        if client != sender_conn:
            try:
                client.send(message)
            except:
                clients.remove(client)


# التعامل مع كل عميل
def handle_client(conn, addr):
    print(f"New connection from {addr}")

    while True:
        try:
            data = conn.recv(1024)

            if not data:
                break

            message = f"{addr}: {data.decode()}".encode()

            print(message.decode())

            broadcast(message, conn)

        except:
            break

    print(f"Client disconnected: {addr}")
    clients.remove(conn)
    conn.close()


# قبول الاتصالات
def accept_connections():
    while True:
        conn, addr = server_socket.accept()

        clients.append(conn)

        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()


accept_connections()
