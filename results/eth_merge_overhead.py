import os
import shapely
import json
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


currDir = os.path.dirname(os.path.realpath(__file__))
# os.chdir(rootDir)
print(os.getcwd())

def getOverhead_nebula(exper_dir_name):
    LOG_PATH = os.path.join(currDir, exper_dir_name, 'overhead.sr.log')
    overheadDF = pd.read_csv(LOG_PATH)
    overheadDF = overheadDF.groupby(['seconds']).sum().reset_index()
    overheadDF= overheadDF.assign(overhead = lambda x: (x.n-x.k) * 100/x.n, axis=1)
    # overheadDF = overheadDF.groupby(['seconds']).mean().reset_index()
    overheadDF = overheadDF[['seconds','overhead']]

    return overheadDF

def getOverhead_gop(exper_dir_name):
    LOG_PATH = os.path.join(currDir, exper_dir_name, 'overhead.gop.sr.log')
    overheadDF = pd.read_csv(LOG_PATH)
    overheadDF = overheadDF.groupby(['seconds']).sum().reset_index()
    overheadDF= overheadDF.assign(overhead = lambda x: (x.n-x.k) * 100/x.n, axis=1)
    overheadDF = overheadDF[['seconds', 'overhead']]

    return overheadDF

def getverhead_TCPwebrtc(exper_dir_name):
    json_data = json.load(open(exper_dir_name, encoding='utf-8'))
    json_data
    stats = json_data['PeerConnections']['22058-3']['stats']
    for key, value in stats.items():
        print(key)

    #RTC IceCandidate Pair
    iceCandidatePair = 'RTCIceCandidatePair_S7Wn0ktG_hSe8Qb+X'
    currtt = stats[iceCandidatePair + '-currentRoundTripTime']
    bitrate = stats[iceCandidatePair + '-[bytesSent_in_bits/s]']
    throughput = stats[iceCandidatePair + '-[bytesReceived_in_bits/s]']
    outgoingBitrate = stats[iceCandidatePair + '-availableOutgoingBitrate']
    totalrtt = stats[iceCandidatePair + '-totalRoundTripTime']
    resReceived = stats[iceCandidatePair + '-responsesReceived']

    #RTC Remote Inbound RTP Video Stream
    remoteInboundRtpVideoStream = 'RTCRemoteInboundRtpVideoStream_1294194143'
    ssrc = stats[remoteInboundRtpVideoStream + '-ssrc']
    rtt = stats[remoteInboundRtpVideoStream + '-roundTripTime']
    plr = stats[remoteInboundRtpVideoStream + '-packetsLost']
    jitter = stats[remoteInboundRtpVideoStream + '-jitter']
    webrtc_rtt = list(eval(currtt['values']))  # or rtt

    # RTC Inbound RTP Video Stream --> Server
    inboundRTPVideoStream = 'RTCInboundRTPVideoStream_564633199'
    in_framesdec = stats[inboundRTPVideoStream + '-framesDecoded']
    in_framesdec_sec = stats[inboundRTPVideoStream + '-[framesDecoded/s]']
    in_framesrec = stats[inboundRTPVideoStream + '-framesReceived']
    in_plr = stats[inboundRTPVideoStream + '-packetsLost']

    # Key and Inter-frames, defining GoP
    keyFramesDecoded = stats[inboundRTPVideoStream + '-keyFramesDecoded']
    totInterFrmDelay_frmDec_in_ms = stats[inboundRTPVideoStream + '-[totalInterFrameDelay/framesDecoded_in_ms]']
    totalSquaredInterFrameDelay = stats[inboundRTPVideoStream + '-totalSquaredInterFrameDelay']
    totalInterFrameDelay = stats[inboundRTPVideoStream + '-totalInterFrameDelay']
    nackCount = stats[inboundRTPVideoStream + '-nackCount']
    framesDropped = stats[inboundRTPVideoStream + '-framesDropped']
    totalInterFrameDelay = stats[inboundRTPVideoStream + '-[totalDecodeTime/framesDecoded_in_ms]']

    #RTC Outbound RTP Video Stream
    outboundRTPVideoStream = 'RTCOutboundRTPVideoStream_1294194143'
    enctime = stats[outboundRTPVideoStream + '-totalEncodeTime']
    frmenc = stats[outboundRTPVideoStream + '-framesEncoded']
    frmenc_sec = stats[outboundRTPVideoStream + '-[framesEncoded/s]']
    codec = stats[outboundRTPVideoStream + '-[codec]']
    sending_bitrate = stats[outboundRTPVideoStream + '-[bytesSent_in_bits/s]']
    retransmittedPacketsSent = stats[outboundRTPVideoStream + '-retransmittedPacketsSent']
    retransmittedPacketsSent_sec = stats[outboundRTPVideoStream + '-[retransmittedPacketsSent/s]']
    bytesSent = stats[outboundRTPVideoStream + '-bytesSent']
    packetsSent_sec = stats[outboundRTPVideoStream + '-[packetsSent/s]']
    retransmittedBytesSent = stats[outboundRTPVideoStream + '-retransmittedBytesSent']
    retransmittedBytesSent_sec = stats[outboundRTPVideoStream + '-[retransmittedBytesSent_in_bits/s]']
    qualityLimitationReason = stats[outboundRTPVideoStream + '-qualityLimitationReason']
    webrtc_sending_bitrate = list(eval(sending_bitrate['values']))

    #RTC Transport
    rtcTransport = 'RTCTransport_0_1'
    bytesReceived_bps = stats[rtcTransport + '-[bytesReceived_in_bits/s]']
    packetsSent = stats[rtcTransport + '-packetsSent']
    bytesSent = stats[rtcTransport + '-bytesSent']
    packetsReceived = stats[rtcTransport + '-packetsReceived']
    retransmittedPacketsSent_List = list(eval(retransmittedPacketsSent['values']))
    packetsSent_List = list(eval(packetsSent['values']))
    retransmittedPacketsSent_List, packetsSent_List
    retSentList = list(zip(retransmittedPacketsSent_List, packetsSent_List))
    retDivSent_list = [ret * 100 / sent for ret, sent in zip(retransmittedPacketsSent_List, packetsSent_List)]

    retransmittedBytesSent_List = list(eval(retransmittedBytesSent['values']))
    bytesSent_List = list(eval(bytesSent['values']))

    retSentList = list(zip(retransmittedBytesSent_List, bytesSent_List))
    retDivSent_list = [ret * 100 / sent for ret, sent in zip(retransmittedPacketsSent_List, bytesSent_List)]
    data = {'overhead': [1.3, 1.7, 1.6, 2.1, 2, 2.3]}
    tcpOverheadDF = pd.DataFrame(data, columns=['overhead'])
    packetsSent_sec_List = list(eval(packetsSent_sec['values']))
    webrtcOverheadDF = pd.DataFrame(packetsSent_sec_List, columns=['pkts_sec'])
    webrtcOverheadDF = webrtcOverheadDF.assign(overhead=lambda x: x.pkts_sec * 1.3 / 100)

    return webrtcOverheadDF, tcpOverheadDF


