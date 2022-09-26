import sys, socket
import pickle

class ClientRTTPReceiverSock:
    def __init__(self, args):
        self.args = args
        # Set data packets receiving sockets
        self.client_report_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client_report_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.client_report_socket.bind(('', args.client_report_port))

    def receiveRTTPpacket(self):
        obj, address = self.client_report_socket.recvfrom(1024)
        rttpPacket = pickle.loads(obj)

        return rttpPacket,address

    def sendRTTPpacket(self, rttpPacket,address):
        obj = pickle.dumps(rttpPacket)
        self.__send(self.client_report_socket, obj, address)

    def close(self):
        self.client_report_socket.close()

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