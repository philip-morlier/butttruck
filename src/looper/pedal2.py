import argparse
import random

from tkinter import *
from tkinter.ttk import Progressbar

from src.application import BuTTTruck
from src.looper.sl_client import SLClient
from src.looper.tttruck import TTTruck
from src.udp.peers import PeerClient

root = Tk()
root.geometry("625x100")
root.resizable(0, 0)
app = Frame(master=root, width=600, height=100, bg='black')

config = argparse.Namespace()
config.peers = '192.168.0.16:1111'
config.sooperlooper_host = None
config.sooperlooper_port = None
config.server_host = None
config.server_port = None

state = 0


# Button states:
def set_loop():
    b1.set("Record")
    b2.set("Overdub")
    b3.set("Add")
    b4.set("Delete")
    b5.set("Undo")
    b6.set("Redo")


def set_edit():
    b1.set("Reverse")
    b2.set("Multiply")
    b3.set("Stretch")
    b4.set("Delay")
    b5.set("Rate")
    b6.set("Solo")


def set_global_edit():
    b1.set("Sync")
    b2.set("Quant")
    b3.set("Tempo")
    b4.set("Delete")
    b5.set("???")
    b6.set("???")


def set_TTTruck():
    b1.set("Publish")
    b2.set("Selected")
    b3.set("All")
    b4.set("Global")
    b5.set("Next")
    b6.set("Prev")


# Modal button
def change_mode():
    # BuTTTruck.exit()
    # exit()
    global state
    if state == 0:
        state = 1
        set_edit()
        mode_indicator("yellow")
    elif state == 1:
        state = 2
        set_global_edit()
        mode_indicator("orange")
    elif state == 2:
        state = 3
        set_TTTruck()
        mode_indicator("red")
    else:
        set_loop()
        state = 0
        mode_indicator("blue")
    app.update()


# Mock LEDs
def indicator1():
    if loop_state_led.cget('bg') == 'red':
        loop_state_led.config(bg="green")
    else:
        loop_state_led.config(bg="red")


def solo_indicator():
    if solo_led.cget('bg') == 'gray':
        solo_led.config(bg="red")
    else:
        solo_led.config(bg="gray")


def mode_indicator(color):
    mode_led.config(bg=color)


def btn1_action():
    if state == 0:
        indicator1()
        TTTruck.loop_record()
    elif state == 1:
        TTTruck.loop_reverse()
    elif state == 2:
        TTTruck.set_sync_source()
    elif state == 3:
        TTTruck.publish_loop()


def btn2_action():
    if state == 0:
        TTTruck.loop_overdub()
    elif state == 1:
        TTTruck.loop_multiply()
    elif state == 2:
        TTTruck.set_quantize()
    elif state == 3:
        TTTruck.publish_selected_changes()


def btn3_action():
    if state == 0:
        TTTruck.loop_add()
    elif state == 1:
        # TTTruck.stretch
        pass
    elif state == 2:
        # TTTruck.set_tempo()
        pass
    elif state == 3:
        TTTruck.publish_all_changes()


def btn4_action():
    if state == 0:
        TTTruck.delete_loop()
    elif state == 1:
        # TTTruck.delay()
        pass
    elif state == 2:
        # TTTruck.delete()
        pass
    elif state == 3:
        TTTruck.publish_global_changes()


def btn5_action():
    if state == 0:
        TTTruck.undo()
    elif state == 1:
        TTTruck.loop_rate(random.random() * 4)
    elif state == 2:
        pass
    elif state == 3:
        pass


def btn6_action():
    if state == 0:
        TTTruck.redo()
    elif state == 1:
        TTTruck.solo()
    elif state == 2:
        TTTruck.select_next_loop()
    elif state == 3:
        TTTruck.select_prev_loop()


def publish():
    TTTruck.publish_loop()


def next_loop():
    TTTruck.select_next_loop()


