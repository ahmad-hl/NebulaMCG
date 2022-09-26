class SCRN2VP8EncData:
    def __init__(self, frame_no, image):
        self.frame_no = frame_no
        self.image = image

    def __str__(self):
        obj_name = "frame_no : " + self.frame_no+", len:"+len(self.image)
        return obj_name

    def printAnyPacket(self, prefix = " Screenshot to VP8 Enc Data Info ::"):
        print(prefix + "\n frame_no : {}, len: {}".format(self.frame_no , self.image))