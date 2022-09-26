import time, ctypes, pickle
import numpy as np
from util import yuv2
from multiprocessing import Process
from util.wrapper import Decoder, VPXFRAMEDATA
from messages.vp8dec_display_data import VP8Dec2DisplayData
import cv2, os
import shutil

class VP8decodeProcess(Process):
    def __init__(self,in_queue, out_queue, logger=None, event_logger=None):
        super(VP8decodeProcess, self).__init__()
        self.in_queue = in_queue
        self.out_queue = out_queue

        if logger:
            self.logger = logger
        if event_logger:
            self.event_logger = event_logger

        # log_url = 'vp8dec_info.log'
        # logging.basicConfig(filename=log_url, level=logging.DEBUG)
        # with open(log_url, 'w'):
        #     pass

    def rescale_frame(self, frame):
        width = 1920
        height = 1080
        dim = (width, height)
        if frame.shape[1]< width:
            # print('DISPLAY: Frame {} is reshaped'.format(frame_no))
            return cv2.resize(frame, dim, interpolation=cv2.INTER_AREA)
        else:
            # print('DISPLAY: Frame {} original'.format(frame_no))
            return frame

    def show_user_event(self, frame, vp8_disp_data):
        font = cv2.FONT_HERSHEY_SIMPLEX
        frame_text = " F:{} ".format(vp8_disp_data.frame_no)
        cv2.putText(frame, frame_text, (10, 80), font, 3, (0, 255, 0), 2, cv2.LINE_AA)
        event_info = vp8_disp_data.event.split(",")
        if len(event_info) == 2:
            if event_info[0] == 'up':
                # Blue color in BGR
                color = (255, 0, 0)
                coordinates = (500, 50)
                cv2.putText(frame, vp8_disp_data.event,coordinates , font, 3, color, 3, cv2.LINE_AA)
            elif event_info[0] == 'down':
                # Blue color in BGR
                color = (255, 0, 0)
                coordinates = (500, 800)
                cv2.putText(frame, vp8_disp_data.event, coordinates , font, 3, color, 3, cv2.LINE_AA)
            elif event_info[0] == 'right':
                # Yellow color in BGR
                color = (0, 255, 255)
                coordinates = (900, 500)
                cv2.putText(frame, vp8_disp_data.event, coordinates, font, 3, color, 3, cv2.LINE_AA)
            elif event_info[0] == 'left':
                # Yellow color in BGR
                color = (0, 255, 255)
                coordinates = (50, 500)
                cv2.putText(frame, vp8_disp_data.event, coordinates, font, 3, color, 3, cv2.LINE_AA)


    def run(self):
        dec = Decoder()
        do_decoding = False
        ignored_Pframes = 0

        while True:

            try:
                #enqueue frame data
                obj = self.in_queue.get()

                # Start the timer
                itemstart = time.time()

                #Decode the frame using VP8
                rlnc_vp8_data = pickle.loads(obj)
                pkt = np.frombuffer(rlnc_vp8_data.data_out, dtype=np.uint8)

                if ~do_decoding and (pkt[0] & 1) == 0:              # If it is Key Frame (I-Frame), start decoding
                    do_decoding = True

                if do_decoding:
                    try:
                        # Decode the frame
                        vpdata = VPXFRAMEDATA()
                        vpdata.buf = pkt.ctypes.data_as(ctypes.POINTER(ctypes.c_ubyte))
                        vpdata.len = len(pkt)
                        fr = dec.decode_frame_to_buf(vpdata.buf, vpdata.len)

                        if fr.len > 0:
                            ret, frame = yuv2.read(fr.buf, fr.width, fr.height)
                            if ret:
                                #Scale and display frame
                                # print("frame {} is received, event {}".format(rlnc_vp8_data.frame_no, rlnc_vp8_data.event))
                                rescaled_frame = self.rescale_frame(frame)
                                vp8_disp_data = VP8Dec2DisplayData(rlnc_vp8_data.frame_no, rlnc_vp8_data.event,
                                                                   rescaled_frame)
                                obj = pickle.dumps(vp8_disp_data)
                                self.out_queue.put(obj)
                                # self.show_user_event(rescaled_frame, rlnc_vp8_data)
                                # cv2.imshow('scaled_frame', rescaled_frame)
                                # cv2.waitKey(1)

                                if rlnc_vp8_data.event != '':  # in ['up', 'down', 'lef', 'right']:
                                    ts = time.time()
                                    self.event_logger.info("recv,{},{}".format(rlnc_vp8_data.event, ts))

                            dec.free_data(fr)
                            #log frame encoding time
                            req_time = (time.time()  - itemstart) * 1000
                            self.logger.info("vp8dec, {}, {}".format(rlnc_vp8_data.frame_no, req_time))
                    except:
                        try:
                            print('Exception in actual decoding....')
                        except:
                            pass
                        dec = Decoder()
                        pass
                else:
                    try:
                        ignored_Pframes += 1
                        print("Failed to decode as first frame is P-frame: #{}".format(ignored_Pframes))
                    except:
                        # dec = Decoder()
                        pass

            except:
                pass


