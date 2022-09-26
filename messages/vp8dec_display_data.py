class VP8Dec2DisplayData:
    def __init__(self, frame_no, event, frame):
        self.frame_no = frame_no
        self.event = event
        self.frame = frame

    def __str__(self):
        obj_name = "frame_no : " + self.frame_no+", len:"+len(self.frame)
        return obj_name

    def printAnyPacket(self, prefix = " RLNC Dec to VP8 Dec Data Info ::"):
        print(prefix + "\n frame_no : {}, len: {}".format(self.frame_no , self.frame))