# Setup window frame
app.rowconfigure(0, weight=1)
app.rowconfigure(1, weight=3)
app.rowconfigure(2, weight=3)

# Configure dynamic buttons
b1 = StringVar(value="Record")
b2 = StringVar(value="Overdub")
b3 = StringVar(value="Add")
b4 = StringVar(value="Delete")
b5 = StringVar(value="Undo")
b6 = StringVar(value="Redo")

btn1 = Button(textvariable=b1, command=btn1_action, width=4)
btn2 = Button(textvariable=b2, command=btn2_action, width=4)
btn3 = Button(textvariable=b3, command=btn3_action, width=4)
btn4 = Button(textvariable=b4, command=btn4_action, width=4)
btn5 = Button(textvariable=b5, command=btn5_action, width=4)
btn6 = Button(textvariable=b6, command=btn6_action, width=4)

btn1.grid(row=1, column=0, sticky=E, padx=5, pady=5)
btn2.grid(row=1, column=1, sticky=E, padx=5, pady=5)
btn3.grid(row=1, column=2, sticky=E, padx=5, pady=5)
btn4.grid(row=1, column=3, sticky=E, padx=5, pady=5)
btn5.grid(row=1, column=5, sticky=E, padx=5, pady=5)
btn6.grid(row=1, column=6, sticky=E, padx=5, pady=5)

# Static Buttons
next_loop_button = Button(text="Next", command=TTTruck.select_next_loop)
previous_loop_button = Button(text="Prev", command=TTTruck.select_prev_loop)


def solo():
    solo_indicator()
    TTTruck.solo()


# solo_button = Button(text="Solo", command=solo)
mode_button = Button(text="Mode", command=change_mode)

# next_loop_button.grid(row=1, column=5, sticky=E, padx=5, pady=5)
# previous_loop_button.grid(row=1, column=6, sticky=E, padx=5, pady=5)
# solo_button.grid(row=1, column=7, sticky=E, padx=5, pady=5)
mode_button.grid(row=1, column=8, sticky=E, padx=5, pady=5)

# Progressbar for loop position
cycle = DoubleVar()
loop_pos = Progressbar(root, orient='horizontal', mode='determinate', length=200, maximum=1)
loop_pos.grid(row=0, column=1, columnspan=4, sticky=W)

# LEDs
loop_state_led = Label(text='O', bg="green")
loop_state_led.grid(column=0, row=0)

solo_led = Label(text='O', bg="gray")
solo_led.grid(column=6, row=0)

loop_count = Label(text='', bg="gray")
loop_count.grid(column=4, row=0)

loop_num = Label(text='', bg="gray")
loop_num.grid(column=5, row=0)

mode_led = Label(text='O', bg="red")
mode_led.grid(column=8, row=0)


def connect():
    ip, port = e.get().split(':')
    print(server.get())
    PeerClient.add_peer((ip, int(port)), server=server.get())


server = BooleanVar()
check = Checkbutton(root, text='Server?', variable=server, onvalue=True, offvalue=False)
check.grid(column=0, row=2)

e = Entry()
e.insert(0, "Enter ip:port")
e.grid(column=2, columnspan=4, row=2, sticky=W)

c = Button(text='connect', command=connect)
c.grid(column=4, row=2, sticky=W)


def update():
    # SLClient.get_cycle_len(-3)
    cycle.set(SLClient.cycle_len)
    loop_count['text'] = SLClient.selected_loop
    loop_num['text'] = SLClient.loops
    len = cycle.get()
    if len:
        loop_pos['maximum'] = len
    loop_pos['value'] = SLClient.loop_pos
    root.update_idletasks()
    app.after(10, update)


def close():
    BuTTTruck.exit()
    root.destroy()


spacer = Label(text="   ")
spacer.grid(row=1, column=4, sticky=E, padx=5, pady=5)

root.protocol("WM_DELETE_WINDOW", close)

if __name__ == '__main__':
    BuTTTruck.main(config=config)
    app.after(10, update)
    app.mainloop()
