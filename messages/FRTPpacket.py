# FEC Forward Recovery Realtime Transport Protocol Packet
# FEC-enabled RTP - FRTP packet

class FRTPpacket:
    def __init__(self, seq_no, frame_no, symbols, event, timestamp=None, payload=None):
        self.seq_no = seq_no
        self.frame_no = frame_no
        self.symbols = symbols
        self.event = event
        self.timestamp = timestamp
        self.payload = payload

    def set_payload(self, RLNCpacket):
        self.payload = RLNCpacket

    def set_start_ts(self, timestamp):
        self.timestamp = timestamp

    def __str__(self):
        obj_name = "Seq No:" + str(self.sequence_no)
        obj_name += ", Frame No:" + str(self.frame_no)
        obj_name += ", symbols: " + str(self.symbols)
        obj_name += ", timestamp: " + str(self.timestamp)
        return obj_name

    def printPacket(self, prefix = " Packet Info::"):
        obj_name = "Seq No:" + str(self.sequence_no)
        obj_name += "Frame No:" + str(self.frame_no)
        obj_name += " , symbols: " + str(self.symbols)
        obj_name += ", timestamp: " + str(self.timestamp)
        obj_name += " , payload length: " + str(len(self.payload)) + "\n"
        print(prefix+"\n", obj_name)


