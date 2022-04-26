import tempfile
import time

from src.udp.wav_slicer import WavSlicer
from src.looper.sl_client import SLClient

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

    def set_sync_time(self, t):
        self.sync_time = t

    def set_cycle_len(self, l):
        self.cycle_len = l

    def publish(self):
        print(self.wav_file)
        SLClient.save_loop(self.wav_file, loop_number=1)
        self.cycle_length = SLClient.cycle_len
        loop_position = SLClient.loop_pos
        main_loop_pos = SLClient.get_loop_pos(0)
        print(SLClient.main_loop_pos)
        print(main_loop_pos)
        print(SLClient.loop_pos)

        #print('Publishing loop of length and pos: ', cycle_length, loop_position)
        #next_cycle_length_time = ((cycle_length  - loop_position) + global_time)
        time.sleep(2)
        WavSlicer.slice_and_send(self.name, self.sync_time, file=self.wav_file)

    def load_loop(self):
        SLClient.load_loop(self.wav_file)
        #TODO: Schedule playback
        if self.state != 'Playing':
            SLClient.pause(-3)
