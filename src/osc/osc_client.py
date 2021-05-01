import logging
import time

from osc4py3 import oscbuildparse
from osc4py3.as_eventloop import osc_udp_client, osc_process, osc_send, osc_terminate, osc_startup

from src.osc.osc_server import OSCServer


class OSCClient:
    host = '127.0.0.1'
    port = 9951
    client_name = 'butttruck'
    running = False
    restart = True

    # osc4py3 as_allthreads is expensive but may work better than this
    @classmethod
    def start(cls, host=None, port=None, client_name=None, debug=False):
        cls.debug = debug
        if host is not None:
            cls.host = host
        if port is not None:
            cls.port = port
        if client_name is not None:
            cls.client_name = client_name
        if debug:
            logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            logger = logging.getLogger("osc")
            logger.setLevel(logging.DEBUG)
            osc_startup(logger=logger)
        else:
            osc_startup()
        osc_udp_client(cls.host, cls.port, cls.client_name)
        if not cls.running:
            cls.running = True
            return cls._run

    @classmethod
    def _run(cls):
        while cls.running:
            time.sleep(0.05)
            osc_process()

            if cls.restart and not cls.running:
                osc_terminate()
                cls.running = True
                cls.start()
                OSCServer.start(cls.debug)
        osc_terminate()

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

    @classmethod
    def get_return_url(cls):
        return OSCServer.return_url
