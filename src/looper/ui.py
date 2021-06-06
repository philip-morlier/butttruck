import random

from prompt_toolkit import Application
from prompt_toolkit.key_binding import KeyBindings

from src.looper.sl_client import SLClient
from src.looper.tttruck import TTTruck

from src.application import BuTTTruck

kb = KeyBindings()

@kb.add('c-q')
def exit_(event):
    """
    Pressing Ctrl-Q will exit the user interface.

    Setting a return value means: quit the event loop that drives the user
    interface and return this value from the `Application.run()` call.
    """
    BuTTTruck.exit()
    event.app.exit()

@kb.add('r')
def _(event):
    TTTruck.loop_record()

@kb.add('c-r')
def _(event):
    TTTruck.loop_rate(random.random() * 4)

@kb.add('n')
def _(event):
    TTTruck.select_next_loop()

@kb.add('c-p')
def _(event):
    SLClient.ping()

@kb.add('c-d')
def _(event):
    TTTruck.delete_loop()

@kb.add('c-n')
def _(event):
    TTTruck.loop_add()

@kb.add('p')
def _(event):
    TTTruck.publish_loop()

@kb.add('c')
def _(event):
    TTTruck.publish_all_changes()

@kb.add('c-s')
def _(event):
    TTTruck.set_sync_source()

@kb.add('c-c')
def _(event):
    TTTruck.publish_selected_changes()

@kb.add('z')
def _(event):
    TTTruck.loop_reverse()

@kb.add('c-z')
def _(event):
    #/tmp/tmpho4iedf1/tq21alez3ne04s1oago7.wav
    TTTruck.loop_load('tq21alez3ne04s1oago7')

app = Application(key_bindings=kb, full_screen=True)
BuTTTruck.main()
app.run()
