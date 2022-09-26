from multiprocessing import Manager
from nebula import RLNCdecode, VP8decode, Display, PSNRcompute
from RTTProbing import RTTProbingClient
import logging, sys, signal, os
from udponly import UDPreceiver
from tcp import TCPreceiver
from util import user_interaction

if __name__ == '__main__':
    currDir = os.path.dirname(os.path.realpath(__file__))
    Logs_Dir = os.path.join(currDir, '..', 'inout_data')
    #configure performance logger
    log_url = os.path.join(Logs_Dir, "perf.cl.log")
    with open(log_url, 'w'):
        pass

    perf_logger = logging.getLogger('Perf_Logger')
    hdlr_1 = logging.FileHandler(log_url)
    perf_logger.setLevel(logging.INFO)
    perf_logger.addHandler(hdlr_1)
    perf_logger.info("process,frame_no,time")

    # configure latenc  y logger
    delay_log_url = os.path.join(Logs_Dir, "delay.cl.log")
    with open(delay_log_url, 'w'):
        pass
    latency_logger = logging.getLogger('Latency_Logger')
    hdlr_2 = logging.FileHandler(delay_log_url)
    latency_logger.setLevel(logging.INFO)
    latency_logger.addHandler(hdlr_2)
    latency_logger.info("second_no,frame_no,packetdelay,framedelay")

    # configure interface bandwidth
    bw_log_url = os.path.join(Logs_Dir, "bw.cl.log")
    with open(bw_log_url, 'w'):
        pass
    bw_logger = logging.getLogger('BW_Logger')
    hdlr_3 = logging.FileHandler(bw_log_url)
    bw_logger.setLevel(logging.INFO)
    bw_logger.addHandler(hdlr_3)
    bw_logger.info("seconds,bw")

    # configure interface bandwidth
    ifbw_log_url = os.path.join(Logs_Dir, "ifbw.cl.log")
    with open(ifbw_log_url, 'w'):
        pass
    ifbw_logger = logging.getLogger('IFBW_Logger')
    hdlr_4 = logging.FileHandler(ifbw_log_url)
    ifbw_logger.setLevel(logging.INFO)
    ifbw_logger.addHandler(hdlr_4)
    ifbw_logger.info("seconds,bw")

    # configure FPS logger
    fps_log_url = os.path.join(Logs_Dir, "display.fps.log")
    with open(fps_log_url, 'w'):
        pass
    fps_logger = logging.getLogger('FPS_Logger')
    hdlr_5 = logging.FileHandler(fps_log_url)
    fps_logger.setLevel(logging.INFO)
    fps_logger.addHandler(hdlr_5)
    fps_logger.info("second_no,frame_no,time")

    # configure user event logger
    event_log_url = os.path.join(Logs_Dir, "event.cl.log")
    with open(event_log_url, 'w'):
        pass
    event_logger = logging.getLogger('Event_Logger')
    hdlr_6 = logging.FileHandler(event_log_url)
    event_logger.setLevel(logging.INFO)
    event_logger.addHandler(hdlr_6)
    event_logger.info("type,event,eventno,ts")

    # configure FPS logger
    plr_log_url = os.path.join(Logs_Dir, "plr.cl.log")
    with open(plr_log_url, 'w'):
        pass
    plr_logger = logging.getLogger('PLR_Logger')
    hdlr_7 = logging.FileHandler(plr_log_url)
    plr_logger.setLevel(logging.INFO)
    plr_logger.addHandler(hdlr_7)
    plr_logger.info("frame,lostpkts")

    signal_raised = False
    def signal_handler(signal, frame):
        global signal_raised
        print ('You pressed Ctrl+C - or killed me with -2')
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    # initiate & start processes
    manager = Manager()
    rec_queue = manager.Queue(maxsize=10)
    psnr_queue = manager.Queue(maxsize=100)

    rlncdec = RLNCdecode.RLNCdecodeProcess(rec_queue, logger=perf_logger, latencylogger=latency_logger, bwlogger=bw_logger, ifbw_logger=ifbw_logger, plrlogger=plr_logger)
    print('*********************** Client & FEC Mode ********************************')
    rlncdec.start()

    reportingClient = RTTProbingClient.RTTProbingClient()
    reportingClient.start()

    vp8dec = VP8decode.VP8decodeProcess(rec_queue, psnr_queue, logger=perf_logger, event_logger=event_logger)
    vp8dec.start()

    display = Display.DisplayProcess(psnr_queue)
    display.start()

    # Support user to keyboad interaction
    user_key_it = user_interaction.UserKeyInteraction(event_logger=event_logger)
    user_key_it.user_key_interaction()

    #join processes
    rlncdec.join()
    reportingClient.join()
    vp8dec.join()
    # display.join()
