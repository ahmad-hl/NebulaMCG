import cv2, time, pickle
from multiprocessing import Process
import os, csv

class PSNRcomputeProcess(Process):
    def __init__(self,in_queue):
        super(PSNRcomputeProcess, self).__init__()
        self.in_queue = in_queue
        self.get_reader()

    def computePSNR(self, vp8_disp_data, compressed_frame, curr_frame_ptr):
        # Loading images (original image and compressed image)
        while curr_frame_ptr <= vp8_disp_data.frame_no:
            print("frame_no {}, curr frame ptr {}".format(vp8_disp_data.frame_no, curr_frame_ptr))
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

    def get_reader(self):
        currDir = os.path.dirname(os.path.realpath(__file__))
        rootDir = os.path.abspath(os.path.join(currDir, '..'))
        self.reader_1920_1080 = cv2.VideoCapture(rootDir + '/MCGserver/ivfvideos_1min/res_1920_1080.ivf')

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
        # frame_text = " {} : {}".format(gop_vp8_disp_data.gop_no, gop_vp8_disp_data.frame_no)
        # cv2.putText(frame100, frame_text, (10, 80), font, 3, (0, 255, 0), 2, cv2.LINE_AA)
        if vp8_disp_data.event != '':
            if vp8_disp_data.event == 'up':
                # Blue color in BGR
                color = (255, 0, 0)
                coordinates = (500, 50)
                cv2.putText(frame, vp8_disp_data.event,coordinates , font, 3, color, 3, cv2.LINE_AA)
            elif vp8_disp_data.event == 'down':
                # Blue color in BGR
                color = (255, 0, 0)
                coordinates = (500, 800)
                cv2.putText(frame, vp8_disp_data.event, coordinates , font, 3, color, 3, cv2.LINE_AA)
            elif vp8_disp_data.event == 'right':
                # Yellow color in BGR
                color = (0, 255, 255)
                coordinates = (900, 500)
                cv2.putText(frame, vp8_disp_data.event, coordinates, font, 3, color, 3, cv2.LINE_AA)
            elif vp8_disp_data.event == 'left':
                # Yellow color in BGR
                color = (0, 255, 255)
                coordinates = (50, 500)
                cv2.putText(frame, vp8_disp_data.event, coordinates, font, 3, color, 3, cv2.LINE_AA)


    def show_event_gopframe_no(self, frame, vp8_disp_data):
        font = cv2.FONT_HERSHEY_SIMPLEX
        frame_text = " {} ".format(vp8_disp_data.frame_no)
        cv2.putText(frame, frame_text, (10, 80), font, 3, (0, 255, 0), 2, cv2.LINE_AA)
        self.show_user_event(frame, vp8_disp_data)

    def run(self):
        second = 0
        curr_frame_ptr = 0
        #init readers
        framepsnr_dict = {}
        while True:
            try:
                obj = self.in_queue.get()
                vp8_disp_data = pickle.loads(obj)
                rescaled_frame = self.rescale_frame(vp8_disp_data.frame,vp8_disp_data.frame_no)
                # self.show_user_event(rescaled_frame, vp8_disp_data)
                # cv2.imshow('scaled_frame', rescaled_frame)
                # cv2.waitKey(1)
                # cv2.imwrite(self.recframesDir + '/' + str(vp8_disp_data.frame_no) + '.jpg', vp8_disp_data.frame, [cv2.IMWRITE_JPEG_QUALITY, 100])

                framepsnr = self.computePSNR(vp8_disp_data, rescaled_frame, curr_frame_ptr)
                print("PSNR of frame {}: {}".format(vp8_disp_data.frame_no, framepsnr))
                curr_frame_ptr = vp8_disp_data.frame_no + 1
                framepsnr_dict[vp8_disp_data.frame_no] = framepsnr

            except:
                with open('psnr.csv', 'w') as f:
                    for key in framepsnr_dict.keys():
                        f.write("%s,%s\n" % (key, framepsnr_dict[key]))
                # print("Exception in frame {}".format(vp8_disp_data.frame_no))
                self.terminate()




