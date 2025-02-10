import socket
import threading
import os
from datetime import datetime

# Server Configuration
HOST = "127.0.0.1"
PORT = 12345
MAX_CLIENTS = 3
clients = {}  # Stores client info: {client_name: (conn, addr, connected_time)}
client_count = 1  # Tracks assigned client numbers
file_repo = "server_files"

# Ensure file directory exists
os.makedirs(file_repo, exist_ok=True)

# Handle client communication
def handle_client(conn, addr, client_name):
    global clients

    # Store client connection time
    connected_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    clients[client_name] = {"addr": addr, "connected_at": connected_time, "disconnected_at": None}

    try:
        while True:
            message = conn.recv(1024).decode().strip()
            if not message:
                break

            print(f"{client_name} says: {message}")

            if message.lower() == "exit":
                print(f"{client_name} disconnected.")
                clients[client_name]["disconnected_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                break
            elif message.lower() == "status":
                status = "\n".join([f"{k}: {v['connected_at']} - {v['disconnected_at'] or 'Active'}" for k, v in clients.items()])
                conn.send(status.encode())
            elif message.lower() == "list":
                files = os.listdir(file_repo)
                conn.send("\n".join(files).encode() if files else b"No files available.")
            elif message.startswith("get "):
                filename = message.split(" ", 1)[1]
                filepath = os.path.join(file_repo, filename)
                if os.path.exists(filepath):
                    with open(filepath, "rb") as f:
                        conn.sendall(f.read())
                else:
                    conn.send(b"File not found.")
            else:
                conn.send(f"{message} ACK".encode())

    except ConnectionResetError:
        pass
    finally:
        conn.close()
        del clients[client_name]

# Main server function
def main():
    global client_count
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(MAX_CLIENTS)
    print(f"Server listening on {HOST}:{PORT}")

    while True:
        if len(clients) < MAX_CLIENTS:
            conn, addr = server.accept()
            client_name = f"Client{client_count:02d}"
            client_count += 1

            print(f"{client_name} connected from {addr}")
            conn.send(client_name.encode())  # Send assigned name to client

            thread = threading.Thread(target=handle_client, args=(conn, addr, client_name))
            thread.start()
        else:
            conn, addr = server.accept()
            print(f"Rejected connection from {addr}: Max clients reached.")
            conn.send(b"Server full. Try again later.")
            conn.close()  # Immediately close connection

if __name__ == "__main__":
    main()
