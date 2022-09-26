import csv
import os

from util.ivfreader import IVFReader

currDir = os.path.dirname(os.path.realpath(__file__))
rootDir = os.path.abspath(os.path.join(currDir, '..'))

# reader_176_144 = IVFReader(rootDir+'/MCGserver/ivfvideos/res_176_144.ivf')
reader_352_288 = IVFReader(rootDir + '/MCGserver/ivfvideos/res_352_288.ivf')
# reader_480_270 = IVFReader(rootDir+'/MCGserver/ivfvideos/res_480_270.ivf')
# reader_504_376 = IVFReader(rootDir+'/MCGserver/ivfvideos/res_504_376.ivf')
reader_640_360 = IVFReader(rootDir + '/MCGserver/ivfvideos/res_640_360.ivf')
reader_854_480 = IVFReader(rootDir + '/MCGserver/ivfvideos/res_854_480.ivf')
# reader_960_540 = IVFReader(rootDir+'/MCGserver/ivfvideos/res_960_540.ivf')
reader_1280_720 = IVFReader(rootDir + '/MCGserver/ivfvideos/res_1280_720.ivf')
reader_1920_1080 = IVFReader(rootDir + '/MCGserver/ivfvideos/res_1920_1080.ivf')
# reader_176_144, reader_480_270, reader_504_376,reader_960_540
readers = [reader_352_288, reader_640_360, reader_854_480, reader_1280_720, reader_1920_1080]
# 163, 686.2, 1250.8, 2060.4
# bitrates = [534.9, 1334.3, 1884.8, 3897.6, 6809.7]
bitrates = [667.5, 1605.025, 2223.976, 4816.6, 8399.834]
# '176X144', '480X270', '504X376',  '960X540'
resolutions = ['352X288', '640X360', '854X480', '1280X720', '1920X1080']

with open(rootDir + '/RLa3c/video_chunks_3GoPs_10min.csv', 'w', newline='') as csvfile:
    csv_writer = csv.writer(csvfile, delimiter=',')
    csv_writer.writerow(['resolution', 'bitrate_level', 'chunk_size', 'chunk_no'])
    for idx in range(len(readers)):
        numframes = readers[idx].nFrames
        frame_no = 0
        GoP_size = 0
        GoP_no = 0
        while frame_no < numframes:
            frame = readers[idx].get_next_frame()
            GoP_size += frame.size
            frame_no += 1
            if frame_no % 10 == 0:
                csv_writer.writerow([resolutions[idx], idx, GoP_size, GoP_no])
                GoP_size = 0
                GoP_no += 1
                # print([frame.nr,frame.size,frame.ts])
