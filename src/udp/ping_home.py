import socket
import time
import threading
from package_classes import *
from interpreter import *
from collections import deque

package_protocol = {
    'standard ping': 100,
    'meta': 200,
    'received meta': 300,
    'body': 400,
    'received body': 500
}

away = ('127.0.0.1', 9998)
home = ('0.0.0.0', 9999)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(home)

p = Package(666, 'loop.wav')
s = ShippingHandler(p.package())
m = s.meta()
e = s.enumerate()

d = DataInterpreter()

sender_id = 0
_id = sender_id.to_bytes(3, 'little')

strd_ping = 100
sdp = strd_ping.to_bytes(3, 'little')

meta_rcvd = 300
mrcd = meta_rcvd.to_bytes(3, 'little')



global wav_frame
wav_frame = None




def ping():
    while True:
        message = sdp + _id
        sock.sendto(message, away)
        time.sleep(1)
        global data
        data, port = sock.recvfrom(55000)
        global tag
        tag = int.from_bytes(data[0:3], 'little')
        time.sleep(1)
        print(tag)


def capture():
    _data = data
    _tag = tag
    while True:
        time.sleep(2)
        if _tag == 100:
            pass
        if _tag == 200:
            if len(_data) == 62:
                wav_frame = d.frame(_data)
                message = mrcd + _id
                sock.sendto(message, away)
            else:
                pass
        if tag == 400:
            size = wav_frame[0]
            count = wav_frame[1]
            header = wav_frame[2]
            _dict = wav_frame[3]
            number = data[3:6]
            _number = int.from_bytes(number, 'little')
            chunk = data[6:len(data)]
            _dict[number] = chunk
            chunks = [_dict[x] for x in _dict if _dict[x] is not None]
            file = b''
            if len(chunks) == count:
                _file = file.join(chunks)
                wav = header + _file
                if sys.getsizeof(wav) == size:
                    with open('success.wav', mode='bx') as f:
                        f.write(wav)
            sock.sendto(sdp, away)






        # if tag == 300:
        #     pass
        # if tag == 400:
        #     pass




#
# def ping(arg=None):
#     strd_ping = 100
#     sdp = strd_ping.to_bytes(3, 'little')
#     while True:
#         if arg:
#             message = arg
#         else:
#             message = sdp
#         sock.sendto(message, away)
#         print('sent')
#         time.sleep(1)
#
#
# def listen():
#     global _count
#     _count = 0
#     while True:
#         print('listening')
#         data, port = sock.recvfrom(55000)
#         new_count = int.from_bytes(data[0:3], 'little')
#         if new_count > _count:
#


# to_send = input()
# meta = m
# enum = e


t1 = threading.Thread(target=ping)
t2 = threading.Thread(target=capture)

t1.start()
t2.start()

t1.join()
t2.join()

# for i in e:
#     ping(i)