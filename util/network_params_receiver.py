from util.initializer import initialize_setting
import threading, socket
import pickle

class ClientParamsReceiverThread(threading.Thread):

    def __init__(self, sync_ack_queue):
        super(ClientParamsReceiverThread, self).__init__()
        self.sync_ack_queue = sync_ack_queue
        self.args = initialize_setting()
        self.control_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.control_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.control_socket.bind((self.args.server_ip, self.args.server_control_port))
        print('feedback socket info {} , {}'.format(self.args.server_ip, self.args.server_control_port))

    def stop(self):
        self.control_socket.close()

    def update_queue(self, netparams):
        # Refresh queue data
        try:
            if self.sync_ack_queue.full():
                try:
                    self.sync_ack_queue.get_nowait()
                except:
                    pass

            self.sync_ack_queue.put(netparams)
        except:
            pass

    def run(self):
        while True:
            # receive Client's Network Parameters
            obj = self.control_socket.recv(1024)
            netparams = pickle.loads(obj)
            netparams.bw = netparams.bw
            self.update_queue(netparams)

            try:
                print("Client Network Parameters: bw {:.0f}, plr {:.4f}!".format(netparams.bw,netparams.plr))
            except:
                print('exceptiopn')
                pass
