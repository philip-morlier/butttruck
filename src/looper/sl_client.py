import time
from threading import Thread

from osc4py3.as_eventloop import *
from osc4py3 import oscbuildparse
import logging


class OSCClient:
    def __init__(self, host='127.0.0.1', port=9951, client_name='butttruck'):
        self.sl_host = host
        self.sl_port = port
        self.client_name = client_name
        self.thread = Thread(target=self.run, daemon=True)
        self.thread.start()

    # osc4py3 as_allthreads is expensive but may work better than this
    def run(self):
        osc_udp_client(self.sl_host, self.sl_port, self.client_name)
        while True:
            time.sleep(0.05)
            osc_process()

    def send_message(self, message, args=None, type=None):
        msg = oscbuildparse.OSCMessage(message, type, args)
        osc_send(msg, self.client_name)


class OSCServer:

    def __init__(self, host='127.0.0.1', port=9952, debug=False):
        self.host = host
        self.port = port
        self.url = self.host + ':' + str(self.port)
        self.debug = debug
        self.start()

    def start(self):
        if self.debug:
            logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            logger = logging.getLogger("osc")
            logger.setLevel(logging.DEBUG)
            osc_startup(logger=logger)
        else:
            osc_startup()
        osc_udp_server(self.host, self.port, "osc_server")
        self._register_handlers()

    def _register_handlers(self):
        osc_method("/pingrecieved", self.ping_handler)
        osc_method("/global/*", self.global_parameter_hander)

    def register_handler(self, address, function):
        osc_method(address, function)

    def global_parameter_hander(self, loop, param, value):
        print(f'Global parameter {param} is {value}')

    def ping_handler(self, address, version, loop_count):
        print(f'Sooperlooper {version} is listening at: {address}. {loop_count} loops in progress')


