class OSCClient():
    def sends_message(self, message, args=None):
        pass


class OSCServer():
    def __init__(self):
        self.url = None


class SLClient():
    def __init__(self):
        self.osc_server = OSCServer()
        self.osc_client = OSCClient()

    def ping(self):
        """"PING Engine

 /ping s:return_url s:return_path

 If engine is there, it will respond with to the given URL and PATH
  with an OSC message with arguments:
     s:hosturl  s:version  i:loopcount
"""
        self.osc_client.sends_message('/ping', [self.osc_server.url, '/pingrecieved'])

    def hit(self, loop_number, command):
        """""/sl/#/hit s:cmdname
  A single hit only, no press-release action"""

        self.osc_client.sends_message(f'/sl/{loop_number}/hit', command)

    def record(self, loop_number=-3):
        self.hit(loop_number, 'record')

    def overdub(self, loop_number=-3):
        self.hit(loop_number, 'overdub')

    def multiply(self, loop_number=-3):
        self.hit(loop_number, 'multiply')

    def insert(self, loop_number=-3):
        self.hit(loop_number, 'insert')

    def replace(self, loop_number=-3):
        self.hit(loop_number, 'replace')

    def reverse(self, loop_number=-3):
        self.hit(loop_number, 'reverse')

    def mute(self, loop_number=-3):
        self.hit(loop_number, 'mute')

    def undo(self, loop_number=-3):
        self.hit(loop_number, 'undo')

    def redo(self, loop_number=-3):
        self.hit(loop_number, 'redo')

    def oneshot(self, loop_number=3):
        self.hit(loop_number, 'oneshot')

    def trigger(self, loop_number=-3):
        self.hit(loop_number, 'trigger')
        # substitute
        # undo_all
        # redo_all
        # mute_on
        # mute_off
        # solo
        # pause
        # solo_next
        # solo_prev
        # record_solo
        # record_solo_next
        # record_solo_prev
        # set_sync_pos
        # reset_sync_pos
