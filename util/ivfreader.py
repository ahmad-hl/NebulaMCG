class Frame:

    def __init__(self, nr, size, ts, framedata):
        self.nr=nr
        self.size=size
        self.ts=ts
        self.framedata=framedata

    def print_stats(self):
        print('-------------')
        print('Frame',self.nr)
        print('Size',self.size)
        print('Timestamp',self.ts)
        print('IFrame',bool(not (self.framedata[0]&1)))
        print('-------------')


class IVFReader:

    def __init__(self, filename):
        self.file=open(filename, 'rb')
        self.header=self.file.read(32)
        self.framecounter=0
        self.width = int.from_bytes(self.header[12:14],byteorder='little')
        self.height = int.from_bytes(self.header[14:16], byteorder='little')
        self.nFrames = int.from_bytes(self.header[24:28],byteorder='little')

    def print_header(self):
        print('==================')
        print('Signature',self.header[0:4].decode("utf-8"))
        print('Version',int.from_bytes(self.header[4:6],byteorder='little'))
        print('self.header length',int.from_bytes(self.header[6:8],byteorder='little'))
        print('FourCC',self.header[8:12].decode("utf-8") )
        print('Width',int.from_bytes(self.header[12:14],byteorder='little'))
        print('Height',int.from_bytes(self.header[14:16],byteorder='little'))
        print('Time Base Denumerator',int.from_bytes(self.header[16:20],byteorder='little'))
        print('Time Base Numerator',int.from_bytes(self.header[20:24],byteorder='little'))
        print('nFrames',int.from_bytes(self.header[24:28],byteorder='little'))
        print('==================')

    def get_next_frame(self):
        size=self.file.read(4)
        if len(size)<4:
            self.file.close()
            return -1
        sizeint=int.from_bytes(size, byteorder='little')
        ts=int.from_bytes(self.file.read(8), byteorder='little')
        framedata=self.file.read(int.from_bytes(size, byteorder='little'))
        frame=Frame(self.framecounter, sizeint, ts, framedata)
        self.framecounter+=1
        return frame

