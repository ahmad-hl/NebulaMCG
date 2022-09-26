from util.initializer import Constants

class VP8Enc2RLNCData:
    def __init__(self, frame_no, frame, frame_type = 0):
        self.frame_no = frame_no
        self.frame = frame
        self.frame_type = frame_type

    def __str__(self):
        obj_name = "frame_no : " + self.frame_no+", len:"+len(self.frame)+" , what_to_protect:"+self.what_to_protect
        return obj_name

    def printAnyPacket(self, prefix = " VP8 Encode to RLNC Encode Data Info ::"):
        print(prefix + "\n frame_no : {}, len: {}, what_to_protect: {}".format(self.frame_no , self.frame, self.what_to_protect))