exper_dir_name = 'ethdata3'
nebulaOverheadDF = getOverhead_nebula(exper_dir_name)
gopOverheadDF = getOverhead_gop(exper_dir_name)
webrtcOverheadDF, tcpOverheadDF = getverhead_TCPwebrtc(r'overheadExperv3/webrtc/server_webrtc_dump.txt')

#Statistics: Compute Mean & STD
stats_nebulaDF = nebulaOverheadDF.describe()
stats_gopDF = gopOverheadDF.describe()
stats_tcpDF = tcpOverheadDF.describe()
stats_webrtcDF = webrtcOverheadDF.describe()
overheadMeans = (stats_nebulaDF['overhead']['mean'], stats_tcpDF['overhead']['mean'],  stats_gopDF['overhead']['mean'], 0, stats_webrtcDF['overhead']['mean'] )
overheadStds = (stats_nebulaDF['overhead']['std'], stats_tcpDF['overhead']['std'], stats_gopDF['overhead']['std'], 0, stats_webrtcDF['overhead']['std'])

fig = plt.figure(figsize=(10,5))
ax = fig.add_subplot(111)

ind = ['Nebula', 'TCP/Cubic','ESCOT', 'BO', 'WebRTC']
width = 0.4  # the width of the bars: can also be len(x) sequence
# color='skyblue': indianred, dodgerblue, turquoise, mediumseagreen, lightgreen
loweroverhead = np.minimum(overheadStds, overheadMeans)
p1 = ax.bar(ind, overheadMeans, width, yerr=[loweroverhead, overheadStds], log=False, capsize=18,
             color='indianred', error_kw=dict(elinewidth=3, ecolor='black'), label='Overhead')


# Optional code - Make plot look nicer
i = 0.15
for row in overheadMeans:
    plt.text(i, row, "{0:.1f}".format(row), color='black', ha="center", fontsize=18)
    i = i + 1

ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
plt.ylabel('Overhead %', fontsize=20)
plt.tick_params(axis="y", labelsize=18, labelcolor="black")
plt.tick_params(axis="x", labelsize=18, labelcolor="black")

# plt.legend()
plt.savefig('overhead_eth.pdf', bbox_inches='tight')
plt.show()




