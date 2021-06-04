import random
import string
import tempfile
import time

from src.looper.sl_client import SLClient
from src.udp.wav_slicer import WavSlicer


class TTTruck:
    loop_dir = tempfile.mkdtemp()
    loops = 0
    loop_index = {}
    loop_parameters = {}
    selected_loop = 0
    changes = {}
    global_changes = {}

    @classmethod
    def loop_record(cls):
        SLClient.record()

    @classmethod
    def register_loop_updates(cls):
        SLClient.register_auto_update('loop_pos', '/test', interval=1, loop_number=cls.loops)
        # SLClient.register_auto_update('cycle_len', '/test', interval=1, loop_number=cls.loops)
        # SLClient.register_auto_update('free_time', '/test', interval=1, loop_number=cls.loops)
        # SLClient.register_auto_update('total_time', '/test', interval=1, loop_number=cls.loops)
        # SLClient.register_auto_update('waiting', '/test', interval=1, loop_number=cls.loops)
        # SLClient.register_auto_update('state', '/test', interval=1, loop_number=cls.loops)
        # SLClient.register_auto_update('next_state', '/test', interval=1, loop_number=cls.loops)
        SLClient.register_auto_update('save_loop', '/test', interval=1, loop_number=cls.selected_loop)
        SLClient.register_auto_update('load_loop', '/test', interval=1, loop_number=cls.selected_loop)


    @classmethod
    def delete_loop(cls):
        SLClient.get_selected_loop_num()
        SLClient.loop_del(cls.selected_loop)
        if cls.loop_index.get(cls.selected_loop, None) is None:
            print(f'Unable to delete loop, index is broken! selected_loop = {cls.selected_loop} index = {cls.loop_index}')
        else:
            cls.loop_index.pop(int(cls.selected_loop))

        SLClient.ping()
        cls.loop_index = cls.update_loop_index()
        cls.select_next_loop()

    @classmethod
    def publish_loop(cls):
        SLClient.get_selected_loop_num()
        name = cls._get_selected_loop_name()
        file = cls.loop_dir + '/' + name
        SLClient.save_loop(file, loop_number=cls.selected_loop)
        WavSlicer.slice_and_send(name, file)

    @classmethod
    def publish_selected_changes(cls):
        name = cls.loop_index.get(cls.selected_loop, None)
        if name is None:
            print(f'{name} is not in {cls.loop_index}')
            return
        changes = cls.changes.get(name, None)
        if changes is None:
            print(f'No changes for {cls.selected_loop} in {cls.changes}')
        else:
            print(f'Sending changes {changes} for {name}')
            WavSlicer.send_changes(changes, name=name)

    @classmethod
    def publish_global_changes(cls):
        WavSlicer.send_changes(cls.global_changes)

    @classmethod
    def publish_all_changes(cls):
        print(cls.changes)
        if cls.changes:
            print('Sending changes ')
            WavSlicer.send_changes(cls.changes)

    @classmethod
    def set_sync_source(cls, source):
        SLClient.set_sync_source(source)
        cls.global_changes['sync_source'] = source

    @classmethod
    def loop_reverse(cls):
        name = cls._get_selected_loop_name()
        SLClient.reverse()
        if cls.changes.get(name, None) is None:
            cls.changes[name] = {'reverse': 1}
        else:
            if cls.changes[name]['reverse'] == 0:
                cls.changes[name]['reverse'] = 1
            if cls.changes[name]['reverse'] == 1:
                cls.changes[name]['reverse'] = 0

    @classmethod
    def _get_selected_loop_name(cls):
        try:
            name =  cls.loop_index[cls.selected_loop]
            return name
        except KeyError:
            print(f'{cls.selected_loop} is not in the index: {cls.loop_index}')

    @classmethod
    def loop_rate(cls, rate):
        SLClient.register_update('rate', '/parameter/rate', loop_number=cls.selected_loop)
        name = cls._get_selected_loop_name()
        SLClient.set_rate(rate)
        if cls.changes.get(name, None) is None:
            cls.changes[name] = {}
        cls.changes[name] = {'rate': rate}

    @staticmethod
    def _generate_name():
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))

    @classmethod
    def loop_add(cls,):
        SLClient.loop_add()
        name = TTTruck._generate_name()
        SLClient.ping()
        if cls.loop_index.get(cls.loops - 1, None) is not None:
            print(f'loop index is broken! loops = {cls.loops} index = {cls.loop_index}')
        cls.loop_index[cls.loops - 1] = name
        cls.select_loop(cls.loops - 1)
        time.sleep(1)
        cls.register_loop_updates()
        SLClient.set_quantize(3, loop_number=cls.selected_loop)
        SLClient.set_sync(1, loop_number=cls.selected_loop)
        SLClient.set_playback_sync(1, loop_number=cls.selected_loop)
        SLClient.set_mute_quantized(1, loop_number=cls.selected_loop)
        SLClient.pause(loop_number=cls.selected_loop)

    @classmethod
    def loop_load(cls, name):
        cls.loop_add()
        SLClient.load_loop(cls.selected_loop, cls.loop_dir + '/' + name + '.wav')
        SLClient.pause(loop_number=cls.selected_loop)

    @classmethod
    def get_loop_index(cls, name):
        return cls.loop_index[name]

    @classmethod
    def update_loop_index(cls):
        updated = {}
        for loop_index, loop_name in cls.loop_index.items():
            if loop_index >= cls.loops:
                updated[loop_index - 1] = loop_name
            elif loop_index < cls.loops:
                updated[loop_index] = loop_name
            else:
                raise Exception(f"loop index is broken! Index: {loop_index}, Name: {loop_name} , clsIndex: {cls.loop_index}")
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
    def select_loop(cls, loop_num):
        SLClient.set_selected_loop_num(loop_num)
        SLClient.get_selected_loop_num()

    @classmethod
    def select_next_loop(cls):
        if cls.selected_loop < cls.loops - 1:
            SLClient.set_selected_loop_num(cls.selected_loop + 1)
        else:
            SLClient.set_selected_loop_num(0)
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
    def write_wav(cls, wav):
        name = wav[0]
        bytes = b''.join(wav[1])
        with open(cls.loop_dir + '/' + name + '.wav', 'wb+') as f:
            f.write(bytes)
        if name == 'test1':
            TTTruck.loop_load(name)
