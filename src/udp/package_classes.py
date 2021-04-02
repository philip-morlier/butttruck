import sys


class Package:

    def __init__(self, sender, wav):
        self.sender = sender.to_bytes(3, 'little')
        _bytes = open(f'{wav}', 'rb')
        self.header = _bytes.read(44)
        self.file = _bytes.read()
        size = sys.getsizeof(self.file)
        self.size = size.to_bytes(7, 'little')

    def package(self):
        return self.sender + self.size + self.header + self.file


class ShippingHandler:

    def __init__(self, package):
        self.package = package
        self.sender = package[0:3]
        self.size = package[3:10]
        self.header = package[10:54]
        self.file = package[54:len(package)]

    def slice(self):
        limit = 50000
        file = self.file
        size = int.from_bytes(self.size, byteorder='little')
        if size >= limit:
            _list = [file[i: i + limit] for i in range(0, size, limit)]
            count = len(_list)
            _count = count.to_bytes(5, 'little')
            return _count, _list
        else:
            file_size = 1
            _count = file_size.to_bytes(5, 'little')
            return _count, file

    def enumerate(self):
        protocol_number = 400
        tag = protocol_number.to_bytes(3, 'little')
        slice_obj = self.slice()
        _list = slice_obj[1]
        _list = [tag + i.to_bytes(3, 'little') + _list[i] for i in range(0, len(_list))]
        return _list

    def meta(self):
        protocol_number = 200
        tag = protocol_number.to_bytes(3, 'little')
        _count = self.slice()[0]
        meta = tag + self.sender + self.size + _count + self.header
        return meta



# class ReceivingHandler:
#
#     def __init__(self):
#         pass
#
#     def interpret(self, obj):
#
#
#     def translate(self, _list):
#         result = map(self.interpret, _list)
#         return list(result)
