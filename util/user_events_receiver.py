from util.initializer import initialize_setting
import threading, socket

class UserEventsReceiverThread(threading.Thread):

    def __init__(self, user_event_queue=None):
        super(UserEventsReceiverThread, self).__init__()
        self.user_event_queue = user_event_queue
        args = initialize_setting()
        self.user_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.user_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.user_socket.bind((args.server_ip, args.user_it_port))
        print('user interaction socket {} , {}'.format(args.server_ip, args.user_it_port))

    def stop(self):
        self.user_socket.close()

    def update_queue(self, key):
        # Refresh queue data
        try:
            self.user_event_queue.put(key)
        except:
            pass

    def run(self):
        while True:
            # receive User's event
            event = self.user_socket.recv(1024)
            self.update_queue(event)

            try:
                print("User raised an event << {} >>!".format(event.decode('utf-8')))
            except:
                print('exception')
                pass
