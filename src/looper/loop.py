import tempfile
import time
import logging

from src.looper.sl_client import SLClient
#from src.udp.wav_slicer import WavSlicer

class Loop:
    loop_dir = tempfile.mkdtemp()

    def __init__(self, name, sync_time=0, cycle_length=0):
        self.name = name
        self.sync_time = sync_time
        self.cycle_length = cycle_length
        self.changes = {}
        self.published = False
        self.wav_file = self.loop_dir + '/' + name + '.wav'
        self.state = 'Unkown'
        self.parameters = {}

    def set_sync_time(self, t):
        self.sync_time = t

    def set_cycle_len(self, l):
        self.cycle_length = l
        print(self.name, self.cycle_length, self.sync_time)

    def record(self):
        if self.state != SLClient.states[2]:
            start = SLClient.get_loop_pos(0)
            SLClient.record()
            end = SLClient.get_loop_pos(0)
            diff = end - start
            self.sync_time = start + (diff / 2)
        else:
            SLClient.record()


    def overdub(self):
        SLClient.overdub()


    def reverse(self):
        SLClient.reverse()
        self._update_changes('reverse')

    def set_rate(self, rate):
        SLClient.set_rate(rate)
        self._update_changes('rate', rate)

    def undo(self):
        SLClient.undo()

    def redo(self):
        SLClient.redo()

    def multiply(self):
        SLClient.multiply()

    def quantize(self):
        #if SLClient.quantize_on == 3:
        print(self.changes)
        SLClient.set_quantize(0) if SLClient.quantize_on == 3.0 else SLClient.set_quantize(SLClient.quantize_on + 1)
    def load_loop(self, loop_number):
        SLClient.load_loop(self.wav_file, loop_number)
        #TODO: Schedule playback
        if self.state == 4:
            SLClient.pause()
        x = SLClient.get_cycle_len()

        # t = point in my loop0 I began
        # x = decimal of my cycle_length
        # y = whole of my cycle_length
        # z = current point your loop0
        # p = next nearest start point

        from math import modf
        x, y = modf(self.cycle_length)
        z = SLClient.main_loop_pos
        if self.sync_time > z:
            p = y + self.sync_time - z
        else:
            p = y + (1 + self.sync_time) - z
        #p = y + (x + (1 - t))
        SLClient.scheduled_tasks.enter(p, 1, SLClient.pause(loop_number))


    def _update_changes(self, parameter, value=None):
        if self.changes.get(parameter, None) is None:
            self.changes[parameter] = 1 if value == None else value
        else:
            if value is None:
                self.changes[parameter] = 0 if self.changes[parameter] == 1 else 1
            else:
                self.changes[parameter] = value
