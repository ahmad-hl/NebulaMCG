from pynput import keyboard
import socket, sys
from util.initializer import initialize_setting

class UserKeyInteraction():

    def __init__(self, out_queue):
        super(UserKeyInteraction, self).__init__()
        self.out_queue = out_queue

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
            self.out_queue.put(str(k).encode('utf-8'))
            return False  # stop listener; remove this if want more keys

    def __release_callback(self, key):
        # print('{} released'.format(key))
        print('')


    def user_key_interaction(self):
        while True:
            listener = keyboard.Listener(on_press=self.__press_callback, on_release=self.__release_callback)
            listener.start()  # start to listen on a separate thread
            listener.join()  # remove if main thread is polling self.keys



if __name__ == '__main__':
    user = UserKeyInteraction()
    user.user_key_interaction()
