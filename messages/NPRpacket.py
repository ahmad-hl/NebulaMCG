# Network Performance/Parameters Report Packet -NPRpacket
#Client Feedback report about network performance

class NPRpacket:
    def __init__(self, bw, plr):
        self.bw = bw
        self.plr = plr

    def __str__(self):
        obj_name = "bw: " + self.bw
        obj_name += ",plr: " + self.plr
        return obj_name

