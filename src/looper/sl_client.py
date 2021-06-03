import time

from src.osc.osc_client import OSCClient

return_url = 'localhost:9952'
class SLClient:

    @staticmethod
    def ping():
        """"PING Engine
         /ping s:return_url s:return_path

         If engine is there, it will respond with to the given URL and PATH with an OSC message with arguments:
         s:hosturl  s:version  i:loopcount"""
        OSCClient.send_message('/ping', [return_url, '/pingrecieved'])

    @staticmethod
    def hit(loop_number, command):
        """""/sl/#/hit s:cmdname
        A single hit only, no press-release action"""

        OSCClient.send_message(f'/sl/{loop_number}/hit', [command])

    ##################################################################
    ### Loop commands and parameter gets/sets paths are all prefixed with:
    ###   /sl/#/   where # is the loop index starting from 0.
    ### Specifying -1 will apply the command or operation to all loops.
    ### Specifying -3 will apply the command or operation to the selected loop.
    ##################################################################

    @staticmethod
    def record(loop_number=-3):
        SLClient.hit(loop_number, 'record')

    @staticmethod
    def overdub(loop_number=-3):
        SLClient.hit(loop_number, 'overdub')

    @staticmethod
    def multiply(loop_number=-3):
        SLClient.hit(loop_number, 'multiply')

    @staticmethod
    def insert(loop_number=-3):
        SLClient.hit(loop_number, 'insert')

    @staticmethod
    def replace(loop_number=-3):
        SLClient.hit(loop_number, 'replace')

    @staticmethod
    def reverse(loop_number=-3):
        SLClient.hit(loop_number, 'reverse')

    @staticmethod
    def mute(loop_number=-3):
        SLClient.hit(loop_number, 'mute')

    @staticmethod
    def undo(loop_number=-3):
        SLClient.hit(loop_number, 'undo')

    @staticmethod
    def redo(loop_number=-3):
        SLClient.hit(loop_number, 'redo')

    @staticmethod
    def oneshot(loop_number=3):
        SLClient.hit(loop_number, 'oneshot')

    @staticmethod
    def trigger(loop_number=-3):
        SLClient.hit(loop_number, 'trigger')

    @staticmethod
    def substitute(loop_number=-3):
        SLClient.hit(loop_number, 'substitute')

    @staticmethod
    def undo_all(loop_number=-3):
        SLClient.hit(loop_number, 'undo_all')

    @staticmethod
    def redo_all(loop_number=-3):
        SLClient.hit(loop_number, 'redo_all')

    @staticmethod
    def mute_on(loop_number=-3):
        SLClient.hit(loop_number, 'mute_on')

    @staticmethod
    def mute_off(loop_number=-3):
        SLClient.hit(loop_number, 'mute_off')

    @staticmethod
    def solo(loop_number=-3):
        SLClient.hit(loop_number, 'solo')

    @staticmethod
    def pause(loop_number=-3):
        SLClient.hit(loop_number, 'pause')

    @staticmethod
    def solo_next(loop_number=-3):
        SLClient.hit(loop_number, 'solo_next')

    @staticmethod
    def solo_prev(loop_number=-3):
        SLClient.hit(loop_number, 'solo_prev')

    @staticmethod
    def record_solo(loop_number=-3):
        SLClient.hit(loop_number, 'record_solo')

    @staticmethod
    def record_solo_next(loop_number=-3):
        SLClient.hit(loop_number, 'record_solo_next')

    @staticmethod
    def record_solo_prev(loop_number=-3):
        SLClient.hit(loop_number, 'record_solo_prev')

    @staticmethod
    def set_sync_pos(loop_number=-3):
        SLClient.hit(loop_number, 'set_sync_pos')

    @staticmethod
    def reset_sync_pos(loop_number=-3):
        SLClient.hit(loop_number, 'reset_sync_pos')

    #######################################################
    # SET PARAMETER VALUES
    # /sl/#/set  s:control  f:value
    #   To set a parameter for a loop.
    #######################################################
    @staticmethod
    def set_parameter(value, loop_number):
        OSCClient.send_message(f'/sl/{loop_number}/set', value)

    @staticmethod
    def set_rec_thresh(value, loop_number=-3):
        """  rec_thresh  	:: expected range is 0 -> 1"""
        SLClient.set_parameter(['rec_thresh', value], loop_number)

    @staticmethod
    def set_feedback(value, loop_number=-3):
        """  feedback    	:: range 0 -> 1"""
        SLClient.set_parameter(['feedback', value], loop_number)

    @staticmethod
    def set_dry(value, loop_number=-3):
        """  dry         	:: range 0 -> 1"""
        SLClient.set_parameter(['dry', value], loop_number)

    @staticmethod
    def set_wet(value, loop_number=-3):
        """  wet         	:: range 0 -> 1"""
        SLClient.set_parameter(['wet', value], loop_number)

    @staticmethod
    def set_input_gain(value, loop_number=-3):
        """  input_gain    :: range 0 -> 1"""
        SLClient.set_parameter(['input_gain', value], loop_number)

    @staticmethod
    def set_rate(value, loop_number=-3):
        """  rate        	:: range 0.25 -> 4.0"""
        SLClient.set_parameter(['rate', value], loop_number)

    @staticmethod
    def set_scratch_pos(value, loop_number=-3):
        """  scratch_pos  	 :: 0 -> 1 """
        SLClient.set_parameter(['scratch_pos', value], loop_number)

    @staticmethod
    def set_delay_trigger(value, loop_number=-3):
        """  delay_trigger  :: any changes"""
        SLClient.set_parameter(['delay_trigger', value], loop_number)

    @staticmethod
    def set_quantize(value, loop_number=-3):
        """  quantize       :: 0 = off, 1 = cycle, 2 = 8th, 3 = loop"""
        SLClient.set_parameter(['quantize', value], loop_number)

    @staticmethod
    def set_round(value, loop_number=-3):
        """  round          :: 0 = off,  not 0 = on """
        SLClient.set_parameter(['round', value], loop_number)

    @staticmethod
    def set_redo_is_tap(value, loop_number=-3):
        """  redo_is_tap    :: 0 = off,  not 0 = on """
        SLClient.set_parameter(['redo_is_tap', value], loop_number)

    @staticmethod
    def set_sync(value, loop_number=-3):
        """  sync           :: 0 = off,  not 0 = on """
        SLClient.set_parameter(['sync', value], loop_number)

    @staticmethod
    def set_playback_sync(value, loop_number=-3):
        """  playback_sync  :: 0 = off,  not 0 = on """
        SLClient.set_parameter(['playback_sync', value], loop_number)

    @staticmethod
    def set_use_rate(value, loop_number=-3):
        """  use_rate       :: 0 = off,  not 0 = on """
        SLClient.set_parameter(['use_rate', value], loop_number)

    @staticmethod
    def set_fade_samples(value, loop_number=-3):
        """  fade_samples   :: 0 -> ..."""
        SLClient.set_parameter(['fade_samples', value], loop_number)

    @staticmethod
    def set_use_feedback_play(value, loop_number=-3):
        """  use_feedback_play   :: 0 = off,  not 0 = on"""
        SLClient.set_parameter(['use_feedback_play', value], loop_number)

    @staticmethod
    def set_use_common_ins(value, loop_number=-3):
        """  use_common_ins   :: 0 = off,  not 0 = on """
        SLClient.set_parameter(['use_common_ins', value], loop_number)

    @staticmethod
    def set_use_common_outs(value, loop_number=-3):
        """  use_common_outs   :: 0 = off,  not 0 = on """
        SLClient.set_parameter(['use_common_outs', value], loop_number)

    @staticmethod
    def set_relative_sync(value, loop_number=-3):
        """  relative_sync   :: 0 = off, not 0 = on"""
        SLClient.set_parameter(['relative_sync', value], loop_number)

    @staticmethod
    def set_use_safety_feedback(value, loop_number=-3):
        """  use_safety_feedback   :: 0 = off, not 0 = on"""
        SLClient.set_parameter(['use_safety_feedback', value], loop_number)

    @staticmethod
    def set_pan_1(value, loop_number=-3):
        """  pan_1         	:: range 0 -> 1"""
        SLClient.set_parameter(['pan_1', value], loop_number)

    @staticmethod
    def set_pan_2(value, loop_number=-3):
        """  pan_2         	:: range 0 -> 1"""
        SLClient.set_parameter(['pan_2', value], loop_number)

    @staticmethod
    def set_pan_3(value, loop_number=-3):
        """  pan_3         	:: range 0 -> 1"""
        SLClient.set_parameter(['pan_3', value], loop_number)

    @staticmethod
    def set_pan_4(value, loop_number=-3):
        """  pan_4         	:: range 0 -> 1"""
        SLClient.set_parameter(['pan_4', value], loop_number)

    @staticmethod
    def set_input_latency(value, loop_number=-3):
        """  input_latency :: range 0 -> ..."""
        SLClient.set_parameter(['input_latency', value], loop_number)

    @staticmethod
    def set_output_latency(value, loop_number=-3):
        """  output_latency :: range 0 -> ..."""
        SLClient.set_parameter(['output_latency', value], loop_number)

    @staticmethod
    def set_trigger_latency(value, loop_number=-3):
        """  trigger_latency :: range 0 -> ..."""
        SLClient.set_parameter(['trigger_latency', value], loop_number)

    @staticmethod
    def set_autoset_latency(value, loop_number=-3):
        """autoset_latency  :: 0 = off, not 0 = on"""
        SLClient.set_parameter(['autoset_latency', value], loop_number)

    @staticmethod
    def set_mute_quantized(value, loop_number=-3):
        """  mute_quantized  :: 0 = off, not 0 = on"""
        SLClient.set_parameter(['mute_quantized', value], loop_number)

    @staticmethod
    def set_overdub_quantized(value, loop_number=-3):
        """  overdub_quantized :: 0 == off, not 0 = on"""
        SLClient.set_parameter(['overdub_quantized', value], loop_number)

    ###########################################
    # GET PARAMETER VALUES
    # /sl/#/get
    # s:control  s:return_url  s: return_path
    ###########################################

    states = {-1: 'unknown', 0: 'Off', 1: 'WaitStart', 2: 'Recording', 3: 'WaitStop', 4: 'Playing',
              5: 'Overdubbing', 6: 'Multiplying', 7: 'Inserting', 8: 'Replacing', 9: 'Delay', 10: 'Muted',
              11: 'Scratching', 12: 'OneShot', 13: 'Substitute', 14: 'Paused', 20: 'OffMuted'}

    @staticmethod
    def get_parameter(control, loop_number):
        """/sl/#/get s:control  s:return_url  s: return_path
        Which returns an OSC message to the given return url and path with the arguments:
        i: loop_index s: control f: value
        Where control is one of the above or: state::"""

        OSCClient.send_message(f'/sl/{loop_number}/get', [control, return_url,
                                                          f'/parameter/{loop_number}/{control}'])

    @staticmethod
    def get_next_state(loop_number=-3):
        SLClient.get_parameter('next_state', loop_number)

    @staticmethod
    def get_loop_len(loop_number=-3):
        SLClient.get_parameter('loop_len', loop_number)

    @staticmethod
    def get_loop_pos(loop_number=-3):
        SLClient.get_parameter('loop_pos', loop_number)

    @staticmethod
    def get_cycle_len(loop_number=-3):
        SLClient.get_parameter('cycle_len', loop_number)

    @staticmethod
    def get_free_time(loop_number=-3):
        SLClient.get_parameter('free_time', loop_number)

    @staticmethod
    def get_total_time(loop_number=-3):
        SLClient.get_parameter('total_time', loop_number)

    @staticmethod
    def get_rate_output(loop_number=-3):
        SLClient.get_parameter('rate_output', loop_number)

    @staticmethod
    def get_in_peak_meter(loop_number=-3):
        """:: absolute float sample value 0.0 -> 1.0 (or higher)"""
        SLClient.get_parameter('in_peak_meter', loop_number)

    @staticmethod
    def get_out_peak_meter(loop_number=-3):
        """:: absolute float sample value 0.0 -> 1.0 (or higher)"""
        SLClient.get_parameter('out_peak_meter', loop_number)

    @staticmethod
    def get_is_soloed(loop_number=-3):
        """is_soloed:: 1 if soloed, 0 if not"""
        SLClient.get_parameter('is_soloed', loop_number)

    @staticmethod
    def get_waiting(loop_number=-3):
        """waiting:: 1 if waiting, 0 if not"""
        SLClient.get_parameter('waiting', loop_number)

    ###########################
    ###
    ### SAVE/LOAD
    ###
    ###########################

    @staticmethod
    def load_loop(loop_number, file):
        """/sl/#/load_loop   s:filename  s:return_url  s:error_path
        loads a given filename into loop, may return error to error_path"""
        OSCClient.send_message(f'/sl/{loop_number}/load_loop',
                               args=[file,     return_url, '/load_loop_error'])

    @staticmethod
    def save_loop(file, loop_number=-3, format='wav', endian='big'):
        """/sl/#/save_loop   s:filename  s:format  s:endian  s:return_url  s:error_path
        saves current loop to given filename, may return error to error_path
        format and endian currently ignored, always uses 32 bit IEEE float WAV"""
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

    @staticmethod
    def _get_global_parameter(parameter, return_path):
        """ /get  s:param  s:return_url  s:retpath"""
        OSCClient.send_message('/get', type=',sss', args=[parameter, return_url, return_path])

    @staticmethod
    def get_tempo():
        SLClient._get_global_parameter('/global/tempo', '/global/parameter/tempo')

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
        SLClient._get_global_parameter('wet', '/global/wet')

    @staticmethod
    def global_set_wet(wet):
        """ wet         	:: range 0 -> 1  affects common output level"""
        SLClient._set_global_parameter('wet', wet)

    @staticmethod
    def get_input_gain():
        SLClient._get_global_parameter('input_gain', '/global/input_gain')

    @staticmethod
    def set_input_gain(input_gain):
        """input_gain    :: range 0 -> 1  affects common input gain"""
        SLClient._set_global_parameter('input_gain', input_gain)

    @staticmethod
    def get_sync_source():
        SLClient._get_global_parameter('sync_source', '/global/sync_source')

    @staticmethod
    def set_sync_source(sync_source):
        """sync_source  :: -3 = internal,  -2 = midi, -1 = jack, 0 = none, # > 0 = loop number (1 indexed)"""
        SLClient._set_global_parameter('sync_source', sync_source)

    @staticmethod
    def get_tap_tempo():
        SLClient._get_global_parameter('tap_tempo', '/global/tap_tempo')

    @staticmethod
    def set_tap_tempo(tap_tempo):
        """tap_tempo :: any changes"""
        SLClient._set_global_parameter('tap_tempo', tap_tempo)

    @staticmethod
    def get_save_loop():
        SLClient._get_global_parameter('save_loop', '/global/save_loop')

    @staticmethod
    def set_save_loop(save_loop):
        """save_loop :: any change triggers quick save, be careful"""
        SLClient._set_global_parameter('save_loop', save_loop)

    @staticmethod
    def get_select_next_loop():
        SLClient._get_global_parameter('select_next_loop', '/global/select_next_loop')

    @staticmethod
    def set_select_next_loop():
        """select_next_loop  :: any changes"""
        SLClient._set_global_parameter('select_next_loop', 1.0)


    @staticmethod
    def get_select_prev_loop():
        SLClient._get_global_parameter('select_prev_loop', '/global/select_prev_loop')

    @staticmethod
    def set_select_prev_loop(select_prev_loop):
        """select_prev_loop  :: any changes"""
        SLClient._set_global_parameter('select_prev_loop', select_prev_loop)

    @staticmethod
    def get_select_all_loops():
        SLClient._get_global_parameter('select_all_loops', '/global/select_all_loops')

    @staticmethod
    def set_select_all_loops(select_all_loops):
        """select_all_loops   :: any changes"""
        SLClient._set_global_parameter('select_all_loops', select_all_loops)

    @staticmethod
    def get_selected_loop_num():
        SLClient._get_global_parameter('selected_loop_num', '/global/selected_loop_num')

    @staticmethod
    def set_selected_loop_num(loop_num):
        """selected_loop_num   :: -1 = all, 0->N selects loop instances (first loop is 0, etc)"""
        SLClient._set_global_parameter('selected_loop_num', loop_num)

    @staticmethod
    def get_output_midi_clock():
        SLClient._get_global_parameter('output_midi_clock', '/global/output_midi_clock')

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

    @staticmethod
    def loop_del(index=-3):
        """/loop_del  i:loopindex
        a value of -1 for loopindex removes last loop, and is the only
        value currently recommended."""
        OSCClient.send_message('/loop_del', type=',i', args=[index])
        #SLClient.ping()

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
    def register_update(control, return_url, return_path, loop_number=-3):
        """/sl/#/register_update  s:ctrl s:returl s:retpath"""
        OSCClient.send_message(f'/sl/{loop_number}/register_update', [control, return_url, return_path])

    @staticmethod
    def unregister_update(control, return_url, return_path, loop_number=-3):
        """/sl/#/unregister_update  s:ctrl s:returl s:retpath"""
        OSCClient.send_message(f'/sl/{loop_number}/register_update', [control, return_url, return_path])

    @staticmethod
    def register_auto_update(control, return_url, return_path, loop_number=-3, interval=10):
        """/sl/#/register_auto_update  s:ctrl i:ms_interval s:returl s:retpath"""
        OSCClient.send_message(f'/sl/{loop_number}/register_auto_update', [control, interval, return_url, return_path])

    @staticmethod
    def unregister_auto_update(control, return_url, return_path, loop_number=-3):
        """/sl/#/unregister_auto_update  s:ctrl s:returl s:retpath"""
        OSCClient.send_message(f'/sl/{loop_number}/register_auto_update', [control, return_url, return_path])

    @staticmethod
    def register_global_update(control, return_url, return_path):
        """/register_update  s:ctrl s:returl s:retpath"""
        OSCClient.send_message('/register_update', [control, return_url, return_path])

    @staticmethod
    def unregister_global_update(control, return_url, return_path):
        """/unregister_update  s:ctrl s:returl s:retpath"""
        OSCClient.send_message('/unregister_update', [control, return_url, return_path])

    @staticmethod
    def register_global_auto_update(control, return_url, return_path, interval=10):
        """ /register_auto_update  s:ctrl i:ms_interval s:returl s:retpath"""
        OSCClient.send_message('/register_auto_update', [control, interval, return_url, return_path])

    @staticmethod
    def unregister_global_auto_update(control, return_url, return_path):
        """/unregister_auto_update  s:ctrl s:returl s:retpath"""
        OSCClient.send_message('/unregister_auto_update', [control, return_url, return_path])
