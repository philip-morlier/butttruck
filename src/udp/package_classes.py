import sys


class Package:

    def __init__(self, sender, wav):
        self.sender = sender.to_bytes(3, 'little')
        wav_to_bytes = open(f'{wav}', 'rb')
        self.wav_header = wav_to_bytes.read(44)
        self.file = wav_to_bytes.read()
        size_in_bytes = sys.getsizeof(self.file)
        self.size_in_bytes = size_in_bytes.to_bytes(7, 'little')

    def package(self):
        return self.sender + self.size_in_bytes + self.wav_header + self.file


class ShippingHandler:

    def __init__(self, package):
        self.package = package
        self.sender = package[0:3]
        self.size_in_bytes = package[3:10]
        self.wav_header = package[10:54]
        self.file = package[54:len(package)]

    def slice(self):
        limit = 50000
        file = self.file
        size = int.from_bytes(self.size_in_bytes, byteorder='little')
        if size >= limit:
            list_of_chunks = [file[i: i + limit] for i in range(0, size, limit)]
            number_of_chunks = len(list_of_chunks).to_bytes(5, 'little')

            return number_of_chunks, list_of_chunks
        else:
            file_size = 1
            count = file_size.to_bytes(5, 'little')
            return count, file

    def enumerate(self):
        tag = int(400).to_bytes(3, 'little')
        slice_obj = self.slice()
        list_of_chunks = slice_obj[1]
        enumerated_list_of_chunks = \
            [tag + i.to_bytes(3, 'little') + list_of_chunks[i] for i in range(0, len(list_of_chunks))]
        return enumerated_list_of_chunks

    def meta(self):
        tag = int(200).to_bytes(3, 'little')
        number_of_chunks = self.slice()[0]
        meta = tag + self.sender + self.size_in_bytes + number_of_chunks + self.wav_header
        return meta
