from nebula import VP8encode, RLNCencodeOff
from RTTProbing import RTTProbingServer
from multiprocessing import Manager
import signal, logging, os, sys

if __name__ == '__main__':
    #SIGPIPE Broken pipe: write to pipe with no readers.
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)

    CurrDir = os.path.dirname(os.path.realpath(__file__))
    Logs_Dir = os.path.join(CurrDir, '..', 'inout_data')
    # configure performance logger
    perf_log_url = os.path.join(Logs_Dir, "perf.sr.log")
    with open(perf_log_url, 'w'):
        pass

    perf_logger = logging.getLogger('Perf_Logger')
    hdlr_1 = logging.FileHandler(perf_log_url)
    perf_logger.setLevel(logging.INFO)
    perf_logger.addHandler(hdlr_1)
    perf_logger.info("process,frame_no,time")

    # configure overhead logger for throughput/goodput
    overhead_log_url = os.path.join(Logs_Dir, "overhead.sr.log")
    with open(overhead_log_url, 'w'):
        pass
    overhead_logger = logging.getLogger('overhead_logger')
    hdlr_2 = logging.FileHandler(overhead_log_url)
    overhead_logger.setLevel(logging.INFO)
    overhead_logger.addHandler(hdlr_2)
    overhead_logger.info("second,frame,seconds,n,k,PLR")


    # configure bandwidth logger for availablebw
    bw_log_url = os.path.join(Logs_Dir, "bw.sr.log")
    with open(bw_log_url, 'w'):
        pass
    bw_logger = logging.getLogger('BW_Logger')
    hdlr_4 = logging.FileHandler(bw_log_url)
    bw_logger.setLevel(logging.INFO)
    bw_logger.addHandler(hdlr_4)
    bw_logger.info("second,frame_no,seconds,channelrate,sourcerate,redundantPkts,redundancyrate,redundantPkts_error,redundancyrate_error")


    # configure overhead logger for feedback/rtt
    rtt_log_url = os.path.join(Logs_Dir, "rtt.sr.log")
    with open(rtt_log_url, 'w'):
        pass
    rtt_logger = logging.getLogger('rtt_Logger')
    hdlr_6 = logging.FileHandler(rtt_log_url)
    rtt_logger.setLevel(logging.INFO)
    rtt_logger.addHandler(hdlr_6)
    rtt_logger.info("seconds,ts,rtt")

    signal_raised = False
    def signal_handler(signal, frame):
        global signal_raised
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    #Start RLNC encode offline video
    manager = Manager()
    rtt_queue = manager.Queue(maxsize=1)
    user_event_queue = manager.Queue(maxsize=3)

    repServer = RTTProbingServer.RTTProbingServer(rtt_queue, rtt_logger)
    repServer.start()

    rlncenc = RLNCencodeOff.RLNCencodeOffProcess(rtt_queue, user_event_queue, logger=perf_logger, Overheadlogger=overhead_logger, BWlogger=bw_logger)
    print('*********************** FEC Nebula Mode ********************************')

    rlncenc.start()

    rlncenc.join()
    repServer.join()


