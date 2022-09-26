import math, time, datetime
import numpy as np
from multiprocessing import Process
from queue import Queue
from util.initializer import initialize_setting
from util import PreTxUtility
from messages.FRTPpacket import FRTPpacket
from util.senderSock import SenderSock
import kodo
import threading, socket
import pickle
from statistics import mean
from util.user_events_receiver import UserEventsReceiverThread

#ffmpeg -i output.mkv -c:v libvpx -r 30 -s hd1080 -b:v 10000k  output.mp4
class RLNCencodeOffProcess(Process):
    def __init__(self, rtt_queue, user_event_queue,  logger=None, Overheadlogger=None, BWlogger = None, is_localhost=False):
        super(RLNCencodeOffProcess, self).__init__()
        self.args = initialize_setting()

        self.snderSock = SenderSock(is_localhost)

        self.DEBUG = 1
        self.rtt_queue = rtt_queue
        self.user_event_queue = user_event_queue

        if logger:
            self.logger = logger
        if Overheadlogger:
            self.Overheadlogger = Overheadlogger

        if BWlogger:
            self.BWlogger = BWlogger

        self.NetworkMonitor = 1
        if self.NetworkMonitor == 1:
            self.sync_ack_queue = Queue(maxsize=1)
        self.bw_list = []


    def parameter_tune(self, frame_no, qlevel, currRTT, bw, readers, bitrates, redundancyRate,redundancyRate_errorprop):
        readers_len = len(readers)

        if frame_no % 10 == 0:

            # Tune source rate
            ruleRTT = max(currRTT, 0.3)
            ruleRTT = 1- min(ruleRTT, 0.6)

            print("currRTT = {}, ruleRTT = {}".format(currRTT, ruleRTT))
            for ind in range(readers_len):
                if ( (bitrates[ind] )  >  bw * ruleRTT ) and (ind>0): # 70% of bw +redundancyRatek
                    qlevel = ind-1
                    break
                else:
                    qlevel = ind

        frame = readers[qlevel].get_next_frame()
        sourcerate = bitrates[qlevel]
        for i in range(readers_len):
            if i != qlevel:
                readers[i].get_next_frame()

        return frame, qlevel, sourcerate

    def run(self):

        # Thread to receive ACK on frame delivery completion from client
        if self.NetworkMonitor == 1:
            clParamsThrd = ClientParamsReceiverThread(self.sync_ack_queue)
            clParamsThrd.start()

            userThrd = UserEventsReceiverThread(self.user_event_queue)
            userThrd.start()


        start = time.time()
        clientPLR = 0
        rttList = [0.05]
        now = datetime.datetime.now()
        second_no = int('%i%i' % (now.minute, now.second))
        frame_no = 0
        fps = 30
        event = ''

        readers, bitrates = PreTxUtility.get_readers()
        qualityLevel = 8
        clientBw = 200000 #bitrates[qualityLevel]
        redundantPkts = 0
        redundantPkts_errorprop = 0
        redundancyRate = 0
        redundancyRate_errorprop = 0
        numframes = readers[0].nFrames

        symbol_size = self.args.symbol_size

        while frame_no < numframes:
            time.sleep(1/fps)

            currRTT = mean(rttList)
            if frame_no % 10 == 0:
                try:
                    recievedRTT  = self.rtt_queue.get_nowait()
                    rttList.append(recievedRTT)
                    currRTT = np.mean(rttList)
                    if len(rttList)>5:
                        rttList.pop(0)
                    # print(' Current RTT is UPDATED to {}'.format(currRTT))
                except Exception as exp:
                    # print(' Current RTT {}, no elements.., exception {}'.format(currRTT, exp))
                    pass


            #read and dump
            frame,qualityLevel,sourceRate = self.parameter_tune(frame_no, qualityLevel,currRTT, clientBw, readers, bitrates, redundancyRate, redundancyRate_errorprop)
            # frame = reader.get_next_frame()
            if self.DEBUG:
                itemstart = time.time()
                if time.time() - start > 1:
                    start = time.time()
                    now = datetime.datetime.now()
                    second_no = int('%i%i' % (now.minute, now.second))
                    redundancyRate = redundantPkts * symbol_size * 8/1024
                    redundantPkts = 0
                    redundancyRate_errorprop = redundantPkts_errorprop * symbol_size * 8/1024
                    redundantPkts_errorprop = 0


            # compute symbols based on frame and symbol_size
            data_in = bytearray(frame.framedata)

            symbols = float(len(data_in)) / symbol_size
            symbols = int(math.ceil(symbols))

            # setup kodo encoder & send settings to server side
            encoder = kodo.RLNCEncoder(
                field=kodo.field.binary8,
                symbols=symbols,
                symbol_size=symbol_size)
            encoder.set_symbols_storage(data_in)

            packet_number = 0

            # to enable AFEC, uncomment the following 2 lines
            # total_packets = max(symbols + 1, math.ceil(symbols * (1 + clientPLR))) # math.ceil(0.3 * (10- (frame_no%10)) *clientPLR))
            redundantPkts = redundantPkts + max(1, math.ceil(symbols * clientPLR))
            redundantPkts_errorprop = redundantPkts_errorprop + max(1, math.ceil(
                symbols * 0.3 * (10 - frame_no % 10) * clientPLR))
            # total_packets = symbols #No FEC
            total_packets = max(symbols + 1, 0) #math.ceil(symbols * (1 + clientPLR))

            # check if client network parameters are received
            if self.NetworkMonitor == 1:
                # Get user events
                try:
                    event_b = self.user_event_queue.get_nowait()
                    event = event_b.decode('utf-8')
                except Exception as ex:
                    event = ''
                    pass

                # Get network parameters
                try:
                    netparams = self.sync_ack_queue.get_nowait()
                    if netparams.plr == netparams.plr:
                        clientPLR = netparams.plr  # np.max(clientPLRlist)

                    if netparams.bw == netparams.bw:
                        clientBw = netparams.bw  # PreTxUtility.average_bw_list(min(netparams.bw, 8000))  # np.mean(clientBWlist) - np.std(clientBWlist)

                except Exception:
                    pass

            while packet_number < total_packets:
                packet_number += 1
                packet = encoder.produce_payload()
                curr_timestamp = time.time()
                frtpPkt = FRTPpacket(packet_number, frame_no, symbols,event, curr_timestamp, payload=packet)
                self.snderSock.sendFRTPpacket(frtpPkt)

            if self.DEBUG:
                req_time = (time.time() - itemstart) * 1000
                # process rlnc encode, frame number, time (ms)
                self.logger.info("rlncenc, {}, {}".format(frame_no, req_time))

                # second no, n , k, PLR
                seconds = math.ceil(time.mktime(datetime.datetime.today().timetuple()))
                self.Overheadlogger.info("{}, {}, {}, {}, {}, {}".format(second_no,frame_no,seconds, packet_number, symbols, clientPLR))
                if sourceRate:
                    self.BWlogger.info("{}, {}, {}, {}, {}, {}, {}, {}, {}".format(second_no, frame_no, seconds, clientBw, sourceRate,1 ,redundancyRate, packet_number-symbols, redundancyRate_errorprop))

            frame_no += 1

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
            self.update_queue(netparams)

            try:
                print("Client Network Parameters: bw {:.0f}, plr {:.4f}!".format(netparams.bw,netparams.plr))
            except:
                print('exceptiopn')
                pass


