class DataInterpreter:

    @staticmethod
    def frame(data):
        size_in_bytes = int.from_bytes(data[6:13], 'little')
        number_of_chunks = int.from_bytes(data[13:18], 'little')
        header = data[18:62]
        dict_of_chunks = {}
        for i in range(number_of_chunks):
            dict_of_chunks[i] = None
        global wav_frame
        wav_frame = [size_in_bytes, number_of_chunks, header, dict_of_chunks]
        return wav_frame

    @staticmethod
    def match_empty_keys_to_chunks(dict_of_chunks, list_of_chunks):
        for x in dict_of_chunks:
            for i in list_of_chunks:
                if x == int.from_bytes(i[3:6], 'little'):
                    dict_of_chunks[x] = i[6: len(i)]
        return dict_of_chunks

    @staticmethod
    def insert_chunk(dict_of_chunks ,chunk):
        index = int.from_bytes(chunk[3:6], 'little')
        dict_of_chunks[index] = chunk[6:len(chunk)]

