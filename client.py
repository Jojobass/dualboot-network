import socket
import sys
import re
from threading import Thread

HOST = "127.0.0.1"
PORT = 12346

nickname = "unknown"


def read_thread(conn: socket.socket) -> None:
    global nickname
    while True:
        message = conn.recv(2048).decode("utf-8")
        if message:
            match = re.fullmatch(r"nickname::(.+)", message)
            if match is not None:
                nickname = match.group(1)
                print("You successfully logged in!")
            else:
                print(message)
        else:
            print("Соединение с сервером потеряно! :q для выхода")
            break


def write_thread(conn: socket.socket) -> None:
    while True:
        message = sys.stdin.readline().strip()
        if message == ":q":
            break
        try:
            conn.sendall(message.encode("utf-8"))
        except BrokenPipeError:
            break
        if nickname != "unknown":
            print(f"<{nickname}>: ", end="")
        print(message)


def start_client() -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.connect((HOST, PORT))
        print("Type :q to quit")
        read_thread_ = Thread(target=read_thread, args=(server,))
        write_thread_ = Thread(target=write_thread, args=(server,))
        read_thread_.start()
        write_thread_.start()
        write_thread_.join()
        read_thread_.join()


if __name__ == "__main__":
    start_client()
