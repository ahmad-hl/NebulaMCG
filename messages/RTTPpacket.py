# Server Report Packet
# SR packet

class RTTPpacket:

    def __init__(self, seq_no,sent_ts):
        self.seq_no = seq_no
        self.sent_ts = sent_ts

    def __str__(self):
        obj_name = "seq_no:" + str(self.seq_no)
        obj_name += "sent_ts:" + str(self.sent_ts)

        return obj_name

