from multiprocessing import Process
from util.initializer import initialize_setting
from RTTProbing.ClientRTTPReceiverSock import ClientRTTPReceiverSock

class RTTProbingClient(Process):
    def __init__(self):
        super(RTTProbingClient, self).__init__()
        args = initialize_setting()
        self.settings = vars(args)

        self.rttProbingSock = ClientRTTPReceiverSock(args)

    def run(self):

        while True:
            rttpPacket,address = self.rttProbingSock.receiveRTTPpacket()
            # print('seconds {}, ts {}'.format(rttpPacket.sec, rttpPacket.ts))
            self.rttProbingSock.sendRTTPpacket(rttpPacket,address)

    def stop(self):
        self.rttProbingSock.close()

