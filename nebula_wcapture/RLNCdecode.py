import sys, time, datetime, math
import numpy as np
from multiprocessing import Process
from util.initializer import initialize_setting
from util.receiverSock import ReceiverSock
from messages.rlnc_vp8dec_data import RLNC2VP8DecData
from messages.NPRpacket import NPRpacket
import kodo
import pickle
import socket
import logging

class RLNCdecodeProcess(Process):
    def __init__(self, out_queue, logger=None, latencylogger=None, bwlogger=None, plrlogger=None, event_logger=None):
        super(RLNCdecodeProcess, self).__init__()
        self.out_queue = out_queue

        self.args = initialize_setting()
        self.rcvrSock = ReceiverSock(self.args )

        # Init server address and socket for acknowledging frame delivery
        self.NetworkMonitor = 1
        if self.NetworkMonitor == 1:
            self.address = (self.args.server_ip, self.args.server_control_port)
            self.ack_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.DEBUG = 1
        if logger:
            self.logger = logger
        if latencylogger:
            self.latencylogger = latencylogger
        if bwlogger:
            self.bwlogger = bwlogger
        if plrlogger:
            self.plrlogger = plrlogger

    def __send(self, socket, message, address):
        if sys.version_info[0] > 2 and isinstance(message, str):
            message = bytes(message, 'utf-8')

        socket.sendto(message, address)

    def find_lost_packets(self, packet_nolist):
        max_pkt_no = np.max(packet_nolist)
        lost_packets = []
        j = 0
        i = 0
        while i <= max_pkt_no:
            while packet_nolist[j] != i:
                lost_packets.append(i)
                i += 1
            j += 1
            i += 1
        return lost_packets

    def recover_frame_data(self,frtpPacket, received_frames, frame_packet_delays):
        if not frtpPacket.frame_no in received_frames:
            received_frames[frtpPacket.frame_no] = []
            # print("new frame {} is being received...".format(frtpPacket.frame_no))
            frame_packet_delays[frtpPacket.frame_no] = []

        received_frames[frtpPacket.frame_no].append(frtpPacket)
        if len(received_frames[frtpPacket.frame_no]) == frtpPacket.symbols:
            # print("frame {} is complete.".format(frtpPacket.frame_no))
            is_complete_frame = True
            # Setup kodo decoder
            decoder = kodo.RLNCDecoder(
                field=kodo.field.binary8,
                symbols=frtpPacket.symbols,
                symbol_size=self.args.symbol_size)

            data_out = bytearray(decoder.block_size())
            decoder.set_symbols_storage(data_out)
            # print("frame {} is received, event {}".format(frtpPacket.frame_no, frtpPacket.event))

            #iterate through received packets of complete frame
            for pkt in received_frames[frtpPacket.frame_no]:
                decoder.consume_payload(pkt.payload)

            #call gc or decoder=None
            del decoder

            return is_complete_frame, data_out
        else:
            is_complete_frame = False
            return is_complete_frame, []

    def delete_lower_frames(self, received_frame_dict, frame_packet_delays, gap):
        max_frame_no = max(k for k, v in received_frame_dict.items())
        for frame_no, value in list(received_frame_dict.items()):
            if frame_no < max_frame_no - gap:
                del received_frame_dict[frame_no]
                del frame_packet_delays[frame_no]


    def compute_packetloss(self, frtpPacket, received_frame_dict):
        plr = 0.0
        try:
            curr_frame_no = frtpPacket.frame_no
            plr_frame = curr_frame_no - 1

            max_frame_no = max(k for k, v in received_frame_dict.items())
            if max_frame_no > curr_frame_no:
                if plr_frame in received_frame_dict.keys():
                    frtpkts_no_list = []
                    for frtp_pkt in received_frame_dict[plr_frame]:
                        frtpkts_no_list.append(frtp_pkt.seq_no)
                        frame_len = frtp_pkt.symbols

                    lost_pkts = abs(np.max(frtpkts_no_list) - frame_len)
                    if len(frtpkts_no_list) > 0:
                        plr = float(lost_pkts) / frame_len

                    self.plrlogger.info("{}, {}".format(plr_frame, lost_pkts))
        except Exception as exx1:
            print(" RLNCdecode (compute_plr): Exception {}".format(exx1))
            pass

        return plr

    def run(self):
        start = time.time()
        #Measure bandwidth and Packet loss rate
        plrlist=[]
        byteReceived = 0
        accFrames_delay = 0

        frtpPacket,datasize = self.rcvrSock.receiveFRTPpacket()
        frame_start_ts = time.time()
        received_frames = {}
        frame_packet_delays = {}
        mean_pkt_delay = 0.001
        gap = 5

        while True:
            # Start the timer
            itemstart = time.time()
            packetdelay = 0

            is_complete_frame, data_out = self.recover_frame_data(frtpPacket, received_frames, frame_packet_delays)

            # Remove frame packets sequences
            self.delete_lower_frames(received_frames, frame_packet_delays, gap)

            if is_complete_frame:
                rlnc_vp8_data = RLNC2VP8DecData(frtpPacket.frame_no, frtpPacket.event, data_out)
                obj = pickle.dumps(rlnc_vp8_data)
                # DO NOT Refresh queue (to avoid distortion)
                self.out_queue.put(obj)

                curr_frame_no = frtpPacket.frame_no
                while frtpPacket.frame_no == curr_frame_no:
                    #update throughput
                    byteReceived = byteReceived + datasize
                    # measure packet receiving time
                    packet_delay_start =  time.time()
                    frtpPacket,datasize = self.rcvrSock.receiveFRTPpacket()
                    packetdelay = time.time() - packet_delay_start #in seconds

                #Compute network metrics
                if len(frame_packet_delays[curr_frame_no])>2:
                    frame_packet_delays[curr_frame_no].pop()
                    mean_pkt_delay = np.mean(frame_packet_delays[curr_frame_no])

                accFrames_delay = accFrames_delay+ mean_pkt_delay+ time.time()- frame_start_ts- packetdelay
                frame_start_ts = time.time()

                if time.time() - start > 1:
                    start = time.time()
                    byteReceived_in_bits = (byteReceived / accFrames_delay) * 8 / 1024  # kbps

                    # send network performance as feedback (client report: throughput (mu), plr)
                    # if self.NetworkMonitor == 1:
                    #     if plrlist:
                    #         try:
                    #             actualplr = np.nanmean(plrlist)
                    #             plrlist = []
                    #             plrlist.append(actualplr)
                    #         except:
                    #             actualplr = 0
                    #     else:


                    actualplr = 0
                    nprPacket = NPRpacket(byteReceived_in_bits, actualplr)
                    obj = pickle.dumps(nprPacket)
                    self.__send(self.ack_socket, obj, self.address)

                    # print & reinitialize byteReceived, accFrames_delay, packet_delayList
                    try:
                        print(
                            "Net Perf: Received {} kb/s, {} B/s, plr {}, frames' delay/s {}!!".format(
                                byteReceived_in_bits, byteReceived, actualplr, accFrames_delay))
                        self.bwlogger.info("{}, {}".format(time.time()*1000, byteReceived_in_bits))
                    except:
                        pass

                    #Re-initialize
                    # accFrames_delay_2sec += accFrames_delay
                    # byteReceived_2sec += byteReceived
                    byteReceived = datasize
                    accFrames_delay = 0

                # Update & log
                req_time = (time.time() - itemstart - packetdelay) * 1000  # minus time of last packet
                self.logger.info("rlncdec, {}, {}".format(curr_frame_no, req_time))
                # print("RLNCdec: {}, {}".format(curr_frame_no, req_time))


            #NOT complete frame
            else:

                # Compute Packet Loss
                plr = self.compute_packetloss(frtpPacket, received_frames)
                plrlist.append(plr)

                # update throughput
                prev_frame_no = frtpPacket.frame_no
                byteReceived = byteReceived + datasize
                # measure packet receiving time
                packet_delay_start = time.time()
                frtpPacket, datasize = self.rcvrSock.receiveFRTPpacket()
                packetdelay = time.time() - packet_delay_start  # in seconds
                frame_packet_delays[prev_frame_no].append(packetdelay)