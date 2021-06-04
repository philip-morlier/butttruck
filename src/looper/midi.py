import mido
from src.looper.tttruck import TTTruck

# map the inputs to the function blocks
options = {60: TTTruck.loop_record,
           61: TTTruck.loop_add,
           62: TTTruck.delete_loop,
           63: TTTruck.loop_reverse,

           70: TTTruck.select_next_loop,
           73: TTTruck.publish_loop}


def run():
    mido.set_backend('mido.backends.rtmidi')
    with mido.open_input() as inport:
        for msg in inport.iter_pending():
            if msg.type == 'note_on':
                options[msg.note]()

if __name__ == '__main__':
    run()
