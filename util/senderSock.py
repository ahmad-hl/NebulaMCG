import math
import time, sys, json
import pickle
import socket
from util.initializer import initialize_setting

class SenderSock:
    def __init__(self, is_localhost=False):
        args = initialize_setting()

        #update IPs
        if is_localhost:
            args.server_ip = 'localhost'  # 192.168.40.206
            args.client_ip = 'localhost'

        # Init client address and its socket
        self.address = (args.client_ip, args.data_port)
        #print("Sender socket: %s, %s" % (args.client_ip, args.data_port))
        self.send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.send_socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 64000000)

    def sendFRTPpacket(self, FRTPpacket):
        obj = pickle.dumps(FRTPpacket)
        self.__send(self.send_socket, obj, self.address)

    def sendVP8encData(self, vp8packet):
        obj = pickle.dumps(vp8packet)
        self.__send(self.send_socket, obj, self.address)

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

