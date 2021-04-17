import json
import pickle
import random
import string
import subprocess
import tempfile
import time

from src.looper.sl_client import SLClient
from src.udp import Peers
from src.udp.Peers import PeerClient


class TTTruck:
    loop_dir = tempfile.mkdtemp()
    loops = 1
    loop_index = {}
    loop_parameters = {}
    deleted_loops = []

    @classmethod
    def publish_loop(cls, loop_number):
        name = TTTruck._generate_name()
        file = cls.loop_dir + '/' + name
        cls._save_loop(loop_number, file)
        time.sleep(1)
        msg = {'loop_add': name}
        #msg = cls._format_msg('loop_add', name, parameters=[])

        PeerClient.send_queue.append(pickle.dumps(msg))


    @staticmethod
    def _generate_name():
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))

    @classmethod
    def _save_loop(cls, loop_number, file):
        SLClient.save_loop(loop_number, file)

    @classmethod
    def _format_msg(cls, command, name, parameters):
        if command == 'loop_add':
            return json.dumps({'command': command, 'name': name, 'parameters': parameters})
        if command == 'loop_del':
            return json.dumps({'command': command, 'name': name})
        if command == 'loop_set':
            return json.dumps({'command': command, 'name': name, 'parameters': parameters})
        if command == 'global_set':
            return json.dumps({'command': command, 'parameters': parameters})

    @staticmethod
    def dispatch(msg):
        msg = json.loads(msg)
        command = msg['command']
        getattr(TTTruck, command)(msg)

    @classmethod
    def loop_add(cls, msg):
        name = msg['name']
        parameters = msg['parameters']
        url = msg['url']
        loop_file = cls.download_loop(url)
        index = cls._get_loops()
        SLClient.loop_add()
        SLClient.load_loop(index, loop_file)
        SLClient.set_quantize(3, loop_number=index)
        SLClient.set_playback_sync(1, loop_number=index)
        SLClient.pause(loop_number=index)


    @classmethod
    def delete_loop(cls, name):
        msg = cls._format_msg('loop_del', name)


    # TODO
    @classmethod
    def modify_loop(cls, name):
        idx = cls.get_loop_index(name)
        parameters = cls._get_all_parameters(name)
        msg = cls._format_msg('loop_set', name, parameters)


    # TODO
    @classmethod
    def modify_global(cls):
        parameters = cls._get_all_global_parameters()
        msg = cls._format_msg('global_set', parameters)


    @classmethod
    def _get_loops(cls):
        pass

    @classmethod
    def set_loops(cls, i):
        cls.loops = i

    @classmethod
    def get_loop_index(cls, name):
        return cls.loop_index[name]

    @classmethod
    def update_loop_index(cls):
        i = 0
        for name, idx in cls.loop_index:
            if idx > i:
                cls.loop_index['name'] = i
            i += 1

    @classmethod
    def _get_all_global_parameters(cls):
        pass

    @classmethod
    def _get_all_parameters(cls):
        pass


if __name__ == '__main__':
    from src.osc.osc_server import OSCServer
    OSCServer.start(debug=True)
    time.sleep(1)
    SLClient.ping()
    time.sleep(1)

