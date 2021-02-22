import time
from threading import Thread

from osc4py3 import oscbuildparse
from osc4py3.as_eventloop import osc_udp_client, osc_process, osc_send

class OSCClient:
    host = None
    port = None
    client_name = None
    running = False
    restart = True

    # osc4py3 as_allthreads is expensive but may work better than this
    @classmethod
    def start(cls, host='127.0.0.1', port=9951, client_name='butttruck'):
        if cls.host is None:
            cls.host = host
        if cls.port is None:
            cls.port = port
        if cls.client_name is None:
            cls.client_name = client_name
        thread = Thread(target=cls._run, daemon=True)
        cls.running = True
        thread.start()

    @classmethod
    def _run(cls):
        osc_udp_client(cls.host, cls.port, cls.client_name)
        while cls.running:
            time.sleep(0.05)
            osc_process()
        if cls.restart:
            cls.start()

    @classmethod
    def send_message(cls, message, args=None, type=None):
        if not cls.running:
            cls.start()
        msg = oscbuildparse.OSCMessage(message, type, args)
        osc_send(msg, cls.client_name)

    @classmethod
    def stop(cls):
        cls.running = False
        cls.restart = False

    @classmethod
    def restart(cls):
        cls.running = False
