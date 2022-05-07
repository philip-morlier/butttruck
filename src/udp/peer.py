import socket
import logging


class Peer(socket.socket):
    def __init__(self, addr, x, y, server):
        super().__init__(x, y)
        self.address = addr
        self.server = server
        self.receiving_status = {}
        self.sending_status = {}
        self.waiting_ack = set()
        self.is_ready = False

    def get_address(self):
        return self.address

    def is_server(self):
        return self.server

    def set_receiving_status(self, status):
        self.receiving_status = status

    def update_receiving_status(self, state):
        for k, v in state.items():
            self.receiving_status[k] = v
        self.is_ready = True

    def clear_receiving_status(self, loop):
        if self.receiving_status.get(loop, None) is not None:
            self.receiving_status.pop(loop)

    def get_receiving_status(self):
        return self.receiving_status

    def update_sending_status(self, loop, chunk):
        try:
            self.sending_status[loop].remove(chunk)
        except ValueError:
            logging.debug(f'Chunk: {chunk} not in sending_status')
        finally:
            return len(self.sending_status.get(loop, [1])) == 0

    def set_sending_status(self, loop, status):
        self.sending_status[loop] = status

    def clear_sending_status(self, loop):
        if self.sending_status.get(loop, None) is not None:
            self.sending_status.pop(loop)

    def get_sending_status(self):
        return self.sending_status
