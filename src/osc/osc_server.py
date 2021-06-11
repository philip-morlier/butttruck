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


    @classmethod
    def _register_handlers(cls):
        osc_method('/pingrecieved', cls.ping_handler)
        osc_method('/global/*', cls.global_parameter_handler)
        osc_method('/global/parameter/selected_loop_num', cls.selected_loop_handler)
        osc_method('/cycle_len', cls.cycle_len_handler)
        osc_method('/test', cls.test_handler)

        osc_method('/loop_pos', cls.loop_pos_handler)
        osc_method('/state', cls.state_handler)
        #osc_method('/loops', cls.test_handler)

        osc_method('/parameter/*', cls.parameter_handler)
        osc_method('/save_loop_error', cls.loop_save_handler)
        osc_method('/load_loop_error', cls._loop_save_handler)

    @staticmethod
    def register_handler(address, function):
        osc_method(address, function)


    @classmethod
    def cycle_len_handler(cls, x, y, z):
        SLClient.cycle_len = z

    @classmethod
    def selected_loop_handler(cls, x, y, z):
        print('Selection handler ', z)
        SLClient.selected_loop = int(z)
        SLClient.selection_evt.set()
        SLClient.selection_evt.clear()

    @classmethod
    def loop_pos_handler(cls, x, y, z):
        #print(x, y, z)
        SLClient.loop_pos = z


    @classmethod
    def test_handler(cls, x, y, z):
        #pass
        print(f'{x} {y} {z}')
    # TTTruck.callback(x, y, z)

    @staticmethod
    def loop_save_handler(x, y, z):
        print(f'Loop save error {x}  {y}  {z}')

    @staticmethod
    def parameter_handler(loop, param, value):
        print(f'Loop {loop} parameter {param} is {value}')
        name = TTTruck.loop_index[loop]
        TTTruck.changes[name][param] = value
        SLClient.parameter_evt.set()
        print(TTTruck.changes)
        SLClient.parameter_evt.clear()

    @staticmethod
    def state_handler(loop, param, value):
        print('STATE CHANGE ', loop, param, value)
        if SLClient.state_change.is_set():
            print('wwops, wrong state')
            SLClient.state_change.clear()
        SLClient.state = SLClient.states[int(value)]
        SLClient.state_change.set()
        SLClient.state_change.clear()


    @staticmethod
    def global_parameter_handler(loop, param, value):
        print(f'Global parameter {param} is {value}')
        SLClient.global_evt.set()
        SLClient.global_evt.clear()

    @classmethod
    def ping_handler(cls, address, version, loop_count):
        SLClient.loops = (loop_count - 1 if loop_count > 0 else 0)
        SLClient.ping_evt.set()
        SLClient.ping_evt.clear()

    @staticmethod
    def _loop_save_handler(x, y, z):
        print(f'Loop load error: {x} {y} {z}')

    @classmethod
    def get_return_url(cls):
        return cls.return_url
