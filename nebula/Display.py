import cv2, time, pickle
from multiprocessing import Process
import os, csv,shutil
from util import PreTxUtility
from messages.vp8dec_display_data import VP8Dec2DisplayData

class DisplayProcess(Process):
    def __init__(self,in_queue, logger=None, fpslogger=None):
        super(DisplayProcess, self).__init__()
        self.in_queue = in_queue

        self.DEBUG = 0
        if logger:
            self.logger = logger
        if fpslogger:
            self.fpslogger = fpslogger

        parentDir = os.path.dirname(os.path.realpath(__file__))
        psnr_log_path = os.path.join(parentDir,'..', 'inout_data', 'nebula_psnr.log')
        self.log_psnr_file = open(psnr_log_path, 'w')


    def computePSNR(self, frame_no, compressed_frame, curr_frame_ptr, vp8_disp_data =None):

        # Loading images (original image and compressed image)
        while curr_frame_ptr <= frame_no:
            print("frame_no {}, curr frame ptr {}".format(frame_no, curr_frame_ptr))
            success, original_1920_1080 = self.reader_1920_1080.read()
            curr_frame_ptr += 1

        if success:
            original = original_1920_1080
            framepsnr = cv2.PSNR(original, compressed_frame)
            # cv2.imshow('original', original)
            # self.show_user_event( compressed_frame, vp8_disp_data)
            # cv2.imshow('compressed', compressed_frame)
            # cv2.waitKey(1)
        else:
            framepsnr = 1

        return framepsnr


    def rescale_frame(self, frame, frame_no, percent=100):
        width = 1920 #int(frame.shape[1] * percent / 100)
        height = 1080 #int(frame.shape[0] * percent / 100)
        dim = (width, height)
        if frame.shape[1]< width:
            # print('DISPLAY: Frame {} is reshaped'.format(frame_no))
            return cv2.resize(frame, dim, interpolation=cv2.INTER_AREA)
        else:
            # print('DISPLAY: Frame {} original'.format(frame_no))
            return frame

    def show_user_event(self, frame, vp8_disp_data):
        font = cv2.FONT_HERSHEY_SIMPLEX
        frame_text = " F: {}".format(vp8_disp_data.frame_no)
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
        start = time.time()
        second = 0
        curr_frame_ptr = 0
        #init readers
        self.reader_1920_1080 = PreTxUtility.get_max_cv2reader()
        while True:
            # try:
            obj = self.in_queue.get()
            vp8_disp_data = pickle.loads(obj)

            if self.DEBUG:
                itemstart = time.time()
                if time.time() - start > 1:
                    start = time.time()
                    second += 1

            rescaled_frame = self.rescale_frame(vp8_disp_data.frame,vp8_disp_data.frame_no)
            framepsnr = self.computePSNR(vp8_disp_data.frame_no, rescaled_frame, curr_frame_ptr, vp8_disp_data)
            print("PSNR of frame {}: {}".format(vp8_disp_data.frame_no, framepsnr))
            # log frame_no, PSNR
            self.log_psnr_file.write(str(vp8_disp_data.frame_no) + '\t' + str(framepsnr) + '\n')
            self.log_psnr_file.flush()

            curr_frame_ptr = vp8_disp_data.frame_no + 1
            self.show_user_event(rescaled_frame, vp8_disp_data)
            cv2.imshow('rescaled_frame', rescaled_frame)
            key = cv2.waitKey(1) & 0xFF

            # if the q key was pressed, break from the loop
            if key == ord("q"):
                cv2.destroyAllWindows()
                break

            if vp8_disp_data.frame_no >= 1799:
                cv2.destroyAllWindows()
                break

            if self.DEBUG:
                req_time = (time.time() - itemstart) * 1000
                self.logger.info("display, {}, {}".format(vp8_disp_data.frame_no, req_time))
                self.fpslogger.info("{},{},{}".format(second, vp8_disp_data.frame_no, req_time))






