
class DataInterpreter:

    # def __init__(self, data):
    #     self.data = data



    # def interpret(self):
    #     data = self.data
    #     tag = data[0:3]
    #     if tag == 100:
    #         pass
    #     if tag == 200:
    #         if len(data) == 62:
    #             self.frame()
    #         else:
    #             pass
    #     if tag == 300:
    #         pass
    #     if tag == 400:
    #         pass
    @staticmethod
    def frame(data):
        size = data[6:13]
        _size = int.from_bytes(size, 'little')
        count = data[13:18]
        _count = int.from_bytes(count, 'little')
        header = data[18:62]
        _frame = {}
        for i in range(_count):
            _frame[i] = None
        global wav_frame
        wav_frame = [_size, _count, header, _frame]
        return wav_frame

    @staticmethod
    def match(_dict, _list):
        for x in _dict:
            for i in _list:
                if x == int.from_bytes(i[3:6], 'little'):
                    _dict[x] = i[6: len(i)]


    def test_pass(self):
        test = self.frame
        print(test)
