import threading
import time
from sched import scheduler

from src.osc.osc_client import OSCClient

return_url = 'localhost:9952'
timeout = 0.2


class SLClient:

    loops = -1
    selected_loop = 0
    cond = threading.Condition()
    cmd_evt = threading.Event()
    parameter_evt = threading.Event()
    global_evt = threading.Event()
    ping_evt = threading.Event()
    selection_evt = threading.Event()
    state_change = threading.Event()
    state = 'Unknown'
    sync_source = -3
    quantize_on = 2
    loop_pos = 0
    main_loop_pos = 0
    cycle_len = 0
    scheduled_tasks = scheduler(time.time, time.sleep)

    @staticmethod
    def ping():
        """"PING Engine
         /ping s:return_url s:return_path

         If engine is there, it will respond with to the given URL and PATH with an OSC message with arguments:
         s:hosturl  s:version  i:loopcount"""

        OSCClient.send_message('/ping', [return_url, '/pingrecieved'])
        SLClient.ping_evt.wait(timeout=timeout)
        return SLClient.loops

    @staticmethod
    def hit(command, loop=-3):
        """""/sl/#/hit s:cmdname
        A single hit only, no press-release action"""
        OSCClient.send_message(f'/sl/{loop}/hit', [command])
        SLClient.state_change.wait(timeout=timeout)
        return SLClient.state

    ##################################################################
    ### Loop commands and parameter gets/sets paths are all prefixed with:
    ###   /sl/#/   where # is the loop index starting from 0.
    ### Specifying -1 will apply the command or operation to all loops.
    ### Specifying -3 will apply the command or operation to the selected loop.
    ##################################################################

    @staticmethod
    def record(loop=-3):
        return SLClient.hit('record', loop)

    @staticmethod
    def overdub(loop=-3):
        return SLClient.hit('overdub', loop)

    @staticmethod
    def multiply(loop=-3):
        return SLClient.hit('multiply', loop)

    @staticmethod
    def insert(loop=-3):
        return SLClient.hit('insert', loop)


    @staticmethod
    def replace(loop=-3):
        return SLClient.hit('replace', loop)

    @staticmethod
    def reverse(loop=-3):
        return SLClient.hit('reverse', loop)

    @staticmethod
    def mute(loop=-3):
        return SLClient.hit('mute', loop)

    @staticmethod
    def undo(loop=-3):
        return SLClient.hit('undo', loop)

    @staticmethod
    def redo(loop=-3):
        return SLClient.hit('redo', loop)

    @staticmethod
    def oneshot(loop=-3):
        return SLClient.hit('oneshot', loop)

    @staticmethod
    def trigger(loop=-3):
        return SLClient.hit('trigger', loop)

    @staticmethod
    def substitute(loop=-3):
        return SLClient.hit('substitute', loop)

    @staticmethod
    def undo_all(loop=-3):
        return SLClient.hit('undo_all', loop)

    @staticmethod
    def redo_all(loop=-3):
        return SLClient.hit('redo_all', loop)

    @staticmethod
    def mute_on(loop=-3):
        return SLClient.hit('mute_on', loop)

    @staticmethod
    def mute_off(loop=-3):
        return SLClient.hit('mute_off', loop)

    @staticmethod
    def solo(loop=-3):
        return SLClient.hit('solo', loop)

    @staticmethod
    def pause(loop=-3):
        return SLClient.hit('pause', loop)

    @staticmethod
    def solo_next(loop=-3):
        return SLClient.hit('solo_next', loop)

    @staticmethod
    def solo_prev(loop=-3):
        return SLClient.hit('solo_prev', loop)

    @staticmethod
    def record_solo(loop=-3):
        return SLClient.hit('record_solo', loop)

    @staticmethod
    def record_solo_next(loop=-3):
        return SLClient.hit('record_solo_next', loop)

    @staticmethod
    def record_solo_prev(loop=-3):
        return SLClient.hit('record_solo_prev', loop)

    @staticmethod
    def set_sync_pos(loop=-3):
        return SLClient.hit('set_sync_pos', loop)

    @staticmethod
    def reset_sync_pos(loop=-3):
        return SLClient.hit('reset_sync_pos', loop)

    #######################################################
    # SET PARAMETER VALUES
    # /sl/#/set  s:control  f:value
    #   To set a parameter for a loop.
    #######################################################
    @staticmethod
    def set_parameter(value, loop=-3):
        OSCClient.send_message(f'/sl/{loop}/set', value)
        return SLClient.get_parameter(value[0], loop)

    @staticmethod
    def set_rec_thresh(value, loop=-3):
        """  rec_thresh  	:: expected range is 0 -> 1"""
        SLClient.set_parameter(['rec_thresh', value], loop)

    @staticmethod
    def set_feedback(value, loop=-3):
        """  feedback    	:: range 0 -> 1"""
        SLClient.set_parameter(['feedback', value], loop)

    @staticmethod
    def set_dry(value, loop=-3):
        """  dry         	:: range 0 -> 1"""
        SLClient.set_parameter(['dry', value], loop)

    @staticmethod
    def set_wet(value, loop=-3):
        """  wet         	:: range 0 -> 1"""
        SLClient.set_parameter(['wet', value], loop)

    @staticmethod
    def set_input_gain(value, loop=-3):
        """  input_gain    :: range 0 -> 1"""
        SLClient.set_parameter(['input_gain', value], loop)

    @staticmethod
    def set_rate(value, loop=-3):
        """  rate        	:: range 0.25 -> 4.0"""
        SLClient.set_parameter(['rate', value], loop)

    @staticmethod
    def set_scratch_pos(value, loop=-3):
        """  scratch_pos  	 :: 0 -> 1 """
        SLClient.set_parameter(['scratch_pos', value], loop)

    @staticmethod
    def set_delay_trigger(value, loop=-3):
        """  delay_trigger  :: any changes"""
        SLClient.set_parameter(['delay_trigger', value], loop)

    @staticmethod
    def set_quantize(value, loop=-3):
        """  quantize       :: 0 = off, 1 = cycle, 2 = 8th, 3 = loop"""
        SLClient.quantize_on = value
        return SLClient.set_parameter(['quantize', value], loop)

    @staticmethod
    def set_round(value, loop=-3):
        """  round          :: 0 = off,  not 0 = on """
        SLClient.set_parameter(['round', value], loop)

    @staticmethod
    def set_redo_is_tap(value, loop=-3):
        """  redo_is_tap    :: 0 = off,  not 0 = on """
        SLClient.set_parameter(['redo_is_tap', value], loop)

    @staticmethod
    def set_sync(value, loop=-3):
        """  sync           :: 0 = off,  not 0 = on """
        return SLClient.set_parameter(['sync', value], loop)

    @staticmethod
    def set_playback_sync(value, loop=-3):
        """  playback_sync  :: 0 = off,  not 0 = on """
        SLClient.set_parameter(['playback_sync', value], loop)

    @staticmethod
    def set_use_rate(value, loop=-3):
        """  use_rate       :: 0 = off,  not 0 = on """
        SLClient.set_parameter(['use_rate', value], loop)

    @staticmethod
    def set_fade_samples(value, loop=-3):
        """  fade_samples   :: 0 -> ..."""
        SLClient.set_parameter(['fade_samples', value], loop)

    @staticmethod
    def set_use_feedback_play(value, loop=-3):
        """  use_feedback_play   :: 0 = off,  not 0 = on"""
        SLClient.set_parameter(['use_feedback_play', value], loop)

    @staticmethod
    def set_use_common_ins(value, loop=-3):
        """  use_common_ins   :: 0 = off,  not 0 = on """
        SLClient.set_parameter(['use_common_ins', value], loop)

    @staticmethod
    def set_use_common_outs(value, loop=-3):
        """  use_common_outs   :: 0 = off,  not 0 = on """
        SLClient.set_parameter(['use_common_outs', value], loop)

    @staticmethod
    def set_relative_sync(value, loop=-3):
        """  relative_sync   :: 0 = off, not 0 = on"""
        SLClient.set_parameter(['relative_sync', value], loop)

    @staticmethod
    def set_use_safety_feedback(value, loop=-3):
        """  use_safety_feedback   :: 0 = off, not 0 = on"""
        SLClient.set_parameter(['use_safety_feedback', value], loop)

    @staticmethod
    def set_pan_1(value, loop=-3):
        """  pan_1         	:: range 0 -> 1"""
        SLClient.set_parameter(['pan_1', value], loop)

    @staticmethod
    def set_pan_2(value, loop=-3):
        """  pan_2         	:: range 0 -> 1"""
        SLClient.set_parameter(['pan_2', value], loop)

    @staticmethod
    def set_pan_3(value, loop=-3):
        """  pan_3         	:: range 0 -> 1"""
        SLClient.set_parameter(['pan_3', value], loop)

    @staticmethod
    def set_pan_4(value, loop=-3):
        """  pan_4         	:: range 0 -> 1"""
        SLClient.set_parameter(['pan_4', value], loop)

    @staticmethod
    def set_input_latency(value, loop=-3):
        """  input_latency :: range 0 -> ..."""
        SLClient.set_parameter(['input_latency', value], loop)

    @staticmethod
    def set_output_latency(value, loop=-3):
        """  output_latency :: range 0 -> ..."""
        SLClient.set_parameter(['output_latency', value], loop)

    @staticmethod
    def set_trigger_latency(value, loop=-3):
        """  trigger_latency :: range 0 -> ..."""
        SLClient.set_parameter(['trigger_latency', value], loop)

    @staticmethod
    def set_autoset_latency(value, loop=-3):
        """autoset_latency  :: 0 = off, not 0 = on"""
        SLClient.set_parameter(['autoset_latency', value], loop)

    @staticmethod
    def set_mute_quantized(value, loop=-3):
        """  mute_quantized  :: 0 = off, not 0 = on"""
        return SLClient.set_parameter(['mute_quantized', value], loop)

    @staticmethod
    def set_overdub_quantized(value, loop_number=-3):
        """  overdub_quantized :: 0 == off, not 0 = on"""
        SLClient.set_parameter(['overdub_quantized', value])

    ###########################################
    # GET PARAMETER VALUES
    # /sl/#/get
    # s:control  s:return_url  s: return_path
    ###########################################

    states = {-1: 'unknown', 0: 'Off', 1: 'WaitStart', 2: 'Recording', 3: 'WaitStop', 4: 'Playing',
              5: 'Overdubbing', 6: 'Multiplying', 7: 'Inserting', 8: 'Replacing', 9: 'Delay', 10: 'Muted',
              11: 'Scratching', 12: 'OneShot', 13: 'Substitute', 14: 'Paused', 20: 'OffMuted'}

    @staticmethod
    def get_parameter(control, loop=-3, return_path=None):
        """/sl/#/get s:control  s:return_url  s: return_path
        Which returns an OSC message to the given return url and path with the arguments:
        i: loop_index s: control f: value
        Where control is one of the above or: state::"""
        return_path = (f'/parameter/{loop}/{control}' if return_path is None else return_path)
        OSCClient.send_message(f'/sl/{loop}/get', [control, return_url, return_path])
        SLClient.parameter_evt.wait(timeout)

    @staticmethod
    def get_next_state(loop=-3):
        SLClient.get_parameter('next_state', loop)

    @staticmethod
    def get_state(loop=-3):
        SLClient.get_parameter('state', '/state', loop)
        return SLClient.state

    @staticmethod
    def get_loop_len(loop=-3):
        SLClient.get_parameter('loop_len', loop)

    @staticmethod
    def get_loop_pos(loop=-3):
        if loop == 0:
            SLClient.get_parameter('loop_pos', loop, return_path='/main_loop_pos')
            return SLClient.main_loop_pos
        else:
            SLClient.get_parameter('loop_pos', loop, return_path='/loop_pos')
            return SLClient.loop_pos

    @staticmethod
    def get_cycle_len(loop=-3):
        SLClient.get_parameter('cycle_len', loop, return_path='/cycle_len')

    @staticmethod
    def get_free_time(loop=-3):
        SLClient.get_parameter('free_time', loop)

    @staticmethod
    def get_total_time(loop=-3):
        SLClient.get_parameter('total_time', loop)

    @staticmethod
    def get_rate_output(loop=-3):
        SLClient.get_parameter('rate_output', loop)

    @staticmethod
    def get_in_peak_meter(loop=-3):
        """:: absolute float sample value 0.0 -> 1.0 (or higher)"""
        SLClient.get_parameter('in_peak_meter', loop)

    @staticmethod
    def get_out_peak_meter(loop=-3):
        """:: absolute float sample value 0.0 -> 1.0 (or higher)"""
        SLClient.get_parameter('out_peak_meter', loop)

    @staticmethod
    def get_is_soloed(loop=-3):
        """is_soloed:: 1 if soloed, 0 if not"""
        SLClient.get_parameter('is_soloed', loop)

    @staticmethod
    def get_waiting(loop=-3):
        """waiting:: 1 if waiting, 0 if not"""
        SLClient.get_parameter('waiting', loop)

    ###########################
    ###
    ### SAVE/LOAD
    ###
    ###########################

    @staticmethod
    def load_loop(file, loop_number=-3):
        """/sl/#/load_loop   s:filename  s:return_url  s:error_path
        loads a given filename into loop, may return error to error_path"""
        OSCClient.send_message(f'/sl/{loop_number}/load_loop',
                               args=[file, return_url, '/load_loop_error'])

    @staticmethod
    def save_loop(file, loop_number=None, format='wav', endian='big'):
        """/sl/#/save_loop   s:filename  s:format  s:endian  s:return_url  s:error_path
        saves current loop to given filename, may return error to error_path
        format and endian currently ignored, always uses 32 bit IEEE float WAV"""
        loop_number = SLClient.selected_loop if loop_number is None else loop_number
        OSCClient.send_message(f'/sl/{loop_number}/save_loop',
                               args=[file, format, endian, return_url, '/save_loop_error'])

    @staticmethod
    def save_session(file):
        """/save_session   s:filename  s:return_url  s:error_path
        saves current session description to filename."""
        OSCClient.send_message('/save_session', args=[file, return_url, '/save_session_error'])

    @staticmethod
    def load_session(file):
        """/load_session   s:filename  s:return_url  s:error_path
        loads and replaces the current session from filename."""
        OSCClient.send_message('/load_session', args=[file, return_url, '/load_session_error'])

    ###########################
    ###
    ### GLOBAL PARAMETERS
    ###
    ###########################
    @staticmethod
    def _set_global_parameter(parameter, value):
        """/set  s:param  f:value"""
        OSCClient.send_message('/set', type=',sf', args=[parameter, float(value)])
        SLClient._get_global_parameter(parameter)

    @staticmethod
    def _get_global_parameter(parameter):
        """ /get  s:param  s:return_url  s:retpath"""
        OSCClient.send_message('/get', type=',sss', args=[parameter, return_url, f'/global/parameter/{parameter}'])
        SLClient.selection_evt.wait(timeout)
        #SLClient.global_evt.wait()

    @staticmethod
    def get_tempo():
        SLClient._get_global_parameter('/global/tempo')

    @staticmethod
    def set_tempo(tempo):
        SLClient._set_global_parameter('tempo', tempo)

    @staticmethod
    def get_eighth_per_cycle():
        SLClient._get_global_parameter('/global/eighth_per_cycle')

    @staticmethod
    def set_eighth_per_cycle(eighth_per_cycle):
        SLClient._set_global_parameter('eighth_per_cycle', eighth_per_cycle)

    @staticmethod
    def global_get_dry():
        SLClient._get_global_parameter('/global/dry')

    @staticmethod
    def global_set_dry(dry):
        """dry         	:: range 0 -> 1 affects common input passthru"""
        SLClient._set_global_parameter('dry', dry)

    @staticmethod
    def global_get_wet():
        SLClient._get_global_parameter('wet')

    @staticmethod
    def global_set_wet(wet):
        """ wet         	:: range 0 -> 1  affects common output level"""
        SLClient._set_global_parameter('wet', wet)

    @staticmethod
    def get_input_gain():
        SLClient._get_global_parameter('input_gain')

    @staticmethod
    def global_set_input_gain(input_gain):
        """input_gain    :: range 0 -> 1  affects common input gain"""
        SLClient._set_global_parameter('input_gain', input_gain)

    @staticmethod
    def get_sync_source():
        SLClient._get_global_parameter('sync_source')

    @staticmethod
    def set_sync_source(sync_source):
        """sync_source  :: -3 = internal,  -2 = midi, -1 = jack, 0 = none, # > 0 = loop number (1 indexed)"""
        SLClient._set_global_parameter('sync_source', sync_source)
        SLClient.sync_source = sync_source

    @staticmethod
    def get_tap_tempo():
        SLClient._get_global_parameter('tap_tempo')

    @staticmethod
    def set_tap_tempo(tap_tempo):
        """tap_tempo :: any changes"""
        SLClient._set_global_parameter('tap_tempo', tap_tempo)

    @staticmethod
    def get_save_loop():
        SLClient._get_global_parameter('save_loop')

    @staticmethod
    def set_save_loop(save_loop):
        """save_loop :: any change triggers quick save, be careful"""
        SLClient._set_global_parameter('save_loop', save_loop)

    @staticmethod
    def get_select_next_loop():
        SLClient._get_global_parameter('select_next_loop')

    @staticmethod
    def set_select_next_loop():
        """select_next_loop  :: any changes"""
        SLClient._set_global_parameter('select_next_loop', 1.0)


    @staticmethod
    def get_select_prev_loop():
        SLClient._get_global_parameter('select_prev_loop')

    @staticmethod
    def set_select_prev_loop(select_prev_loop):
        """select_prev_loop  :: any changes"""
        SLClient._set_global_parameter('select_prev_loop', select_prev_loop)

    @staticmethod
    def get_select_all_loops():
        SLClient._get_global_parameter('select_all_loops')

    @staticmethod
    def set_select_all_loops(select_all_loops):
        """select_all_loops   :: any changes"""
        SLClient._set_global_parameter('select_all_loops', select_all_loops)

    @staticmethod
    def get_selected_loop_num():
        SLClient._get_global_parameter('selected_loop_num')
        return SLClient.selected_loop


    @staticmethod
    def set_selected_loop_num(loop_num):
        """selected_loop_num   :: -1 = all, 0->N selects loop instances (first loop is 0, etc)"""
        SLClient._set_global_parameter('selected_loop_num', loop_num)
        return SLClient.get_selected_loop_num()


    @staticmethod
    def get_output_midi_clock():
        SLClient._get_global_parameter('output_midi_clock')

    @staticmethod
    def set_output_midi_clock(output_midi_clock):
        """output_midi_clock :: 0.0 = no, 1.0 = yes"""
        SLClient._set_global_parameter('output_midi_clock', output_midi_clock)

    ###############################
    ###
    ### LOOP ADD/REMOVE
    ###
    ###############################

    @staticmethod
    def loop_add(channels=2, length=60):
        """/loop_add  i:#channels  f:min_length_seconds
        adds a new loop with # channels and a minimum loop memory"""
        OSCClient.send_message('/loop_add', type=',if', args=[channels, length])
        SLClient.ping()

    @staticmethod
    def loop_del(index=-3):
        """/loop_del  i:loopindex
        a value of -1 for loopindex removes last loop, and is the only
        value currently recommended."""
        OSCClient.send_message('/loop_del', type=',i', args=[index])

    ###############################
    ###
    ### SHUTDOWN
    ###
    ###############################

    @staticmethod
    def quit():
        """/quit
        shutdown engine"""
        OSCClient.send_message('/quit')

    ###############################
    ###
    ### REGISTER FOR CONTROL CHANGES
    ###
    ### The following messages register and unregister from update events
    ### which will be sent the returl and retpath specified.  The update OSC message
    ### has the following parameters:
    ###     i:loop#  s:ctrl  f:control_value
    ###
    ###############################

    @staticmethod
    def register_update(control, return_path, loop):
        """/sl/#/register_update  s:ctrl s:returl s:retpath"""
        OSCClient.send_message(f'/sl/{loop}/register_update', [control, return_url, return_path])

    @staticmethod
    def unregister_update(control, return_path, loop):
        """/sl/#/unregister_update  s:ctrl s:returl s:retpath"""
        OSCClient.send_message(f'/sl/{loop}/register_update', [control, return_url, return_path])

    @staticmethod
    def register_auto_update(control, return_path, loop, interval=10):
        """/sl/#/register_auto_update  s:ctrl i:ms_interval s:returl s:retpath"""
        OSCClient.send_message(f'/sl/{loop}/register_auto_update', [control, interval, return_url, return_path])

    @staticmethod
    def unregister_auto_update(control, return_path, loop):
        """/sl/#/unregister_auto_update  s:ctrl s:returl s:retpath"""
        OSCClient.send_message(f'/sl/{loop}/unregister_auto_update', [control, return_url, return_path])

    @staticmethod
    def register_global_update(control, return_path):
        """/register_update  s:ctrl s:returl s:retpath"""
        OSCClient.send_message('/register_update', [control, return_url, return_path])

    @staticmethod
    def unregister_global_update(control, return_path):
        """/unregister_update  s:ctrl s:returl s:retpath"""
        OSCClient.send_message('/unregister_update', [control, return_url, return_path])

    @staticmethod
    def register_global_auto_update(control, return_path, interval=10):
        """ /register_auto_update  s:ctrl i:ms_interval s:returl s:retpath"""
        OSCClient.send_message('/register_auto_update', [control, interval, return_url, return_path])

    @staticmethod
    def unregister_global_auto_update(control, return_path):
        """/unregister_auto_update  s:ctrl s:returl s:retpath"""
        OSCClient.send_message('/unregister_auto_update', [control, return_url, return_path])
