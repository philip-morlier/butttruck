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

sender_id = 77
_id = sender_id.to_bytes(3, 'little')

p = Package(sender_id, 'loop.wav')
s = ShippingHandler(p.package())
m = s.meta()
e = s.enumerate()


strd_ping = 100
sdp = strd_ping.to_bytes(3, 'little')




def ping(arg=None):
    while True:
        if arg:
            message = arg
        else:
            message = sdp + _id
        sock. sendto(message, away)
        data, port = sock.recvfrom(55000)
        protocol_number = data[0:3]
        global tag
        tag = int.from_bytes(protocol_number, 'little')
        time.sleep(1)


def capture(arg=None):
    _tag = tag
    while True:
        time.sleep(1)
        print(_tag)
        if arg:
            sock.sendto(arg, away)
        if tag == 300:
            for i in e:
                sock.sendto(i, away)


t1 = threading.Thread(target=ping)
t2 = threading.Thread(target=capture(m))

t1.start()
t2.start()

t1.join()
t2.join()


