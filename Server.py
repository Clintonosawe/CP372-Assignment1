import socket
import threading
import os
from datetime import datetime

# Server Configuration
HOST = "127.0.0.1"
PORT = 12345
MAX_CLIENTS = 3
clients = {}
file_repo = "server_files"  # Directory for storing files

# Ensure the file repository exists
os.makedirs(file_repo, exist_ok=True)

def handle_client(client_socket, client_name):
    clients[client_name] = {
        "connected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "disconnected_at": None
    }
    
    try:
        while True:
            message = client_socket.recv(1024).decode()
            if not message:
                break
            
            if message.lower() == "exit":
                print(f"{client_name} disconnected.")
                clients[client_name]["disconnected_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                break
            elif message.lower() == "status":
                status = "\n".join([f"{k}: {v['connected_at']} - {v['disconnected_at'] or 'Active'}" for k, v in clients.items()])
                client_socket.send(status.encode())
            elif message.lower() == "list":
                files = os.listdir(file_repo)
                client_socket.send("\n".join(files).encode() if files else b"No files available.")
            elif message.startswith("get "):
                filename = message.split(" ", 1)[1]
                filepath = os.path.join(file_repo, filename)
                if os.path.exists(filepath):
                    with open(filepath, "rb") as f:
                        client_socket.sendall(f.read())
                else:
                    client_socket.send(b"File not found.")
            else:
                response = f"{message} ACK"
                client_socket.send(response.encode())
    
    except ConnectionResetError:
        pass
    finally:
        client_socket.close()
        del clients[client_name]

# Main server function
def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(MAX_CLIENTS)
    print(f"Server listening on {HOST}:{PORT}")

    client_id = 1
    while True:
        if len(clients) < MAX_CLIENTS:
            client_socket, addr = server.accept()
            client_name = f"Client{client_id:02d}"
            client_id += 1
            print(f"{client_name} connected from {addr}")

            client_socket.send(client_name.encode())

            thread = threading.Thread(target=handle_client, args=(client_socket, client_name))
            thread.start()
        else:
            print("Max clients reached, rejecting connection.")

if __name__ == "__main__":
    main()
