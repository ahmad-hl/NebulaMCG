import csv
import os
import PreTxUtility

reader_1920_1080  = PreTxUtility.get_maxres_reader()
CurrDir = os.path.dirname(os.path.realpath(__file__))
Logs_Dir = os.path.join(CurrDir, '..', 'inout_data')
outcsv_path = os.path.join(Logs_Dir, "Frame_size_1min.csv")

with open(outcsv_path, 'w', newline='') as csvfile:
    csv_writer = csv.writer(csvfile, delimiter=',')
    csv_writer.writerow(['frame_no','frame_size'])
    numframes = reader_1920_1080.nFrames
    frame_no = 0
    while frame_no < numframes:
        frame = reader_1920_1080.get_next_frame()
        frame_no += 1
        csv_writer.writerow([ frame.nr,frame.size])
        print([frame.nr, frame.size])
