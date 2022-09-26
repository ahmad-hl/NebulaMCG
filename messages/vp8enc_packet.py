class VP8EncPacket:
    def __init__(self, sequence_number, frame_no, frame_len, data):
        self.sequence_number = sequence_number
        self.frame_no = frame_no
        self.frame_len = frame_len
        self.data = data
