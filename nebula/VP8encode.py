import time, ctypes, pickle
import numpy as np
from multiprocessing import Process
from util.wrapper import Encoder, RAWFRAMEDATA
from messages.vp8enc_rlncEnc_data import VP8Enc2RLNCData
from util.initializer import Constants


class VP8encodeProcess(Process):
    def __init__(self,in_queue, out_queue, dim, logger=None):
        super(VP8encodeProcess, self).__init__()
        self.dim = dim
        self.in_queue = in_queue
        self.out_queue = out_queue

        self.DEBUG = 1
        if logger:
            self.logger = logger


    def run(self):
        enc = Encoder(self.dim[2], self.dim[3])
        frame_nolist = []
        while True:

            #Get & load image
            obj = self.in_queue.get()

            if self.DEBUG:
                itemstart = time.time()

            scrn_vp8enc_data = pickle.loads(obj)
            image = scrn_vp8enc_data.image

            #vp8 encoding logic
            data = RAWFRAMEDATA()
            data.len = len(image.ravel())
            data.buf = image.ravel().ctypes.data_as(ctypes.POINTER(ctypes.c_ubyte))
            pkts = enc.get_encoded_pkts_from_data(data)
            for pkt in pkts:
                shape = (pkt.len,)
                pktdata = np.ctypeslib.as_array(pkt.buf, shape)

                # Pickle output data to out queue to be consumed by rlnc encode
                if pktdata[0] & 1 == 0:  # If it is Key Frame (I-Frame)
                    vp8enc_rlnc_data = VP8Enc2RLNCData(scrn_vp8enc_data.frame_no, pktdata, Constants.I_FRAME)
                else:  # If it is Inter Frame (P-Frame)
                    vp8enc_rlnc_data = VP8Enc2RLNCData(scrn_vp8enc_data.frame_no, pktdata, Constants.P_FRAME)
                obj = pickle.dumps(vp8enc_rlnc_data)

                # Refresh queue data
                if self.out_queue.full():
                    try:
                        self.out_queue.get_nowait()

                    except:
                        pass
                self.out_queue.put(obj)

                if self.DEBUG:
                    req_time = (time.time()  - itemstart) *1000
                    frame_nolist.append(scrn_vp8enc_data.frame_no)
                    self.logger.info("vp8enc, {}, {}".format(scrn_vp8enc_data.frame_no , req_time))
