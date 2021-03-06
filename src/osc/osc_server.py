import logging

from osc4py3.as_eventloop import osc_startup, osc_udp_server, osc_method


class OSCServer:

    return_url = None

    @classmethod
    def start(cls, host='127.0.0.1', port=9952, debug=False):
        if debug:
            logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            logger = logging.getLogger("osc")
            logger.setLevel(logging.DEBUG)
            osc_startup(logger=logger)
        else:
            osc_startup()
        cls.return_url = host + ':' + str(port)
        osc_udp_server(host, port, "osc_server")
        cls._register_handlers()

    @classmethod
    def _register_handlers(cls):
        osc_method('/pingrecieved', cls.ping_handler)
        osc_method('/global/*', cls.global_parameter_handler)
        osc_method('/parameter/*', cls.parameter_handler)
        osc_method('/save_loop_error', cls.loop_save_handler)
        osc_method('/load_loop_error', OSCServer._loop_save_handler)

    @staticmethod
    def register_handler(address, function):
        osc_method(address, function)

    @staticmethod
    def loop_save_handler(x, y, z):
        print(f'Loop save error {x}  {y}  {z}')

    @staticmethod
    def parameter_handler(loop, param, value):
        print(f'Loop {loop} parameter {param} is {value}')

    @staticmethod
    def global_parameter_handler(loop, param, value):
        print(f'Global parameter {param} is {value}')

    @staticmethod
    def ping_handler(address, version, loop_count):
        print(f'Sooperlooper {version} is listening at: {address}. {loop_count} loops in progress')

    @staticmethod
    def _loop_save_handler(x, y, z):
        print(f'Loop load error: {x} {y} {z}')

    @classmethod
    def get_return_url(cls):
        return cls.return_url
