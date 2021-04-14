import socket
import time
import threading
from package_classes import *
from interpreter import *
from collections import deque

away = ('127.0.0.1', 9999)
home = ('0.0.0.0', 9998)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(home)


class ServerClient:

    def __init__(self):
        self.data = b''
        self.id = int(33).to_bytes(3, 'little')

    def send_ping(self):
        while True:
            time.sleep(1)
            sock.sendto(self.count_bytes, away)

    def receive_data(self):
        while True:
            time.sleep(1)
            data, port = sock.recvfrom(55000)
            self.data = data
            print(int.from_bytes(data, 'little'))
            self.translate()

    def translate(self):
        _int = int.from_bytes(self.data, 'little')
        count = _int + 1
        self.count_bytes = count.to_bytes(3, 'little')

    def run(self):
        t1 = threading.Thread(target=self.send_ping)
        t2 = threading.Thread(target=self.receive_data)
        t1.start()
        t2.start()
        # t1.join()
        # t2.join()


if __name__ == '__main__':
    d = ServerClient()
    d.run()