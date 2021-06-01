import json
import pickle
import random
import string
import subprocess
import tempfile
import time

from src.looper.sl_client import SLClient
from src.udp.Peers import PeerClient
from src.udp.package_classes import Package, ShippingHandler
from src.udp.wav_slicer import WavSlicer


class TTTruck:
    loop_dir = tempfile.mkdtemp()
    loops = 0
    loop_index = {}
    loop_parameters = {}
    selected_loop = 0
    # {name : []}
    changes = {}

    @classmethod
    def loop_record(cls):
        SLClient.record()

    @classmethod
    def new_loop(cls):
        SLClient.loop_add()
        name = TTTruck._generate_name()
        cls.loops += 1
        cls.loop_index[cls.loops] = name
        SLClient.set_selected_loop_num(cls.loops - 1)

    @classmethod
    def delete_loop(cls):
        SLClient.loop_del(cls.selected_loop)
        cls.loop_index.pop(int(cls.selected_loop + 1))
        cls.loops -= 1
        cls.loop_index = cls.update_loop_index(cls.loops)

    @classmethod
    def publish_loop(cls):
        SLClient.get_selected_loop_num()
        time.sleep(1)
        name = cls.loop_index[cls.selected_loop]
        file = cls.loop_dir + '/' + name
        SLClient.save_loop(file)
        # TODO: find a more reliable way to determine when the file has been written
        time.sleep(1)
        WavSlicer.slice_and_send(file, name)

    @classmethod
    def loop_reverse(cls):
        name = cls.loop_index[TTTruck.get_selected_loop()]
        SLClient.reverse()
        if cls.changes.get(name, None) is None:
            cls.changes[name] = {'reverse': 1}
        else:
            if cls.changes[name]['reverse'] == 0:
                cls.changes[name]['reverse'] = 1
            if cls.changes[name]['reverse'] == 1:
                cls.changes[name]['reverse'] = 0

    @classmethod
    def loop_rate(cls, rate):
        name = cls.loop_index[TTTruck.get_selected_loop()]
        SLClient.set_rate(rate)
        if cls.changes.get(name, None) is None:
            cls.changes[name] = {}
        cls.changes[name] = {'rate': rate}

    @staticmethod
    def _generate_name():
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))

    @classmethod
    def loop_add(cls, msg):
        SLClient.loop_add()
        SLClient.load_loop(index, loop_file)
        SLClient.set_quantize(3, loop_number=index)
        SLClient.set_playback_sync(1, loop_number=index)
        SLClient.pause(loop_number=index)

    @classmethod
    def get_loop_index(cls, name):
        return cls.loop_index[name]

    @classmethod
    def update_loop_index(cls, number_of_loops):
        updated = {}
        for loop_index, loop_name in cls.loop_index.items():
            if loop_index == number_of_loops + 1:
                updated[loop_index-1] = loop_name
            elif loop_index == number_of_loops:
                updated[loop_index] = loop_name
            else:
                raise Exception("loop index is broken")
        return updated


    @classmethod
    def callback(cls, x, y, z):
        try:
            getattr(TTTruck, y)(z)
        except Exception as e:
            print(e)

    @classmethod
    def selected_loop_num(cls, loop_num):
        cls.selected_loop = loop_num

    @classmethod
    def select_next_loop(cls):
        if (cls.get_selected_loop() < cls.loops):
            SLClient.set_selected_loop_num(cls.selected_loop + 1)
        else:
            SLClient.set_selected_loop_num(0)
        time.sleep(0.5)
        SLClient.get_selected_loop_num()

    @classmethod
    def get_selected_loop(cls):
        return cls.selected_loop + 1

    @classmethod
    def delete_all_loops(cls):
        SLClient.ping()
        time.sleep(1)
        while cls.loops > 0:
            SLClient.set_selected_loop_num(1)
            cls.delete_loop()
            time.sleep(1)

    @classmethod
    def new_remote_loop(cls):
        msg = json.dumps({'action': 'new_loop'})
        PeerClient.send_queue.append(msg)
        print(PeerClient.send_queue)

