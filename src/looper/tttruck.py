import random
import string
import tempfile
import time

from src.looper.sl_client import SLClient
from src.udp.wav_slicer import WavSlicer


class TTTruck:
    loop_dir = tempfile.mkdtemp()
    loop_index = {}
    loop_parameters = {}
    changes = {}
    global_changes = {}

    @classmethod
    def loop_record(cls):
        loop = cls.get_selected_loop()
        SLClient.record(loop)

    @classmethod
    def delete_loop(cls):
        selected = cls.get_selected_loop()
        SLClient.loop_del(selected)
        if cls.loop_index.get(selected, None) is None:
            print(
                f'Unable toselect_n delete loop, index is broken! selected_loop = {selected} index = {cls.loop_index}')
        else:
            cls.loop_index.pop(selected)
        loop_number = cls.get_number_of_loops()
        cls.loop_index = cls._update_loop_index(loop_number)

    @classmethod
    def get_number_of_loops(cls):
        return SLClient.ping()

    @classmethod
    def get_selected_loop(cls):
        return SLClient.get_selected_loop_num()

    @classmethod
    def publish_loop(cls):
        loop = cls.get_selected_loop()
        name = cls._get_selected_loop_name(loop)
        file = cls.loop_dir + '/' + name
        SLClient.save_loop(file, loop_number=loop)
        time.sleep(2)
        WavSlicer.slice_and_send(name, file)

    @classmethod
    def publish_selected_changes(cls):
        loop = cls.get_selected_loop()
        name = cls.loop_index.get(loop, None)
        if name is None:
            print(f'{name} is not in {cls.loop_index}')
            return
        changes = cls.changes.get(name, None)
        if changes is None:
            print(f'No changes for {loop} in {cls.changes}')
        else:
            print(f'Sending changes {changes} for {name}')
            WavSlicer.send_changes(changes, name=name)

    @classmethod
    def publish_global_changes(cls):
        WavSlicer.send_changes(cls.global_changes)

    @classmethod
    def publish_all_changes(cls):
        if cls.changes:
            print('Sending changes ')
            WavSlicer.send_changes(cls.changes)

    @classmethod
    def set_sync_source(cls):
        selected = cls.get_selected_loop()
        SLClient.set_sync_source(selected + 1)
        cls.global_changes['sync_source'] = selected

    @classmethod
    def loop_reverse(cls):
        loop = cls.get_selected_loop()
        name = cls._get_selected_loop_name(loop)
        SLClient.reverse(loop)
        if cls.changes.get(name, None) is None:
            cls.changes[name] = {'reverse': 1}
        else:
            if cls.changes[name]['reverse'] == 0:
                cls.changes[name]['reverse'] = 1
            if cls.changes[name]['reverse'] == 1:
                cls.changes[name]['reverse'] = 0

    @classmethod
    def loop_rate(cls, rate):
        loop = cls.get_selected_loop()
        name = cls._get_selected_loop_name(loop)
        SLClient.set_rate(rate, loop)
        if cls.changes.get(name, None) is None:
            cls.changes[name] = {}
        cls.changes[name] = {'rate': rate}

    @classmethod
    def loop_add(cls):
        SLClient.loop_add()
        name = TTTruck._generate_name()
        new_loop_number = cls.get_number_of_loops()
        if cls.loop_index.get(new_loop_number, None) is not None:
            print(f'loop index is broken! loops = {new_loop_number} index = {cls.loop_index}')
        cls.loop_index[new_loop_number] = name
        cls.select_loop(new_loop_number)
        if new_loop_number == 0:
            SLClient.set_sync_source(-3)
            SLClient.set_quantize(1, new_loop_number)
        else:
            SLClient.set_sync_source(SLClient.sync_source)
            SLClient.set_quantize(SLClient.quantize_on, new_loop_number)
        SLClient.set_sync(1, new_loop_number)
        SLClient.set_playback_sync(1, new_loop_number)
        SLClient.set_mute_quantized(1, new_loop_number)
        return new_loop_number

    @classmethod
    def loop_load(cls, name):
        existing = cls._index_contains(name)
        if existing:
            loop = existing
        else:
            loop = cls.loop_add()
        SLClient.load_loop(loop, cls.loop_dir + '/' + name + '.wav')
        if SLClient.get_state(loop) != 'Playing':
            SLClient.pause(loop)

    @classmethod
    def callback(cls, x, y, z):
        try:
            getattr(TTTruck, y)(z)
        except Exception as e:
            print(e)

    @classmethod
    def select_loop(cls, loop_num):
        cls._unregister_loop_updates(SLClient.selected_loop)
        SLClient.set_selected_loop_num(loop_num)
        cls._register_loop_updates(loop_num)

    @classmethod
    def select_next_loop(cls):
        selected = cls.get_selected_loop()
        num_loops = cls.get_number_of_loops()
        if selected < num_loops:
            cls.select_loop(selected + 1)
        else:
            cls.select_loop(0)

    @classmethod
    def _register_loop_updates(cls, loop):
        SLClient.register_auto_update('loop_pos', '/test', loop, interval=100)
        # SLClient.register_auto_update('cycle_len', '/test', interval=1, loop_number=cls.loops)
        # SLClient.register_auto_update('free_time', '/test', interval=1, loop_number=cls.loops)
        # SLClient.register_auto_update('total_time', '/test', interval=1, loop_number=cls.loops)
        # SLClient.register_auto_update('waiting', '/test', interval=1, loop_number=cls.loops)
        SLClient.register_auto_update('state', '/state', loop)
        # SLClient.register_auto_update('next_state', '/test', interval=1, loop_number=cls.loops)
        SLClient.register_auto_update('save_loop', '/test', loop)
        SLClient.register_auto_update('load_loop', '/test', loop)

    @classmethod
    def _unregister_loop_updates(cls, loop):
        SLClient.unregister_auto_update('loop_pos', '/test', loop)
        # SLClient.register_auto_update('cycle_len', '/test', interval=1, loop_number=cls.loops)
        # SLClient.register_auto_update('free_time', '/test', interval=1, loop_number=cls.loops)
        # SLClient.register_auto_update('total_time', '/test', interval=1, loop_number=cls.loops)
        # SLClient.register_auto_update('waiting', '/test', interval=1, loop_number=cls.loops)
        SLClient.unregister_auto_update('state', '/test', loop)
        # SLClient.register_auto_update('next_state', '/test', interval=1, loop_number=cls.loops)
        SLClient.unregister_auto_update('save_loop', '/test', loop)
        SLClient.unregister_auto_update('load_loop', '/test', loop)

    @classmethod
    def _index_contains(cls, name):
        print(cls.loop_index)
        for k, v in cls.loop_index.items():
            print(k, v)
            if v == name:
                return k
        return False

    @classmethod
    def _update_loop_index(cls, loop_number):
        updated = {}
        for loop_index, loop_name in cls.loop_index.items():
            if loop_index >= loop_number - 1 and loop_index > 0:
                updated[loop_index - 1] = loop_name
            elif loop_index <= loop_number:
                updated[loop_index] = loop_name
            else:
                raise Exception(
                    f"loop index is broken! Index: {loop_index}, Name: {loop_name} , clsIndex: {cls.loop_index}")
        return updated

    @classmethod
    def _delete_all_loops(cls):
        num_loops = cls.get_number_of_loops()
        while num_loops >= 0:
            SLClient.set_selected_loop_num(0)
            cls.delete_loop()

    @classmethod
    def _get_selected_loop_name(cls, loop_number):
        try:
            name = cls.loop_index[loop_number]
            return name
        except KeyError:
            print(f'{loop_number} is not in the index: {cls.loop_index}')

    @staticmethod
    def _generate_name():
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))

    @classmethod
    def _write_wav(cls, wav):
        name = wav[0]
        bytes = b''.join(wav[1])
        with open(cls.loop_dir + '/' + name + '.wav', 'wb+') as f:
            f.write(bytes)
        TTTruck.loop_load(name)
