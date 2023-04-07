import socket
from threading import Thread
import datetime

HOST = "127.0.0.1"
PORT = 12346

clients = {}
nicknames = {"unknown"}


class fragile(object):
    class Break(Exception):
        """Break out of the with statement"""

    def __init__(self, value):
        self.value = value

    def __enter__(self):
        return self.value.__enter__()

    def __exit__(self, etype, value, traceback):
        error = self.value.__exit__(etype, value, traceback)
        if etype == self.Break:
            return True
        return error


def client_thread(conn_: socket.socket, address: tuple) -> None:
    with fragile(conn_) as connection:
        nickname = "unknown"
        while nickname in nicknames:
            connection.send(b"Welcome to the chatroom!\nPlease, enter your nickname:")
            nickname = connection.recv(1024).decode("utf-8")
            if not nickname:
                raise fragile.Break

        connection.send(f"nickname::{nickname}".encode("utf-8"))
        nicknames.add(nickname)
        clients[f"{address[0]}:{str(address[1])}"]["nickname"] = nickname
        print(f"{nickname} [{address[0]}:{str(address[1])}] connected.")
        send_message(f"{nickname} connected.", connection)

        while True:
            message = connection.recv(1024).decode("utf-8")
            if message:
                full_message = f"<{nickname}>: {message.strip()}"
                print(
                    f"[{address[0]}:{str(address[1])}, {datetime.datetime.now()}] {full_message}"
                )
                send_message(full_message, connection)
            else:
                break
    remove_client(address[0] + ":" + str(address[1]))


def send_message(message: str, connection: socket.socket) -> None:
    for client in clients:
        if clients[client]["socket"] != connection and "nickname" in clients[client]:
            clients[client]["socket"].send(message.encode("utf-8"))


def remove_client(client: str) -> None:
    if client in clients:
        address = client
        connection = clients[client]["socket"]
        if "nickname" in clients[client]:
            nickname = clients[client]["nickname"]
            nicknames.remove(clients[client]["nickname"])
            print(f"{nickname}", end="")
            send_message(f"{nickname} disconnected.", connection)
        clients.pop(client)
        print(f" [{address}] disconnected.")


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    while True:
        conn, addr = s.accept()
        clients[addr[0] + ":" + str(addr[1])] = {"socket": conn, "address": addr}
        new_thread = Thread(target=client_thread, args=(conn, addr))
        new_thread.start()
