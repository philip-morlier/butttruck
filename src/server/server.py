import socketserver
import random
import pickle
import time
import json

class BuTTTruckHandler(socketserver.DatagramRequestHandler):
    peers = {}

    def handle(self):
        """Return a dict of {peer_ip : port} for all peers"""
        data = self.rfile.read()
        requester = self.client_address[0]
        requesters_peers = self.peers.get(requester, None)
        print(data)
        if requesters_peers is None:
            requesters_peers = {}
            self.peers[requester] = requesters_peers

        # Get a list of all peers that does not include the requester
        all_peers = dict(filter(lambda peer: peer[0] != requester, self.peers.items()))

        # Update the requesters peers if there are more peers available
        if all_peers != requesters_peers:
            print(self.peers)
            self._update_peers(requester, all_peers, requesters_peers)

        time_in_ms = time.monotonic() 
        response = bytes(json.dumps([time_in_ms, self.peers[requester]]), 'utf8')
        self.wfile.write(response)


    # TODO: this assumes that current_peers is always < all_peers.
    # We need to handle de-registration of peers at some point probably
    def _update_peers(self, requester, all_peers, requesters_peers):
        # Get a list of all peer IPs not in requester's peers
        missing_peers = list(filter(lambda item: item not in requesters_peers, all_peers))
        for peer in missing_peers:
            port_number = self._port_number(requester, peer)
            self.peers[requester][peer] = port_number
            self.peers[peer][requester] = port_number

    def _port_number(self, requester, peer):
        # Get a port number not already in use by the requester or their peer
        port_number = random.randint(5000, 20000)
        if port_number not in self.peers[requester].values() and port_number not in self.peers[peer].values():
            return port_number
        else:
            self._port_number(requester, peer)


if __name__ == '__main__':
    server = socketserver.ThreadingUDPServer(('0.0.0.0', 9999), BuTTTruckHandler)
    server.serve_forever()
