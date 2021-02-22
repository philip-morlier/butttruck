import json
import random
import string
import subprocess
import tempfile
import time

from src.looper.sl_client import SLClient
from src.producer.ttt_producer import TTTruckProducer


class TTTruck:
    loop_dir = tempfile.mkdtemp()
    loops = 1
    loop_index = {}
    loop_parameters = {}
    deleted_loops = []

    @classmethod
    def publish_loop(cls, loop_number):
        name = cls._generate_name()
        file = cls.loop_dir + '/' + name
        cls._save_loop(loop_number, file)
        time.sleep(1)
        url = cls.upload_loop(file, name)
        msg = cls._format_msg('loop_add', name, parameters=[], url=url)
        TTTruckProducer.publish_msg(msg)

    @classmethod
    def _generate_name(cls):
        ''.join(random.choice(string.ascii_lowercase + string.digits, k=20))

    @classmethod
    def _save_loop(cls, loop_number, file):
        SLClient.save_loop(loop_number, file)

    @staticmethod
    def upload_loop(file, name):
        out, err = subprocess.Popen(['ffsend', 'upload', file, '-n', name], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    encoding='utf-8').communicate()
        if err.strip().startswith('error'):
            print(err)
        return out.strip()


    @classmethod
    def _format_msg(cls, command, name, parameters, url):
        if command == 'loop_add':
            return json.dumps({'command': command, 'name': name, 'parameters': parameters, 'url': url})



    @classmethod
    def download_loop(cls, url):
        out, err = subprocess.Popen(['ffsend', 'download', '-I', '-o', cls.loop_dir, url], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    encoding='utf-8').communicate()
        if err.strip().startswith('error'):
            print(err)
        return out.strip()

    @staticmethod
    def dispatch(msg):
        msg = json.loads(msg)
        command = msg['command']
        getattr(TTTruck, command)(msg)

    @classmethod
    def loop_add(cls, msg):
        name = msg['name']
        parameters = msg['parameters']
        url = msg['url']
        loop_file = cls.download_loop(url)
        index = cls._get_loops()
        SLClient.loop_add()
        SLClient.load_loop(index, loop_file)
        SLClient.set_quantize(3, loop_number=index)
        SLClient.set_playback_sync(1, loop_number=index)
        SLClient.pause(loop_number=index)



    @classmethod
    def _get_loops(cls):
        pass

if __name__ == '__main__':
    from src.OSC.osc_server import OSCServer
    OSCServer.start(debug=True)
    time.sleep(1)
    SLClient.ping()
    time.sleep(1)

