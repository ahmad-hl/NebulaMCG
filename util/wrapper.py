import ctypes
from ctypes import *
from util.ivfreader import Frame,IVFReader
import numpy as np
import time

class VPXFRAMEDATA(Structure):
    _fields_=[("len",c_size_t),("buf", POINTER(c_ubyte))]


class RAWFRAMEDATA(Structure):
    _fields_=[("len",c_size_t),("buf", POINTER(c_ubyte)), ("width",c_uint),
            ("height",c_uint)] #POINTER(c_ubyte))]


class Encoder():

    DEBUG=0

    #def __init__(self, inf,width,height):
    def __init__(self, num_encoders,widths,heights,bitrates):
# Encoder
        ctypes.CDLL('/usr/lib/x86_64-linux-gnu/libvpx.so',mode=RTLD_GLOBAL)
        self.encoderlib = ctypes.CDLL('../lib/encoder.so',mode=ctypes.RTLD_GLOBAL)
# Dirty hack to pass string to the C code
        #infile=ctypes.create_string_buffer(str.encode(inf))
# Set the file in which we want to read
        #self.encoderlib.set_infile(infile.value)
# Init the encoder
        IntArray = ctypes.c_uint32 * num_encoders
        widths_array = IntArray(*widths)
        heights_array = IntArray(*heights)
        bitrates_array = IntArray(*bitrates)
        self.encoderlib.init_encoder(num_encoders,widths_array,heights_array,bitrates_array)


    def get_encoded_pkts_from_file(self):
        if(self.encoderlib.encode_frame_from_file()==-1):
            return -1
        pkts=[]
        start=time.time()
        while True:
            vpxdata=VPXFRAMEDATA()
            if not self.encoderlib.get_encoded_frame(byref(vpxdata)):
                break
            if(vpxdata.len>0):
                pkts.append(vpxdata)
        if self.DEBUG:
            print("Encoding Time",time.time()-start,"s")
        return pkts


    def get_encoded_pkts_from_data(self, data, index, kf):
        if(self.encoderlib.encode_frame_from_data(byref(data),index,kf)==-1):
            print("Error somehow")
            return -1
        pkts=[]
        start=time.time()
        while True:
            vpxdata=VPXFRAMEDATA()
            if not self.encoderlib.get_encoded_frame(byref(vpxdata),index):
                # print("Error somehow again")
                break
            if(vpxdata.len>0):
                pkts.append(vpxdata)
        if self.DEBUG:
            print("Encoding Time",time.time()-start,"s")
        return pkts

    def free_data(self,data):
        self.encoderlib.freedata(data)

class Decoder():

    DEBUG=0

    #def __init__(self, outf):
    def __init__(self):
# Decoder
        ctypes.CDLL('/usr/lib/x86_64-linux-gnu/libvpx.so',mode=RTLD_GLOBAL)
        self.decoderlib = ctypes.CDLL('../lib/decoder.so',mode=ctypes.RTLD_GLOBAL)
# Dirty hack to pass string to the C code
        #outfile=ctypes.create_string_buffer(str.encode(outf))
# Set the file in which we want to write
        #self.decoderlib.set_outfile(outfile.value)
# Init the decoder
        self.decoderlib.init_decoder()

    def decode_frame_and_write(self,frame,length):
        self.decoderlib.decode_frame_and_write(frame,length)

    def decode_pkts_and_write(self,pkts):
        start=time.time()
        for vpxdata in pkts:
            self.decoderlib.decode_frame_and_write(vpxdata.buf,vpxdata.len)
        if self.DEBUG:
            print("Decoding Time",time.time()-start,"s")

    def decode_frame_to_buf(self,frame,length):
        vpxdata=RAWFRAMEDATA()
        self.decoderlib.decode_to_buffer(frame,length,byref(vpxdata))
        return vpxdata

    def free_data(self,vpxdata):
        self.decoderlib.free_data(byref(vpxdata))
