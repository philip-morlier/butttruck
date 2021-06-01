

from prompt_toolkit import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Layout

from src.looper.sl_client import SLClient
from src.looper.tttruck import TTTruck
from src.osc.osc_client import OSCClient

from src.application import BuTTTruck
from src.udp.wav_slicer import WavSlicer

kb = KeyBindings()

TTT = BuTTTruck()
TTT.main()

@kb.add('c-q')
def exit_(event):
    """
    Pressing Ctrl-Q will exit the user interface.

    Setting a return value means: quit the event loop that drives the user
    interface and return this value from the `Application.run()` call.
    """
    event.app.exit()

@kb.add('r')
def _(event):
    SLClient.record()

@kb.add('n')
def _(event):
    TTTruck.new_loop()

@kb.add('p')
def _(event):
    TTTruck.publish_loop()

@kb.add('z')
def _(event):
    TTTruck.loop_reverse()

@kb.add('j')
def _(event):
    TTTruck.new_remote_loop()

@kb.add('q')
def _(event):
    WavSlicer.slice_and_send('/home/Philip/Desktop/tttruck_loop/butttruck/src/udp/test1.wav', 'sakjsalkdjflds')



app = Application(key_bindings=kb, full_screen=True)
app.run()