class SLClient:
    def __init__(self):
        self.osc_server = OSCServer()
        self.osc_client = OSCClient()

    def ping(self):
        """"PING Engine
         /ping s:return_url s:return_path

         If engine is there, it will respond with to the given URL and PATH with an OSC message with arguments:
         s:hosturl  s:version  i:loopcount"""
        self.osc_client.send_message('/ping', [self.osc_server.url, '/pingrecieved'])

    def hit(self, loop_number, command):
        """""/sl/#/hit s:cmdname
        A single hit only, no press-release action"""

        self.osc_client.send_message(f'/sl/{loop_number}/hit', [command])

    ##################################################################
    ### Loop commands and parameter gets/sets paths are all prefixed with:
    ###   /sl/#/   where # is the loop index starting from 0.
    ### Specifying -1 will apply the command or operation to all loops.
    ### Specifying -3 will apply the command or operation to the selected loop.
    ##################################################################

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

    def substitute(self, loop_number=-3):
        self.hit(loop_number, 'substitute')

    def undo_all(self, loop_number=-3):
        self.hit(loop_number, 'undo_all')

    def redo_all(self, loop_number=-3):
        self.hit(loop_number, 'redo_all')

    def mute_on(self, loop_number=-3):
        self.hit(loop_number, 'mute_on')

    def mute_off(self, loop_number=-3):
        self.hit(loop_number, 'mute_off')

    def solo(self, loop_number=-3):
        self.hit(loop_number, 'solo')

    def pause(self, loop_number=-3):
        self.hit(loop_number, 'pause')

    def solo_next(self, loop_number=-3):
        self.hit(loop_number, 'solo_next')

    def solo_prev(self, loop_number=-3):
        self.hit(loop_number, 'solo_prev')

    def record_solo(self, loop_number=-3):
        self.hit(loop_number, 'record_solo')

    def record_solo_next(self, loop_number=-3):
        self.hit(loop_number, 'record_solo_next')

    def record_solo_prev(self, loop_number=-3):
        self.hit(loop_number, 'record_solo_prev')

    def set_sync_pos(self, loop_number=-3):
        self.hit(loop_number, 'set_sync_pos')

    def reset_sync_pos(self, loop_number=-3):
        self.hit(loop_number, 'reset_sync_pos')

    #######################################################
    # SET PARAMETER VALUES
    # /sl/#/set  s:control  f:value
    #   To set a parameter for a loop.
    #######################################################

    def set_parameter(self, value, loop_number):
        self.osc_client.send_message(f'/sl/{loop_number}/set', [value])

    def set_rec_thresh(self, value, loop_number=-3):
        """  rec_thresh  	:: expected range is 0 -> 1"""
        self.set_parameter(['rec_thresh', value], loop_number)

    def set_feedback(self, value, loop_number=-3):
        """  feedback    	:: range 0 -> 1"""
        self.set_parameter(['feedback', value], loop_number)

    def set_dry(self, value, loop_number=-3):
        """  dry         	:: range 0 -> 1"""
        self.set_parameter(['dry', value], loop_number)

    def set_wet(self, value, loop_number=-3):
        """  wet         	:: range 0 -> 1"""
        self.set_parameter(['wet', value], loop_number)

    def set_input_gain(self, value, loop_number=-3):
        """  input_gain    :: range 0 -> 1"""
        self.set_parameter(['input_gain', value], loop_number)

    def set_rate(self, value, loop_number=-3, ):
        """  rate        	:: range 0.25 -> 4.0"""
        self.set_parameter(['feedback', value], loop_number)

    def set_scratch_pos(self, value, loop_number=-3):
        """  scratch_pos  	 :: 0 -> 1 """
        self.set_parameter(['scratch_pos', value], loop_number)

    def set_delay_trigger(self, value, loop_number=-3):
        """  delay_trigger  :: any changes"""
        self.set_parameter(['delay_trigger', value], loop_number)

    def set_quantize(self, value, loop_number=-3):
        """  quantize       :: 0 = off, 1 = cycle, 2 = 8th, 3 = loop"""
        self.set_parameter(['quantize', value], loop_number)

    def set_round(self, value, loop_number=-3):
        """  round          :: 0 = off,  not 0 = on """
        self.set_parameter(['round', value], loop_number)

    def set_redo_is_tap(self, value, loop_number=-3):
        """  redo_is_tap    :: 0 = off,  not 0 = on """
        self.set_parameter(['redo_is_tap', value], loop_number)

    def set_sync(self, value, loop_number=-3):
        """  sync           :: 0 = off,  not 0 = on """
        self.set_parameter(['sync', value], loop_number)

    def set_playback_sync(self, value, loop_number=-3):
        """  playback_sync  :: 0 = off,  not 0 = on """
        self.set_parameter(['playback_sync', value], loop_number)

    def set_use_rate(self, value, loop_number=-3):
        """  use_rate       :: 0 = off,  not 0 = on """
        self.set_parameter(['use_rate', value], loop_number)

    def set_fade_samples(self, value, loop_number=-3):
        """  fade_samples   :: 0 -> ..."""
        self.set_parameter(['fade_samples', value], loop_number)

    def set_use_feedback_play(self, value, loop_number=-3):
        """  use_feedback_play   :: 0 = off,  not 0 = on"""
        self.set_parameter(['use_feedback_play', value], loop_number)

    def set_use_common_ins(self, value, loop_number=-3):
        """  use_common_ins   :: 0 = off,  not 0 = on """
        self.set_parameter(['use_common_ins', value], loop_number)

    def set_use_common_outs(self, value, loop_number=-3):
        """  use_common_outs   :: 0 = off,  not 0 = on """
        self.set_parameter(['use_common_outs', value], loop_number)

    def set_relative_sync(self, value, loop_number=-3):
        """  relative_sync   :: 0 = off, not 0 = on"""
        self.set_parameter(['relative_sync', value], loop_number)

    def set_use_safety_feedback(self, value, loop_number=-3):
        """  use_safety_feedback   :: 0 = off, not 0 = on"""
        self.set_parameter(['use_safety_feedback', value], loop_number)

    def set_pan_1(self, value, loop_number=-3):
        """  pan_1         	:: range 0 -> 1"""
        self.set_parameter(['pan_1', value], loop_number)

    def set_pan_2(self, value, loop_number=-3):
        """  pan_2         	:: range 0 -> 1"""
        self.set_parameter(['pan_2', value], loop_number)

    def set_pan_3(self, value, loop_number=-3):
        """  pan_3         	:: range 0 -> 1"""
        self.set_parameter(['pan_3', value], loop_number)

    def set_pan_4(self, value, loop_number=-3):
        """  pan_4         	:: range 0 -> 1"""
        self.set_parameter(['pan_4', value], loop_number)

    def set_input_latency(self, value, loop_number=-3):
        """  input_latency :: range 0 -> ..."""
        self.set_parameter(['input_latency', value], loop_number)

    def set_output_latency(self, value, loop_number=-3):
        """  output_latency :: range 0 -> ..."""
        self.set_parameter(['output_latency', value], loop_number)

    def set_trigger_latency(self, value, loop_number=-3):
        """  trigger_latency :: range 0 -> ..."""
        self.set_parameter(['trigger_latency', value], loop_number)

    def set_autoset_latency(self, value, loop_number=-3):
        """autoset_latency  :: 0 = off, not 0 = on"""
        self.set_parameter(['autoset_latency', value], loop_number)

    def set_mute_quantized(self, value, loop_number=-3):
        """  mute_quantized  :: 0 = off, not 0 = on"""
        self.set_parameter(['mute_quantized', value], loop_number)

    def set_overdub_quantized(self, value, loop_number=-3):
        """  overdub_quantized :: 0 == off, not 0 = on"""
        self.set_parameter(['overdub_quantized', value], loop_number)

    ###########################################
    # GET PARAMETER VALUES
    # /sl/#/get
    # s:control  s:return_url  s: return_path
    ###########################################

    states = {-1: 'unknown', 0: 'Off', 1: 'WaitStart', 2: 'Recording', 3: 'WaitStop', 4: 'Playing',
              5: 'Overdubbing', 6: 'Multiplying', 7: 'Inserting', 8: 'Replacing', 9: 'Delay', 10: 'Muted',
              11: 'Scratching', 12: 'OneShot', 13: 'Substitute', 14: 'Paused', 20: 'OffMuted'}

    def get_parameter(self, control, loop_number):
        """/sl/#/get s:control  s:return_url  s: return_path
        Which returns an OSC message to the given return url and path with the arguments:
        i: loop_index s: control f: value
        Where control is one of the above or: state::"""

        self.osc_client.send_message(f'/sl/{loop_number}/get', [control, self.osc_server.url,
                                                                f'/parameter/{loop_number}/{control}'])

    def get_next_state(self, loop_number=-3):
        self.get_parameter('next_state', loop_number)

    def get_loop_len(self, loop_number=-3):
        self.get_parameter('loop_len', loop_number=-3)

    def get_loop_pos(self, loop_number=-3):
        self.get_parameter('loop_pos', loop_nymber=-3)

    def get_cycle_len(self, loop_number=-3):
        self.get_parameter('cycle_len', loop_number=-3)

    def get_free_time(self, loop_number=-3):
        self.get_parameter('free_time', loop_number=-3)

    def get_total_time(self, loop_number=-3):
        self.get_parameter('total_time', loop_number=-3)

    def get_rate_output(self, loop_number=-3):
        self.get_parameter('rate_output', loop_number=-3)

    def get_in_peak_meter(self, loop_number=-3):
        """:: absolute float sample value 0.0 -> 1.0 (or higher)"""
        self.get_parameter('in_peak_meter', loop_number=-3)

    def get_out_peak_meter(self, loop_number=-3):
        """:: absolute float sample value 0.0 -> 1.0 (or higher)"""
        self.get_parameter('out_peak_meter', loop_number=-3)

    def get_is_soloed(self, loop_number=-3):
        """is_soloed:: 1 if soloed, 0 if not"""
        self.get_parameter('is_soloed', loop_number=-3)

    def get_waiting(self, loop_number=-3):
        """waiting:: 1 if waiting, 0 if not"""
        self.get_parameter('waiting', loop_number=-3)

    ###########################
    ###
    ### SAVE/LOAD
    ###
    ###########################

    def load_loop(self, loop_number, file):
        """/sl/#/load_loop   s:filename  s:return_url  s:error_path
        loads a given filename into loop, may return error to error_path"""
        self.osc_client.send_message(f'/sl/{loop_number}/load_loop',
                                     args=[file, self.osc_server.url, '/load_loop_error'])

    def save_loop(self, loop_number, file, format='wav', endian='big'):
        """/sl/#/save_loop   s:filename  s:format  s:endian  s:return_url  s:error_path
        saves current loop to given filename, may return error to error_path
        format and endian currently ignored, always uses 32 bit IEEE float WAV"""
        self.osc_client.send_message(f'/sl/{loop_number}/save_loop',
                                     args=[file, format, endian, self.osc_server.url, '/save_loop_error'])

    def save_session(self, file):
        """/save_session   s:filename  s:return_url  s:error_path
        saves current session description to filename."""
        self.osc_client.send_message('/save_session', args=[file, self.osc_server.url, '/save_session_error'])

    def load_session(self, file):
        """/load_session   s:filename  s:return_url  s:error_path
        loads and replaces the current session from filename."""
        self.osc_client.send_message('/load_session', args=[file, self.osc_server.url, '/load_session_error'])

    ###########################
    ###
    ### GLOBAL PARAMETERS
    ###
    ###########################

    def _set_global_parameter(self, parameter, value):
        """/set  s:param  f:value"""
        self.osc_client.send_message('/set', type=',sf', args=[parameter, float(value)])

    def _get_global_parameter(self, parameter, return_url, return_path):
        """ /get  s:param  s:return_url  s:retpath"""
        self.osc_client.send_message('/get', type=',sss', args=[parameter, return_url, return_path])

    def get_tempo(self):
        self._get_global_parameter('tempo', self.osc_server.url, '/global/tempo')

    def set_tempo(self, tempo):
        self._set_global_parameter('tempo', tempo)

    def get_eighth_per_cycle(self):
        self._get_global_parameter('eighth_per_cycle', self.osc_server.url, '/global/eighth_per_cycle')

    def set_eighth_per_cycle(self, eighth_per_cycle):
        self._set_global_parameter('eighth_per_cycle', eighth_per_cycle)

    def get_dry(self):
        self._get_global_parameter('dry', self.osc_server.url, '/global/dry')

    def set_dry(self, dry):
        """dry         	:: range 0 -> 1 affects common input passthru"""
        self._set_global_parameter('dry', dry)

    def get_wet(self):
        self._get_global_parameter('wet', self.osc_server.url, '/global/wet')

    def set_wet(self, wet):
        """ wet         	:: range 0 -> 1  affects common output level"""
        self._set_global_parameter('wet', wet)

    def get_input_gain(self):
        self._get_global_parameter('input_gain', self.osc_server.url, '/global/input_gain')

    def set_input_gain(self, input_gain):
        """input_gain    :: range 0 -> 1  affects common input gain"""
        self._set_global_parameter('input_gain', input_gain)

    def get_sync_source(self):
        self._get_global_parameter('sync_source', self.osc_server.url, '/global/sync_source')

    def set_sync_source(self, sync_source):
        """sync_source  :: -3 = internal,  -2 = midi, -1 = jack, 0 = none, # > 0 = loop number (1 indexed)"""
        self._set_global_parameter('sync_source', sync_source)

    def get_tap_tempo(self):
        self._get_global_parameter('tap_tempo', self.osc_server.url, '/global/tap_tempo')

    def set_tap_tempo(self, tap_tempo):
        """tap_tempo :: any changes"""
        self._set_global_parameter('tap_tempo', tap_tempo)

    def get_save_loop(self):
        self._get_global_parameter('save_loop', self.osc_server.url, '/global/save_loop')

    def set_save_loop(self, save_loop):
        """save_loop :: any change triggers quick save, be careful"""
        self._set_global_parameter('save_loop', save_loop)

    def get_select_next_loop(self):
        self._get_global_parameter('select_next_loop', self.osc_server.url, '/global/select_next_loop')

    def set_select_next_loop(self, select_next_loop):
        """select_next_loop  :: any changes"""
        self._set_global_parameter('select_next_loop', select_next_loop)

    def get_select_prev_loop(self):
        self._get_global_parameter('select_prev_loop', self.osc_server.url, '/global/select_prev_loop')

    def set_select_prev_loop(self, select_prev_loop):
        """select_prev_loop  :: any changes"""
        self._set_global_parameter('select_prev_loop', select_prev_loop)

    def get_select_all_loops(self):
        self._get_global_parameter('select_all_loops', self.osc_server.url, '/global/select_all_loops')

    def set_select_all_loops(self, select_all_loops):
        """select_all_loops   :: any changes"""
        self._set_global_parameter('select_all_loops', select_all_loops)

    def get_selected_loop_num(self):
        self._get_global_parameter('selected_loop_num', self.osc_server.url, '/global/selected_loop_num')

    def set_selected_loop_num(self, loop_num):
        """selected_loop_num   :: -1 = all, 0->N selects loop instances (first loop is 0, etc)"""
        self._set_global_parameter('selected_loop_num', loop_num)

    def get_output_midi_clock(self):
        self._get_global_parameter('output_midi_clock', self.osc_server.url, '/global/output_midi_clock')

    def set_output_midi_clock(self, output_midi_clock):
        """output_midi_clock :: 0.0 = no, 1.0 = yes"""
        self._set_global_parameter('output_midi_clock', output_midi_clock)

    ###############################
    ###
    ### LOOP ADD/REMOVE
    ###
    ###############################

    def loop_add(self, channels=2, length=60):
        """/loop_add  i:#channels  f:min_length_seconds
        adds a new loop with # channels and a minimum loop memory"""
        self.osc_client.send_message('/loop_add', type=',if', args=[channels, length])

    def loop_del(self, index):
        """/loop_del  i:loopindex
        a value of -1 for loopindex removes last loop, and is the only
        value currently recommended."""
        self.osc_client.send_message('/loop_del', type=',i', args=[index])

    ###############################
    ###
    ### SHUTDOWN
    ###
    ###############################

    def quit(self):
        """/quit
        shutdown engine"""
        self.osc_client.send_message('/quit')

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

    def register_update(self, control, return_url, return_path, loop_number=-3):
        """/sl/#/register_update  s:ctrl s:returl s:retpath"""
        self.osc_client.send_message(f'/sl/{loop_number}/register_update', [control, return_url, return_path])

    def unregister_update(self, control, return_url, return_path, loop_number=-3):
        """/sl/#/unregister_update  s:ctrl s:returl s:retpath"""
        self.osc_client.send_message(f'/sl/{loop_number}/register_update', [control, return_url, return_path])

    def register_auto_update(self, control, return_url, return_path, loop_number=-3):
        """/sl/#/register_auto_update  s:ctrl i:ms_interval s:returl s:retpath"""
        self.osc_client.send_message(f'/sl/{loop_number}/register_update', [control, return_url, return_path])

    def unregister_auto_update(self, control, return_url, return_path, loop_number=-3):
        """/sl/#/unregister_auto_update  s:ctrl s:returl s:retpath"""
        self.osc_client.send_message(f'/sl/{loop_number}/register_update', [control, return_url, return_path])

    def register_global_update(self, control, return_url, return_path):
        """/register_update  s:ctrl s:returl s:retpath"""
        self.osc_client.send_message('/register_update', [control, return_url, return_path])

    def unregister_global_update(self, control, return_url, return_path):
        """/unregister_update  s:ctrl s:returl s:retpath"""
        self.osc_client.send_message('/unregister_update', [control, return_url, return_path])

    def register_global_auto_update(self, control, return_url, return_path):
        """ /register_auto_update  s:ctrl i:ms_interval s:returl s:retpath"""
        self.osc_client.send_message('register_auto_update', [control, return_url, return_path])

    def unregister_global_auto_update(self, control, return_url, return_path):
        """/unregister_auto_update  s:ctrl s:returl s:retpath"""
        self.osc_client.send_message('/unregister_auto_update', [control, return_url, return_path])
