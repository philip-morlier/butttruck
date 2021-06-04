import logging

from osc4py3.as_eventloop import osc_startup, osc_udp_server, osc_method

from src.looper.sl_client import SLClient
from src.looper.tttruck import TTTruck


class OSCServer:
    host = '127.0.0.1'
    return_url = None

    @classmethod
    def start(cls, debug=False, port=9952):
        if debug:
            logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            logger = logging.getLogger("osc")
            logger.setLevel(logging.DEBUG)
            osc_startup(logger=logger)
        else:
            osc_startup()
        cls.return_url = cls.host + ':' + str(port)
        osc_udp_server(cls.host, port, "osc_server")
        cls._register_handlers()
        cls.register_global_updates()


    @classmethod
    def _register_handlers(cls):
        osc_method('/pingrecieved', cls.ping_handler)
        osc_method('/global/selected_loop_num', cls.selected_loop_handler)
        osc_method('/test', cls.test_handler)
        #osc_method('/loops', cls.test_handler)
        #osc_method('/global/*', cls.global_parameter_handler)
        osc_method('/parameter/*', cls.parameter_handler)
        osc_method('/save_loop_error', cls.loop_save_handler)
        osc_method('/load_loop_error', cls._loop_save_handler)

    @staticmethod
    def register_handler(address, function):
        osc_method(address, function)


    @classmethod
    def selected_loop_handler(cls, x, y, z):
        print('selected ', z)
        TTTruck.selected_loop = int(z)

    @classmethod
    def test_handler(cls, x, y, z):
        print(f'{x} {y} {z}')
        #TTTruck.callback(x, y, z)

    @staticmethod
    def loop_save_handler(x, y, z):
        print(f'Loop save error {x}  {y}  {z}')

    @staticmethod
    def parameter_handler(loop, param, value):
        print(f'Loop {loop} parameter {param} is {value}')

    @staticmethod
    def global_parameter_handler(loop, param, value):
        print(f'Global parameter {param} is {value}')

    @classmethod
    def ping_handler(cls, address, version, loop_count):
        print(f'Sooperlooper {version} is listening at: {address}. {loop_count} loops in progress')
        TTTruck.loops = loop_count

    @staticmethod
    def _loop_save_handler(x, y, z):
        print(f'Loop load error: {x} {y} {z}')

    @classmethod
    def get_return_url(cls):
        return cls.return_url

    @classmethod
    def register_global_updates(cls):
        SLClient.register_global_auto_update('selected_loop_num', '/global/selected_loop_num', interval=1)
