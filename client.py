import socket
import threading
import tkinter as tk
from tkinter import scrolledtext

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('192.168.100.7', 50000))

# إرسال الرسائل
def send_message():
    message = entry.get()
    if message:
        client_socket.sendall(message.encode())
        chat_box.insert(tk.END, "You: " + message + "\n")
        entry.delete(0, tk.END)

# استقبال الرسائل
def receive_messages():
    while True:
        try:
            data = client_socket.recv(1024)
            if not data:
                break
            # ابدأ بعد الثريد بتاع ال ui
            root.after(0, lambda: chat_box.insert(tk.END, "Server: " + data.decode() + "\n"))
        except:
            break

# UI
root = tk.Tk()
root.title("Chat Client")

chat_box = scrolledtext.ScrolledText(root, width=50, height=20)
chat_box.pack()
chat_box.config(state='disabled')

entry = tk.Entry(root, width=40)
entry.pack(side=tk.LEFT, padx=5, pady=5)
entry.bind("<Return>", lambda event: send_message())

send_button = tk.Button(root, text="Send", command=send_message)
send_button.pack(side=tk.LEFT)

# Thread للاستقبال
receive_thread = threading.Thread(target=receive_messages, daemon=True)
receive_thread.start()

# غلق البرنامج
def on_closing():

    client_socket.close()

    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)

root.mainloop()
