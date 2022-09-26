import sys, socket

import pickle

class ReceiverSock:
    def __init__(self, args):
        self.args = args
        # Set data packets receiving sockets
        self.data_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.data_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.data_socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 67108864)
        self.data_socket.bind(('', args.data_port))

    def receiveFRTPpacket(self):
        obj, address = self.data_socket.recvfrom(self.args.symbol_size + 300)
        datasize = sys.getsizeof(obj)  # + 14 + 24 + 8 size of UDP header = 8 Bytes
        frtpPacket = pickle.loads(obj)

        return frtpPacket,datasize

    def receiveVP8encData(self):
        obj = self.data_socket.recv(4048)
        datasize = sys.getsizeof(obj)  # + 14 + 24 + 8 size of UDP header = 8 Bytes
        vp8encData = pickle.loads(obj)
        return vp8encData, datasize

    def __send(self, socket, message, address):
        # Convert str message to bytes on Python 3+
        if sys.version_info[0] > 2 and isinstance(message, str):
            message = bytes(message, 'utf-8')

        socket.sendto(message, address)

    def __receive(self, socket, number_of_bytes):
        # Receive an amount of bytes.
        data, address = socket.recvfrom(number_of_bytes)
        if sys.version_info[0] > 2 and isinstance(data, bytes):
            return str(data, 'utf-8'), address

        return data, address