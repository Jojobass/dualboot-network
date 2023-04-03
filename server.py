import socket

HOST = "127.0.0.1"
PORT = 12345


def new_client(connection: socket.socket) -> None:
    with connection:
        while True:
            data = connection.recv(1024)
            if not data:
                break
            print(f"Received {data}")
            connection.sendall(b"Hello client")


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    while True:
        conn, _ = s.accept()
        new_client(conn)