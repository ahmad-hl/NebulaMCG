class RLNC2VP8DecData:
    def __init__(self, frame_no, event, data_out):
        self.frame_no = frame_no
        self.event = event
        self.data_out = data_out

    def __str__(self):
        obj_name = "frame_no : " + self.frame_no+", len:"+len(self.data_out)
        return obj_name

    def printAnyPacket(self, prefix = " RLNC Dec to VP8 Dec Data Info ::"):
        print(prefix + "\n frame_no : {}, len: {}".format(self.frame_no , self.data_out))