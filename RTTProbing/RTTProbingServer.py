import time, math
from datetime import datetime
import socket
from multiprocessing import Process
from util.initializer import initialize_setting
from RTTProbing.ServerRTTPSenderSock import ServerRTTPSenderSock
from messages.RTTPpacket import RTTPpacket
import threading

class RTTProbingServer(Process):
    def __init__(self, rtt_queue, RTTlogger=None):
        super(RTTProbingServer, self).__init__()
        args = initialize_setting()
        self.settings = vars(args)

        self.rtt_queue = rtt_queue
        if RTTlogger:
            self.RTTlogger = RTTlogger

    def run(self):

        self.serverRTTPSock = ServerRTTPSenderSock(False)
        self.rttpSenderThread = RTTPSenderThread(self.serverRTTPSock)
        self.rttpSenderThread.start()

        self.rttpReceiverThread = RTTPReceiverThread(self.serverRTTPSock, self.rtt_queue, self.RTTlogger)
        self.rttpReceiverThread.start()

        self.rttpSenderThread.join()
        self.rttpReceiverThread.join()

    def stop(self):
        self.serverRTTPSock.close()
        self.rttpReceiverThread.stop()
        self.rttpSenderThread.stop()



class RTTPSenderThread(threading.Thread):

    def __init__(self, serverRTTPSock):
        super(RTTPSenderThread, self).__init__()
        self.serverRTTPSock = serverRTTPSock

    def run(self):

        start_ts = time.time()
        sequence_no = 1
        while True:
            if time.time() - start_ts > 0.5:
                start_ts = time.time()
                # seconds = math.ceil(time.mktime(datetime.datetime.today().timetuple()))
                rttpPkt = RTTPpacket(sequence_no,time.time())

                # Send a RTT Probing packet
                self.serverRTTPSock.sendRTTPpacket(rttpPkt)
                sequence_no += 1

class RTTPReceiverThread(threading.Thread):

    def __init__(self, serverRTTPSock, rtt_queue, RTTlogger):
        super(RTTPReceiverThread, self).__init__()
        self.serverRTTPSock = serverRTTPSock
        self.rtt_queue = rtt_queue
        self.RTTlogger = RTTlogger

    def update_RTTqueue(self, rtt):
        try:
            if self.rtt_queue.full():
                self.rtt_queue.get_nowait()
            self.rtt_queue.put(rtt)
        except:
            try:
                self.rtt_queue.get_nowait()
                self.rtt_queue.put(rtt)
            except:
                pass
            pass

    def run(self):
        while True:
            # Receive a RTT Probing response packet
            try:
                rttpPacket = self.serverRTTPSock.receiveRTTPpacket()

                # receive_ts = time.time()
                rtt = time.time() - rttpPacket.sent_ts
                self.update_RTTqueue(rtt)
                seconds = math.ceil(time.mktime(datetime.today().timetuple()))
                self.RTTlogger.info(
                    "{}, {}, {}".format(seconds, rttpPacket.sent_ts, rtt*1000))

            except socket.timeout as e:
                print(e)
                pass