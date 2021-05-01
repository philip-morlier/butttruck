import json
import pickle
import random
import string
import subprocess
import tempfile
import time

from src.looper.sl_client import SLClient
from src.osc.osc_server import OSCServer
from src.udp.Peers import PeerClient
from src.udp.package_classes import Package, ShippingHandler


class TTTruck:
    loop_dir = tempfile.mkdtemp()
    loops = 0
    loop_index = {}
    loop_parameters = {}
    selected_loop = 0

    @classmethod
    def new_loop(cls):
        SLClient.loop_add()
        name = TTTruck._generate_name()
        cls.loops += 1
        cls.loop_index[cls.loops] = name
        SLClient.set_selected_loop_num(cls.loops - 1)

    @classmethod
    def delete_loop(cls):
        time.sleep(0.5)
        selected_loop = OSCServer.selected_loop
        SLClient.loop_del(selected_loop)
        time.sleep(0.5)
        print(cls.loop_index)
        name = cls.loop_index.pop(int(selected_loop + 1))
        cls.loops -= 1
        cls.loop_index = cls.update_loop_index(cls.loops)

    @classmethod
    def publish_loop(cls):
        #name = TTTruck._generate_name()
        # TODO
        name = cls.loop_index[SLClient.get_selected_loop_num()]
        file = cls.loop_dir + '/' + cls.loops[SLClient.get_selected_loop_num()]
        cls._save_loop(file)
        time.sleep(1)
        msg = {'loop_add': name}
        p = Package(77, file)
        s = ShippingHandler(p)
        slices = s.slice()
        enums = s.enumerate()
        metas = s.meta()
        #msg = cls._format_msg('loop_add', name, parameters=[])

        PeerClient.send_queue.append(pickle.dumps(msg))



    @staticmethod
    def _generate_name():
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))

    @classmethod
    def _save_loop(cls, file):
        SLClient.save_loop( file)

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


    # @classmethod
    # def delete_loop(cls, name):
    #     msg = cls._format_msg('loop_del', name)


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
    def update_loop_index(cls, idx):
        updated = {}
        for k, v in cls.loop_index.items():
            if k > idx:
                item = cls.loop_index[k]
                updated[k-1] = item
            else:
                updated[k] = v
        return updated


    @classmethod
    def _get_all_global_parameters(cls):
        pass

    @classmethod
    def _get_all_parameters(cls):
        pass

    @classmethod
    def callback(cls, x, y, z):
        print('callback')


if __name__ == '__main__':
    from src.osc.osc_server import OSCServer
    OSCServer.start(debug=True)
    time.sleep(1)
    SLClient.ping()
    time.sleep(1)

