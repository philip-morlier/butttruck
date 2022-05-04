import logging
import random
import string
import tempfile
import time
from sched import scheduler

from src.looper.sl_client import SLClient
from src.looper.loop import Loop
from src.udp.peers import PeerClient
from src.udp.wav_slicer import WavSlicer

class TTTruck:
    #loop_dir = tempfile.mkdtemp()
    loop_index = {}
    loop_parameters = {}
    changes = {}
    global_changes = {}
    scheduled_tasks = scheduler(time.time, time.sleep)

    @classmethod
    def loop_record(cls):
        loop = cls._get_selected_loop(cls.get_selected_loop_num())
        start = cls.get_main_loop_pos()
        SLClient.record()
        end = cls.get_main_loop_pos()
        diff = end - start
        if loop.state != SLClient.states[2]:
            loop.sync_time = start + (diff / 2)

    @classmethod
    def loop_overdub(cls):
        loop = cls.get_selected_loop_num()
        SLClient.overdub(loop)

    @classmethod
    def delete_loop(cls):
        if cls.get_number_of_loops() == 0:
            return
        selected = cls.get_selected_loop_num()

        SLClient.loop_del(selected)
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
        loop_number = cls.get_selected_loop_num()
        loop = cls._get_selected_loop(loop_number)
        loop.publish()

    @classmethod
    def publish_selected_changes(cls):
        loop_num = cls.get_selected_loop_num()
        loop = cls.loop_index.get(loop_num, None)
        if loop is None:
            logging.warning(f'Unable to publish changes. Loop doesnt exist')
            return
        if loop.changes:
            logging.debug(f'Sending changes {changes} for {name}')
            WavSlicer.send_changes(loop.changes, name=loop.name)
        else:
            logging.debug(f'{loop.name} has no changes to publish. {cls.loop_index}')

    @classmethod
    def publish_global_changes(cls):
        WavSlicer.send_changes(cls.global_changes)

    @classmethod
    def publish_all_changes(cls):
        if cls.changes:
            logging.debug(f'Publishing all changes: {cls.changes}')
            WavSlicer.send_changes(cls.changes)

    @classmethod
    def set_sync_source(cls):
        selected = cls.get_selected_loop_num()
        SLClient.set_sync_source(selected + 1)
        cls.global_changes['sync_source'] = selected

    @classmethod
    def loop_reverse(cls):
        loop_num = cls.get_selected_loop_num()
        loop = cls._get_selected_loop(loop_num)
        SLClient.reverse(loop_num)
        if loop.changes.get('reverse', None) is None:
            loop.changes['reverse'] = 1
        else:
            loop.changes['reverse'] = 0 if loop.changes['reverse'] == 1 else 1

    @classmethod
    def loop_rate(cls, rate):
        loop_num = cls.get_selected_loop_num()
        loop = cls._get_selected_loop_name(loop_num)
        SLClient.set_rate(rate, loop)
        if loop.changes[name].get('rate', None) is None:
            loop.changes[name][rate] = rate
        loop.changes[name]['rate'] = rate

    @classmethod
    def add_main_loop(cls):
        SLClient.loop_add()

        loop = Loop('main')
        cls.loop_index[0] = loop

        SLClient.set_selected_loop_num(0)
        SLClient.set_sync_source(-3)
        SLClient.set_tempo(30)
        SLClient.set_sync(1, 0)
        SLClient.set_quantize(2, 0)
        SLClient.register_auto_update('state', '/state', 0)

        SLClient.record()
        while loop.state.startswith('Wait'):
            time.sleep(0.5)

        SLClient.record()
        #FIXME: Why is this necessary???
        while loop.state.startswith('Wait'):
            time.sleep(0.5)

    @classmethod
    def loop_add(cls, name=None):
        SLClient.loop_add()
        name = name if name is not None else TTTruck._generate_name()
        loop = Loop(name)
        new_loop_number = cls.get_number_of_loops()
        cls.loop_index[new_loop_number] = loop
        #cls.changes[name] = {}
        cls.select_loop(new_loop_number)
        if new_loop_number == 1:
            # FIXME: hack to make the register_auto_updates work on first loop.
            time.sleep(0.5)

        #cls.select_loop(1)
            # TODO: do we want to set sync and quantize???
            # SLClient.set_sync_source(-3)
            # SLClient.set_quantize(2, new_loop_number)
        # else:
        #     SLClient.set_sync_source(SLClient.sync_source)
        #     SLClient.set_quantize(SLClient.quantize_on, new_loop_number)

        #SLClient.set_sync(1, new_loop_number)
        #SLClient.set_playback_sync(1, new_loop_number)

        return loop

    @classmethod
    def loop_load(cls, name, sync_time):
        existing = cls._index_contains(name)
        if existing:
            loop = existing
        else:
            loop = cls.loop_add()
        SLClient.load_loop(loop.wav_file)
        if SLClient.get_state() != 'Paused':
            SLClient.pause()


        # t = point in my loop0 I began
        # x = decimal of my cycle_length
        # y = whole of my cycle_length
        # z = current point your loop0
        # p = next nearest start point
        from math import modf
        #t = loop.sync_time
        x, y = modf(loop.cycle_length)
        z = SLClient.main_loop_pos
        if sync_time > z:
            p = y + sync_time - z
        else:
            p = y + (1+sync_time) - z
        #p = y + (x + (1 - t))
        cls.scheduled_tasks.enter(p, 1, SLClient.pause(SLClient.selected_loop))

    @classmethod
    def callback(cls, x, y, z):
        try:
            getattr(TTTruck, y)(z)
        except Exception as e:
            logging.warning(f'TTTruck callback failed: {e}')

    @classmethod
    def select_loop(cls, loop_num):
        if loop_num == 0:
            print("First loop is unavailable")
        elif loop_num == SLClient.selected_loop:
            print('already selected')
        else:
            cls._unregister_loop_updates(SLClient.selected_loop)
            SLClient.set_selected_loop_num(loop_num)
            cls._register_loop_updates(loop_num)
            SLClient.get_cycle_len(loop_num)
            SLClient.get_state(loop_num)

    @classmethod
    def select_next_loop(cls):
        selected = cls.get_selected_loop_num()
        num_loops = cls.get_number_of_loops()
        if selected < num_loops:
            cls.select_loop(selected + 1)
        else:
            cls.select_loop(1)

    @classmethod
    def select_prev_loop(cls):
        selected = cls.get_selected_loop_num()
        num_loops = cls.get_number_of_loops()
        if selected > 1:
            cls.select_loop(selected - 1)
        else:
            cls.select_loop(num_loops)

    @classmethod
    def solo(cls):
        SLClient.solo(cls.get_selected_loop_num())

    @classmethod
    def get_main_loop_pos(cls):
        return SLClient.get_loop_pos(0)
        #SLClient.register_auto_update('loop_pos', '/main_loop_pos', 0, interval=10)

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
    def _index_contains(cls, name):
        for k, v in cls.loop_index.items():
            if v.name == name:
                return v
        return False

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
        while num_loops >= 0:
            SLClient.set_selected_loop_num(0)
            cls.delete_loop()
            num_loops -= 1

    @classmethod
    def _get_selected_loop_name(cls, loop_number):
        try:
            return cls.loop_index[loop_number].name
        except KeyError:
            logging.warning(f'{loop_number} is not in the index: {cls.loop_index}')

    @classmethod
    def _get_selected_loop(cls, loop_number):
        try:
            return cls.loop_index[loop_number]
        except KeyError:
            logging.warning(f'{loop_number} is not in the index: {cls.loop_index}')

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
    def _write_wav(cls, name, msg):
        wav_bytes = b''.join(msg['chunks'])
        sync_time = msg['sync_time']
        #bytes = b''.join(wav_bytes)
        with open(Loop.loop_dir + '/' + name + '.wav', 'wb+') as f:
            f.write(wav_bytes)
            logging.debug(f'Wrote file: {f}')
        TTTruck.loop_load(name, sync_time)


    @classmethod
    def undo(cls):
        SLClient.undo(cls.get_selected_loop_num())

    @classmethod
    def loop_multiply(cls):
        SLClient.multiply(cls.get_selected_loop_num())

    @classmethod
    def set_quantize(cls):
        loop = cls.get_selected_loop()
        if SLClient.quantize_on == 3:
            SLClient.set_quantize(0, loop)
        else:
            SLClient.set_quantize(SLClient.quantize_on + 1, loop)

    @classmethod
    def set_parameter(cls, param, value,  loop_name=None):
        if loop_name is None:
            loop_number = cls.get_selected_loop_num()
        else:
            loop_number = cls._get_loop_number(loop_name)
        logging.debug(f'Setting {param} to {value} for {loop_number} {loop_name} ')
        SLClient.set_parameter([param, value], loop_number)

    @classmethod
    def redo(cls):
        SLClient.redo(cls.get_selected_loop_num())
