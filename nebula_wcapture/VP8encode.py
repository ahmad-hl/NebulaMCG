import time, ctypes, pickle, math
import numpy as np
from multiprocessing import Process
from util import PreTxUtility
from util.wrapper import Encoder, RAWFRAMEDATA
from messages.vp8enc_rlncEnc_data import VP8Enc2RLNCData
from util.initializer import Constants
import cv2, socket, threading
from util.initializer import initialize_setting
from queue import Queue


class VP8encodeProcess(Process):
    def __init__(self,in_queue, out_queue, dim, rtt_queue, logger=None):
        super(VP8encodeProcess, self).__init__()
        self.dim = dim
        self.in_queue = in_queue
        self.out_queue = out_queue
        self.rtt_queue = rtt_queue
        self.sync_ack_queue = Queue(maxsize=1)
        self.DEBUG = 1
        if logger:
            self.logger = logger

        self.GoP_len = 10
        self.NetworkMonitor = 1
        self.last_throughput = 6000
        self.last_plr = 0
        self.last_rtt = 0.1
        self.rtt_keep_list = [0.1]

        self.args = initialize_setting()


    def tune_sending_bitrate(self, rtt, throughput, bitrates, redundancyRate):
        bitrates_len = len(bitrates)
        # Tune source rate
        # rtt = rtt + 0.1
        # ruleRTT = min(rtt, 0.5)
        # ruleRTT = 1- min(ruleRTT, 0.9)
        if rtt>=1:
            ruleRTT = 0.8
        else:
            ruleRTT = rtt


        print("currRTT = {:.3f}, ruleRTT = {}, Mu = {:.3f}".format(rtt, ruleRTT, throughput))
        for ind in range(bitrates_len):
            if (bitrates[ind] / 1024  + redundancyRate) < throughput * ruleRTT:  # 70% of bw +redundancyRatek
                print("bitrates[ind] = {:.3f}, bitrate: {:.3f}, redundancyRate : {:.3f}, ruleRTT: {:.3f},  throughput * ruleRTT = {}, qlevel = {}".
                      format(bitrates[ind],bitrates[ind] / 1024, redundancyRate, ruleRTT, throughput * ruleRTT, ind))
                return ind

        ind = len(bitrates)-1
        print("OUTER: bitrates[ind] = {:.3f}, bitrate: {:.3f}, redundancyRate : {:.3f}, ruleRTT: {:.3f},  throughput * ruleRTT = {:.3f}, qlevel = {}#####".
            format(bitrates[ind], bitrates[ind] / 1024, redundancyRate, ruleRTT, throughput * ruleRTT, ind))

        return len(bitrates)-1

    # Get network round trip time RTT
    def get_netRTT(self):
        currRTT = 0
        try:
            recievedRTT = self.rtt_queue.get_nowait()
            self.rtt_keep_list.append(recievedRTT)
            currRTT = np.mean(self.rtt_keep_list)
            if len(self.rtt_keep_list) > 5:
                self.rtt_keep_list.pop(0)
            # print(' Current RTT is UPDATED to {}'.format(currRTT))
            self.last_rtt = currRTT

            return currRTT
        except:
            pass

        return self.last_rtt

    # Get network parameters
    def get_netPLR_throughput(self):
        try:
            netparams = self.sync_ack_queue.get_nowait()
            if netparams.plr == netparams.plr:
                clientPLR = netparams.plr  # np.max(clientPLRlist)

            if netparams.bw == netparams.bw:
                clientBw = netparams.bw  # PreTxUtility.average_bw_list(min(netparams.bw, 8000))  # np.mean(clientBWlist) - np.std(clientBWlist)
            self.last_throughput = clientBw
            self.last_plr = clientPLR
            return clientBw, clientPLR
        except Exception:
            pass
        # print("get_netPLR_throughput: {},{}".format(self.last_throughput , self.last_plr))

        return self.last_throughput , self.last_plr

    def run(self):

        # Thread to receive ACK on frame delivery completion from client
        if self.NetworkMonitor == 1:
            clParamsThrd = ClientParamsReceiverThread(self.sync_ack_queue, args=self.args)
            clParamsThrd.start()

        start_time = time.time()
        start = time.time()
        bitrates, resolutions,num_encoders = PreTxUtility.get_nebula_rates_resolutions()
        widths = [r[0] for r in resolutions]
        heights = [r[1] for r in resolutions]

        enc = Encoder(num_encoders,widths,heights, bitrates)
        redundantPkts = 0
        redundancyRate = 0
        encindex=2
        force_keyframe = 0
        print(" initialize vp8 encoder:{}".format((time.time() - start_time)*1000))

        while True:

            #Get & load image
            obj = self.in_queue.get()

            itemstart = time.time()

            scrn_vp8enc_data = pickle.loads(obj)
            im = scrn_vp8enc_data.image
            im2 = cv2.resize(im, resolutions[encindex])
            image = cv2.cvtColor(im2, cv2.COLOR_BGRA2YUV_I420, 1)  # 2

            #vp8 encoding logic
            data = RAWFRAMEDATA()
            data.len = len(image.ravel())
            data.buf = image.ravel().ctypes.data_as(ctypes.POINTER(ctypes.c_ubyte))
            pkts = enc.get_encoded_pkts_from_data(data,encindex,force_keyframe)
            force_keyframe = 0
            for pkt in pkts:

                shape = (pkt.len,)
                pktdata = np.ctypeslib.as_array(pkt.buf, shape)

                # Pickle output data to out queue to be consumed by rlnc encode
                if pktdata[0] & 1 == 0:  # If it is Key Frame (I-Frame)
                    vp8enc_rlnc_data = VP8Enc2RLNCData(scrn_vp8enc_data.frame_no, pktdata, Constants.I_FRAME)
                else:  # If it is Inter Frame (P-Frame)
                    vp8enc_rlnc_data = VP8Enc2RLNCData(scrn_vp8enc_data.frame_no, pktdata, Constants.P_FRAME)

                redundantPkts = redundantPkts + max(1,  0) #math.ceil(symbols * clientPLR)

                # Put new queue data
                obj = pickle.dumps(vp8enc_rlnc_data)
                try:
                    if self.out_queue.full():
                        try:
                            self.out_queue.get_nowait()
                        except:
                            pass
                    self.out_queue.put_nowait(obj)
                except:
                    print("Boooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooom")
                    pass


                if self.DEBUG:
                    req_time = (time.time()  - itemstart) *1000
                    self.logger.info("vp8enc, {}, {}".format(scrn_vp8enc_data.frame_no , req_time))
                    print("VP8 enc: frame {}, time {}".format(scrn_vp8enc_data.frame_no, req_time))


            # Get network conditions (RTT, Mu, loss)
            currRTT = self.get_netRTT()
            throughput, clientPLR = self.get_netPLR_throughput()
            res_index = self.tune_sending_bitrate(currRTT,throughput,bitrates, redundancyRate)

            if time.time() - start>1:
                encindex = res_index
                force_keyframe=1
                start = time.time()
                redundancyRate = redundantPkts * 1200 * 8 / 1024 #symbol_size=1200
                redundantPkts = 0


class ClientParamsReceiverThread(threading.Thread):

    def __init__(self, sync_ack_queue, args):
        super(ClientParamsReceiverThread, self).__init__()
        self.sync_ack_queue = sync_ack_queue
        self.args = args
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
            self.update_queue(netparams)

            try:
                print("Client Network Parameters: bw {:.0f}, plr {:.4f}!".format(netparams.bw,netparams.plr))
            except:
                print('exceptiopn')
                pass


