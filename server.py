import socket
import threading
import tkinter as tk
from tkinter import scrolledtext

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('0.0.0.0', 50000))
server_socket.listen()

print("Waiting for connection...")
conn, addr = server_socket.accept()
print("Connected to", addr)

# إرسال
def send_message():
    message = entry.get()
    if message:
        conn.sendall(message.encode())
        chat_box.insert(tk.END, "You: " + message + "\n")
        entry.delete(0, tk.END)

# استقبال
def receive_messages():
    while True:
        try:
            data = conn.recv(1024)
            if not data:
                break
            # ابدأ بعد الثريد بتاع ال ui
            root.after(0, lambda: chat_box.insert(tk.END, "Client: " + data.decode() + "\n"))
        except:
            break


# Thread للاستقبال
receive_thread = threading.Thread(target=receive_messages, daemon=True)
receive_thread.start()



