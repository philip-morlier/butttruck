import socket

class Peer(socket.socket):
    def __init__(self, addr, x, y, server):
        super().__init__(x, y)
        self.address = addr
        self.server = server
        self.receiving_status = {}
        self.sending_status = {}
        self.waiting_ack = set()

    def get_address(self):
        return self.address

    def is_server(self):
        return self.server

    def set_receiving_status(self, status):
        self.receiving_status = status

    def update_receiving_status(self, state):
        # for k,v in state.items():
        #     self.receiving_status[k] = v
        self.receiving_status = state

    def clear_receiving_status(self, loop):
        self.receiving_status.pop(loop)

    def get_receiving_status(self):
        return self.receiving_status

    def update_sending_status(self, loop, chunk):
        try:
            self.sending_status[loop].remove(chunk + 1)
        except Exception as e:
            print('Update sending ', e)
            return False
        return len(self.sending_status.get(loop,1)) == 0

    def set_sending_status(self, loop, status):
        self.sending_status[loop] = status

    def clear_sending_status(self, loop):
        self.sending_status.pop(loop)

    def get_sending_status(self):
        return self.sending_status
