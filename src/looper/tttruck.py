import logging
import random
import string
import tempfile
import time

from src.looper.sl_client import SLClient
from src.looper.loop import Loop
from src.udp.wav_slicer import WavSlicer


class TTTruck:
    #loop_dir = tempfile.mkdtemp()
    loop_index = {}
    global_changes = {}
    selected_loop_num = -1

    @classmethod
    def loop_record(cls):
        loop = cls._get_loop().record()

    @classmethod
    def loop_overdub(cls):
        cls._get_loop().overdub()

    @classmethod
    def delete_loop(cls):
        if cls.get_number_of_loops() == 1:
            return
        SLClient.loop_del(cls.selected_loop_num)
        if cls.loop_index.get(selected, None) is None:
            logging.warning(
                f'Unable to delete loop, index is broken! selected_loop = {selected} index = {cls.loop_index}')
        else:
            cls.loop_index.pop(selected)
        loop_number = cls.get_number_of_loops()
        cls.loop_index = cls._update_loop_index(loop_number)

    @classmethod
    def get_number_of_loops(cls):
        return SLClient.ping()

    @classmethod
    def get_selected_loop_num(cls):
        return SLClient.get_selected_loop_num()

    @classmethod
    def publish_loop(cls):
        loop = cls._get_loop()
        SLClient.save_loop(loop.wav_file)
        time.sleep(2)
        WavSlicer.send_new_loop_message(loop)

    @classmethod
    def publish_selected_changes(cls):
        #loop = cls.loop_index.get(cls.selected_loop_num, None)
        loop = cls._get_loop()
        if loop is None:
            logging.warning(f'Unable to publish changes. Loop doesnt exist')
            return
        if loop.changes:
            logging.debug(f'Sending changes {loop.changes} for {loop.name}')
            WavSlicer.send_changes(loop.changes, name=loop.name)
        else:
            logging.debug(f'{loop.name} has no changes to publish.')


    # @classmethod
    # def publish_global_changes(cls):
    #     WavSlicer.send_changes(cls.global_changes)

    # @classmethod
    # def publish_all_changes(cls):
    #     if cls.changes:
    #         logging.debug(f'Publishing all changes: {cls.changes}')
    #         WavSlicer.send_changes(cls.changes)

    @classmethod
    def set_sync_source(cls):
        n =  cls.global_changes.get('sync_source', 0)
        if n >= cls.get_number_of_loops():
            n = -3
        else:
            n += 1
        SLClient.set_sync_source(n)
        cls.global_changes['sync_source'] = n

    @classmethod
    def loop_reverse(cls):
        cls._get_loop().reverse()

    @classmethod
    def loop_rate(cls, rate):
        loop = cls._get_loop()
        loop.set_rate(rate)

    @classmethod
    def add_main_loop(cls):
        SLClient.loop_add()
        loop = Loop('main')
        cls.loop_index[0] = loop

        # SLClient.register_auto_update('state', '/state', 0)
        # SLClient.set_selected_loop_num(0)
        # SLClient.set_sync_source(-3)
        # SLClient.set_tempo(30)

        # SLClient.set_sync(1, 0)
        # SLClient.set_quantize(2, 0)
        # SLClient.set_input_gain(0, 0)
        # time.sleep(2)

        # SLClient.record(0)
        # while loop.state.startswith('Wait'):
        #     time.sleep(0.1)
        # SLClient.record(0)
        import os
        f = os.path.split(__file__)[0] + '/cycle_1s.wav'
        SLClient.load_loop(f, 0)
        SLClient.pause(0)

    @classmethod
    def loop_add(cls, name=None):
        SLClient.loop_add()
        name = name if name is not None else cls._generate_name()
        loop = Loop(name)
        new_loop_number = cls.get_number_of_loops()
        cls.loop_index[new_loop_number] = loop
        cls.select_loop(new_loop_number)
        if new_loop_number == 1:
            # FIXME: hack to make the register_auto_updates work on first loop.
            time.sleep(0.5)
        return loop, new_loop_number

    @classmethod
    def loop_load(cls, name, sync_time):
        loop, loop_number = cls._get_loop_by_name(name)
        if loop_number:
            SLClient.set_selected_loop_num(loop_number)
        else:
            loop, loop_number = cls.loop_add(name=name)
        loop.set_sync_time(sync_time)
        loop.load_loop(loop_number)


    @classmethod
    def _get_loop_by_name(cls, loop_name):
        for idx, loop in cls.loop_index.items():
            if loop.name == loop_name:
                return cls.loop_index[idx], idx
        return None, None

    @classmethod
    def select_loop(cls, loop_num):
        if loop_num == 0:
            print("First loop is unavailable")
        elif loop_num == cls.selected_loop_num:
            print('already selected')
        else:
            cls._unregister_loop_updates(cls.selected_loop_num)
            SLClient.set_selected_loop_num(loop_num)
            cls._register_loop_updates(loop_num)
            SLClient.get_cycle_len(loop_num)
            SLClient.get_state(loop_num)

    @classmethod
    def select_next_loop(cls):
