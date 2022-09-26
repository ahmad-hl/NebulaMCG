import time

from pynput import keyboard
import socket, sys
from util.initializer import initialize_setting

class UserKeyInteraction():

    def __init__(self, event_logger=None):
        super(UserKeyInteraction, self).__init__()
        if event_logger:
            self.logger = event_logger
        self.event_no = 0
        self.args = initialize_setting()
        self.address = (self.args.server_ip, self.args.user_it_port)
        self.user_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def __send(self, socket, message, address):
        if sys.version_info[0] > 2 and isinstance(message, str):
            message = bytes(message, 'utf-8')

        socket.sendto(message, address)

    def __press_callback(self, key):
        if key == keyboard.Key.esc:
            return False  # stop listener
        try:
            k = key.char  # single-char keys
        except:
            k = key.name  # other keys
        if k in ['up', 'down', 'left', 'right']:  # keys of interest
            # self.keys.append(k)  # store it in global-like variable
            # print('Key pressed: ' + k)
            ts = time.time()
            self.event_no += 1
            self.logger.info("sent,{},{},{}".format(k, self.event_no,ts))
            key_info = "{},{}".format(k,self.event_no)
            self.__send(self.user_socket, key_info, self.address)
            return False  # stop listener; remove this if want more keys

    def __release_callback(self, key):
        # print('{} released'.format(key))
        pass



    def user_key_interaction(self):
        while True:
            listener = keyboard.Listener(on_press=self.__press_callback, on_release=self.__release_callback)
            listener.start()  # start to listen on a separate thread
            listener.join()  # remove if main thread is polling self.keys



if __name__ == '__main__':
    user = UserKeyInteraction()
    user.user_key_interaction()
