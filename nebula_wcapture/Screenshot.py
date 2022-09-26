from mss import mss
import cv2, os,shutil, time, pickle
import numpy as np
from multiprocessing import Process
from messages.screen_vp8enc_data import SCRN2VP8EncData


class ScreenShotProcess(Process):
    def __init__(self, out_queue, dim, logger=None):
        super(ScreenShotProcess, self).__init__()
        self.dim = dim
        self.out_queue = out_queue

        self.DEBUG = 1
        if logger:
            self.logger = logger

        self.sct = mss()

        #remove all the files in the recframes directory
        # cur_dir = os.getcwd()
        # self.recframesDir = os.path.join(cur_dir, 'recframes')
        # for filename in os.listdir(self.recframesDir):
        #     file_path = os.path.join(self.recframesDir, filename)
        #     try:
        #         if os.path.isfile(file_path) or os.path.islink(file_path):
        #             os.unlink(file_path)
        #         elif os.path.isdir(file_path):
        #             shutil.rmtree(file_path)
        #     except Exception as e:
        #         print('Failed to delete %s. Reason: %s' % (file_path, e))


    # Refresh queue data
    def update_queue(self, obj):
        if self.out_queue.full():
            try:
                self.out_queue.get_nowait()
            except:
                pass
        self.out_queue.put(obj)


    def run(self):
        frame_no = 0
        while True:
            itemstart = time.time()
            mon = {'top': self.dim[1], 'left': self.dim[0], 'width': self.dim[2], 'height': self.dim[3]}
            im = np.array(self.sct.grab(mon))
            # cv2.imwrite(self.recframesDir + '/' + str(frame_no) + '.jpg', im, [cv2.IMWRITE_JPEG_QUALITY, 100])

            #Pickle output data to out queue to be consumed by vp8 encode
            scrn_vp8enc_data = SCRN2VP8EncData(frame_no, im)
            obj = pickle.dumps(scrn_vp8enc_data)
            # Add/update queue data
            self.update_queue(obj)

            if self.DEBUG:
                req_time = (time.time()  - itemstart) * 1000
                self.logger.info("screenshot, {}, {}".format(frame_no , req_time))
                print("Screenshot: frame {}, time {}".format(frame_no, req_time))

            #next frame number
            frame_no += 1


