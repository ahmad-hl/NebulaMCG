from multiprocessing import Process, Queue
from util.initializer import initialize_setting
from messages.FRTPpacket import FRTPpacket
from util.senderSock import SenderSock
import kodo
import pickle, time, datetime, math
from util.user_events_receiver import UserEventsReceiverThread


class RLNCencodeProcess(Process):
    def __init__(self, in_queue,  user_event_queue, logger=None, Overheadlogger=None, FEClogger=None, is_localhost=False):
        super(RLNCencodeProcess, self).__init__()
        self.in_queue = in_queue
        self.user_event_queue = user_event_queue
        args = initialize_setting()
        self.settings = vars(args)

        self.snderSock = SenderSock(is_localhost)

        self.DEBUG = 1

        if logger:
            self.logger = logger
        if Overheadlogger:
            self.Overheadlogger = Overheadlogger
        if FEClogger:
            self.FEClogger = FEClogger

        self.NetworkMonitor = 1
        if self.NetworkMonitor == 1:
            self.sync_ack_queue = Queue(maxsize=1)


    def run(self):

        # Thread to receive ACK on frame delivery completion from client
        if self.NetworkMonitor == 1:
            userThrd = UserEventsReceiverThread(self.user_event_queue)
            userThrd.start()

        start = time.time()
        clientPLR = 0
        redundancyRate = 0
        now = datetime.datetime.now()
        second_no = int('%i%i' % (now.minute, now.second))
        event = ''

        while True:

            # restart the time evrey second
            if self.DEBUG:
                itemstart = time.time()
                if time.time() - start > 1:
                    start = time.time()
                    now = datetime.datetime.now()
                    second_no = int('%i%i' % (now.minute, now.second))

            #Get vp8 encoded frame
            obj = self.in_queue.get()
            vp8enc_rlnc_data = pickle.loads(obj)
            frame = vp8enc_rlnc_data.frame

            # compute symbols based on frame and symbol_size
            data_in = bytearray(frame)
            symbol_size = self.settings['symbol_size']
            max_redundancy = self.settings['max_redundancy']

            symbols = float(len(data_in)) / symbol_size
            symbols = int(math.ceil(symbols))

            # setup kodo encoder & send settings to server side
            encoder = kodo.RLNCEncoder(
                field=kodo.field.binary8,
                symbols=symbols,
                symbol_size=symbol_size)
            encoder.set_symbols_storage(data_in)

            # to enable AFEC, uncomment the following 2 lines
            fw = 1 #0.3 * (10 - vp8enc_rlnc_data.frame_no % 10)
            total_packets = symbols #max(symbols +1, math.ceil(symbols  * (1+  clientPLR *fw  )))
            packet_number = 0
            while packet_number < total_packets:
                packet_number += 1
                packet = encoder.produce_payload()
                curr_timestamp = time.time()
                frtpPkt = FRTPpacket(packet_number, vp8enc_rlnc_data.frame_no, symbols, event, curr_timestamp, payload=packet)
                self.snderSock.sendFRTPpacket(frtpPkt)


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
                # try:
                #     netparams = self.sync_ack_queue.get_nowait()
                #     print(" Consumed Parameters".format(netparams))
                #     if netparams.plr == netparams.plr:
                #         clientPLR = netparams.plr  # np.max(clientPLRlist)
                #
                #     if netparams.bw == netparams.bw:
                #         clientBw = netparams.bw  # PreTxUtility.average_bw_list(min(netparams.bw, 8000))  # np.mean(clientBWlist) - np.std(clientBWlist)
                #
                # except Exception:
                #     pass


            if self.DEBUG:
                req_time = (time.time()  - itemstart) *1000
                # process rlnc encode, frame number, time (ms)
                self.logger.info("rlncenc, {}, {}".format(vp8enc_rlnc_data.frame_no, req_time))

                # second no, n , k, PLR
                seconds = math.ceil(time.mktime(datetime.datetime.today().timetuple()))
                self.Overheadlogger.info(
                    "{}, {}, {}, {}, {}, {}".format(second_no, vp8enc_rlnc_data.frame_no, seconds, packet_number, symbols, clientPLR))
                # if sourceRate:
                #     self.BWlogger.info(
                #         "{}, {}, {}, {}, {}, {}, {}, {}".format(second_no, frame_no, seconds, clientBw, sourceRate,
                #                                                     1, redundancyRate, packet_number - symbols))
                print("RLNCenc: frame {}, time {}".format(vp8enc_rlnc_data.frame_no, req_time))



