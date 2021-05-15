

from prompt_toolkit import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Layout

from src.looper.sl_client import SLClient
from src.looper.tttruck import TTTruck
from src.osc.osc_client import OSCClient

kb = KeyBindings()

from concurrent.futures import ThreadPoolExecutor
executor = ThreadPoolExecutor(max_workers=5)
executor.submit(OSCClient.start(debug=True))

@kb.add('c-q')
def exit_(event):
    """
    Pressing Ctrl-Q will exit the user interface.

    Setting a return value means: quit the event loop that drives the user
    interface and return this value from the `Application.run()` call.
    """
    executor.shutdown(False)
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

app = Application(key_bindings=kb, full_screen=True)
app.run()
