import cv2
import numpy as np
from util.ivfreader import IVFReader
from statistics import mean
# from BuffOccup_UDP.vp8enc_packet import VP8EncPacket
import os, subprocess, time


currDir = os.path.dirname(os.path.realpath(__file__))
rootDir = os.path.abspath(os.path.join(currDir, '..'))
Video_PATH = os.path.join(rootDir, 'inout_data','ivfvideos_1min')

def start_openarena(IS_FULLHD=True):
    OPENARENA_COMMAND = 'openarena'
    if IS_FULLHD:
        OPENARENA_COMMAND = 'openarena +set r_mode -1 r_customwidth 1920 r_customheight 1080'
    else:
        OPENARENA_COMMAND = 'openarena +set r_mode -1 r_customwidth 640 r_customheight 480'

    subprocess.Popen([OPENARENA_COMMAND, ], shell=True, stdin=None, stdout=None, stderr=None, close_fds=True)

def get_readers():
    reader_176_144 = IVFReader(Video_PATH+'/res_176_144.ivf')
    reader_352_288 = IVFReader(Video_PATH+'/res_352_288.ivf')
    reader_480_270 = IVFReader(Video_PATH+'/res_480_270.ivf')
    reader_504_376 = IVFReader(Video_PATH+'/res_504_376.ivf')
    reader_640_360 = IVFReader(Video_PATH+'/res_640_360.ivf')
    reader_854_480 = IVFReader(Video_PATH+'/res_854_480.ivf')
    reader_960_540 = IVFReader(Video_PATH+'/res_960_540.ivf')
    reader_1280_720 = IVFReader(Video_PATH+'/res_1280_720.ivf')
    reader_1920_1080 = IVFReader(Video_PATH+'/res_1920_1080.ivf')
    readers = [reader_176_144, reader_352_288, reader_480_270, reader_504_376, reader_640_360, reader_854_480,
               reader_960_540, reader_1280_720, reader_1920_1080]
    bitrates = [191.14, 546.13, 696.32, 1283.4, 1365.33, 1925.12, 2116.26, 3986.773, 6976.853]  # 1 minute
    # bitrates = [314.026, 667.5, 873.8133, 1146.88, 1605.025, 2223.976, 3178.2, 4816.6, 8399.834]    #10 minutes

    return readers, bitrates

def get_maxres_reader():
    reader_1920_1080 = IVFReader(Video_PATH+'/res_1920_1080.ivf')
    return reader_1920_1080

def get_max_cv2reader():
    reader_1920_1080 = cv2.VideoCapture(Video_PATH+'/res_1920_1080.ivf')
    return reader_1920_1080

def get_capture_rates_resolutions():
    capture_bitrates = [6976853, 3986773, 1925120, 696320, 546130, 200000]
    capture_resolutions = [(1920,1080),(1280,720),(800,600),(640,480),(480,360), (176,144)]
    num_encoders = 6
    return capture_bitrates, capture_resolutions, num_encoders

def get_nebula_rates_resolutions():
    capture_bitrates = [ 3986773, 1925120, 696320, 546130, 300000]
    capture_resolutions = [(1280,720),(800,600),(640,480),(480,360), (352,288)]
    num_encoders = 5
    return capture_bitrates, capture_resolutions, num_encoders

def get_capture_TCPrate_res():
    capture_bitrate = [6976853]
    capture_resolution = [(1920,1080)]
    num_encoders = 1
    return capture_bitrate, capture_resolution,num_encoders

def get_bitrates():
    bitrates = [191.14, 546.13, 696.32, 1283.4, 1365.33, 1925.12, 2116.26, 3986.773, 6976.853]  # 1 minute
    # bitrates = [314.026, 667.5, 873.8133, 1146.88, 1605.025, 2223.976, 3178.2, 4816.6, 8399.834]    #10 minutes

    return bitrates


def average_bw_list(bw_list,  bw_value):
    bw_list.append(bw_value)
    if len(bw_list)>5:
        bw_list.pop(0)
    # print(self.bw_list)

    return mean(bw_list)

#
# # Divide vp8 encoded frame and send as packets to the client
# def divide_send_frame(snderSock, frame, frame_no, mss=1200):
#     sequence_number = 0
#     frame_len = len(frame)
#     pkt_idx = 0
#
#     while pkt_idx < frame_len:
#         if pkt_idx + mss > frame_len:
#             frame_slice = np.array(frame[pkt_idx:], dtype=np.uint8)
#         else:
#             frame_slice = np.array(frame[pkt_idx:pkt_idx + mss], dtype=np.uint8)
#
#         pkt = VP8EncPacket(sequence_number=sequence_number,frame_no=frame_no, frame_len=frame_len, data=frame_slice)
#         snderSock.sendVP8encData(pkt)
#         pkt_idx += mss
#         sequence_number = sequence_number + 1
#
#     return sequence_number, frame_len
#
#
# # Divide vp8 encoded frame and send as packets to the client
# def divide_send_frame(snderSock, frame, frame_no, event, mss=1200):
#     sequence_number = 0
#     frame_len = len(frame)
#     pkt_idx = 0
#
#     while pkt_idx < frame_len:
#         if pkt_idx + mss > frame_len:
#             frame_slice = np.array(frame[pkt_idx:], dtype=np.uint8)
#         else:
#             frame_slice = np.array(frame[pkt_idx:pkt_idx + mss], dtype=np.uint8)
#
#         pkt = VP8EncPacket(sequence_number=sequence_number,frame_no=frame_no, frame_len=frame_len, event=event, data=frame_slice)
#         snderSock.sendVP8encData(pkt)
#         pkt_idx += mss
#         sequence_number = sequence_number + 1
#
#     return sequence_number, frame_len