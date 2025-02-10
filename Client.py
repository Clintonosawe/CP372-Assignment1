import socket

HOST = "127.0.0.1"
PORT = 12345

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))

    client_name = client.recv(1024).decode()
    print(f"Connected as {client_name}")

    while True:
        message = input("> ").strip()
        if not message:
            continue

        client.send(message.encode())

        if message.lower() == "exit":
            break

        response = client.recv(4096).decode()
        print("Server:", response)

    client.close()

if __name__ == "__main__":
    main()