#        selected = cls.get_selected_loop_num()
        num_loops = cls.get_number_of_loops()
        if cls.selected_loop_num < num_loops:
            cls.select_loop(cls.selected_loop_num + 1)
        else:
            cls.select_loop(1)

    @classmethod
    def select_prev_loop(cls):
        num_loops = cls.get_number_of_loops()
        if cls.selected_loop_num >= 2 :
            cls.select_loop(cls.selected_loop_num - 1)
        else:
            cls.select_loop(num_loops)

    @classmethod
    def _get_loop(cls):
        return cls._get_loop_by_idx(cls.selected_loop_num)

    @classmethod
    def solo(cls):
        SLClient.solo(cls.selected_loop_num)

    @classmethod
    def get_main_loop_pos(cls):
        return SLClient.get_loop_pos(0)

    @classmethod
    def _register_loop_updates(cls, loop):
        SLClient.register_auto_update('loop_pos', '/loop_pos', loop, interval=100)
        #SLClient.register_auto_update('cycle_len', '/test', loop, interval=100)
        # SLClient.register_auto_update('free_time', '/test', interval=1, loop_number=cls.loops)
        SLClient.register_auto_update('total_time', '/test', loop)
        # SLClient.register_auto_update('waiting', '/test', interval=1, loop_number=cls.loops)
        SLClient.register_auto_update('state', '/state', loop)
        # SLClient.register_auto_update('next_state', '/test', interval=1, loop_number=cls.loops)
        SLClient.register_auto_update('save_loop', '/test', loop)
        SLClient.register_auto_update('load_loop', '/test', loop)

    @classmethod
    def _unregister_loop_updates(cls, loop):
        SLClient.unregister_auto_update('loop_pos', '/loop_pos', loop)
        #SLClient.unregister_auto_update('cycle_len', '/test', loop)
        # SLClient.register_auto_update('free_time', '/test', interval=1, loop_number=cls.loops)
        # SLClient.register_auto_update('total_time', '/test', interval=1, loop_number=cls.loops)
        # SLClient.register_auto_update('waiting', '/test', interval=1, loop_number=cls.loops)
        SLClient.unregister_auto_update('state', '/test', loop)
        # SLClient.register_auto_update('next_state', '/test', interval=1, loop_number=cls.loops)
        SLClient.unregister_auto_update('save_loop', '/test', loop)
        SLClient.unregister_auto_update('load_loop', '/test', loop)


    @classmethod
    def _update_loop_index(cls, loop_number):
        updated = {}
        for loop_index, loop in cls.loop_index.items():
            if loop_index >= loop_number - 1 and loop_index > 0:
                updated[loop_index - 1] = loop
            elif loop_index <= loop_number:
                updated[loop_index] = loop
            else:
                raise Exception(
                    f"loop index is broken! Index: {loop_index}, Name: {loop_name} , clsIndex: {cls.loop_index}")
        return updated

    @classmethod
    def _delete_all_loops(cls):
        num_loops = cls.get_number_of_loops()
        while num_loops >= 1:
            SLClient.set_selected_loop_num(1)
            cls.delete_loop()
            num_loops -= 1

    @classmethod
    def _get_loop_by_idx(cls, idx):
        try:
            return cls.loop_index[idx]
        except KeyError:
            logging.warning(f'{idx} is not in the index: {cls.loop_index}')

    @classmethod
    def _get_loop_number(cls, loop_name):
        for idx, loop in cls.loop_index.items():
            if loop.name == loop_name:
                return idx
        logging.warning(f'{loop_name} is not in the index: {cls.loop_index}')

    @staticmethod
    def _generate_name():
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))

    @classmethod
    def add_remote_loop(cls, name, msg):
        wav_bytes = b''.join(msg['chunks'])
        sync_time = msg['sync_time']
        with open(Loop.loop_dir + '/' + name + '.wav', 'wb+') as f:
            f.write(wav_bytes)
            logging.debug(f'Wrote file: {f}')
        cls.loop_load(name, sync_time)

    @classmethod
    def undo(cls):
        cls._get_loop().undo()

    @classmethod
    def loop_multiply(cls):
        cls._get_loop().multiply()

    @classmethod
    def set_quantize(cls):
        cls._get_loop().quantize()

    @classmethod
    def redo(cls):
        cls._get_loop().redo()
