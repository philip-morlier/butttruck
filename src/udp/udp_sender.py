import socket
import time

away = ('127.0.0.1', 9999)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)


class UdpSender:

    @staticmethod
    def send_udp(message):
        sock.sendto(message, away)
