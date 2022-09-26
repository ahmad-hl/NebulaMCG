import sys
import pickle
import socket
from util.initializer import initialize_setting

class ServerRTTPSenderSock:
    def __init__(self, is_localhost=True):
        args = initialize_setting()

        #update IPs
        if is_localhost:
            args.server_ip = 'localhost'  # 192.168.40.206
            args.client_ip = 'localhost'
        self.settings = vars(args)

        # Init client address and its socket
        self.address = (args.client_ip, args.client_report_port)
        self.server_report_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # self.server_report_socket.settimeout(0.5) #timeout 0.5 s = 500ms

        print('socket to reporting client is init {} , {}'.format(args.client_ip, args.client_report_port))

    def sendRTTPpacket(self, rttpPacket):
        obj = pickle.dumps(rttpPacket)
        self.__send(self.server_report_socket, obj, self.address)

    def receiveRTTPpacket(self):
        obj = self.server_report_socket.recv(1024)
        rttpPacket = pickle.loads(obj)
        return  rttpPacket

    def close(self):
        self.server_report_socket.close()

    def __send(self, socket, message, address):
        """
        Send message to address using the provide socket.
        Works for both python2 and python3
        """
        # Convert str message to bytes on Python 3+
        if sys.version_info[0] > 2 and isinstance(message, str):
            message = bytes(message, 'utf-8')

        socket.sendto(message, address)

    def __receive(self, socket, number_of_bytes):
        """
        Receive an amount of bytes.
        Works for both python2 and python3
        """
        data, address = socket.recvfrom(number_of_bytes)
        if sys.version_info[0] > 2 and isinstance(data, bytes):
            return str(data, 'utf-8'), address

        return data, address

