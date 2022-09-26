import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import os
# import seaborn as sns
vp8_encode_delay =  20.8

#Motion to Photon
def computeMTP_nebula(dir_names):

    column_names = ['sentype', 'event', 'eventno', 'sentts','recvtype','recvts','motion2photon']
    mtpDF =  pd.DataFrame(columns = column_names)
    for dir_name in dir_names:
        #Nebula Motion to Photon Calculation
        eventsDF = pd.read_csv(dir_name+'/event.cl.log', sep=',')
        sent_eventsDF = eventsDF.loc[eventsDF.type=='sent']
        recv_eventsDF = eventsDF.loc[eventsDF.type=='recv']
        recv_eventsDF = recv_eventsDF.drop(['event'], axis=1)

        merged_eventsDF = pd.merge(sent_eventsDF, recv_eventsDF, on='eventno')
        merged_eventsDF.columns = ['sentype', 'event', 'eventno', 'sentts','recvtype','recvts']
        merged_eventsDF['motion2photon'] = merged_eventsDF.apply(lambda x: (x.recvts-x.sentts)*1000 + vp8_encode_delay , axis=1)
        mtpDF = pd.concat([mtpDF,merged_eventsDF], ignore_index=True)

    return mtpDF

def computeMTP_tcp(dir_names):
    # TCP (CUBIC) Motion to Photon Calculation
    column_names = ['sentype', 'event', 'eventno', 'sentts', 'recvtype', 'recvts', 'motion2photon']
    mtpDF = pd.DataFrame(columns=column_names)
    for dir_name in dir_names:
        # Nebula Motion to Photon Calculation
        eventsDF = pd.read_csv(dir_name + '/event.tcp.cl.log', sep=',')
        sent_eventsDF = eventsDF.loc[eventsDF.type == 'sent']
        recv_eventsDF = eventsDF.loc[eventsDF.type == 'recv']
        recv_eventsDF = recv_eventsDF.drop(['event'], axis=1)

        merged_tcp_eventsDF = pd.merge(sent_eventsDF, recv_eventsDF, on='eventno')
        merged_tcp_eventsDF.columns = ['sentype', 'event', 'eventno', 'sentts', 'recvtype', 'recvts']
        merged_tcp_eventsDF = merged_tcp_eventsDF.assign(motion2photon= lambda x: (x.recvts - x.sentts) * 1000 + vp8_encode_delay, axis=1)
        mtpDF = pd.concat([mtpDF, merged_tcp_eventsDF], ignore_index=True)

    return mtpDF

def computeMTP_gop(dir_names):
    #GoP-based (ESCOT) Motion to Photon Calculation
    column_names = ['sentype', 'event', 'eventno', 'sentts', 'recvtype', 'recvts', 'motion2photon']
    mtpDF = pd.DataFrame(columns=column_names)
    for dir_name in dir_names:
        # Nebula Motion to Photon Calculation
        eventsDF = pd.read_csv(dir_name + '/event.gop.cl.log', sep=',')
        sent_eventsDF = eventsDF.loc[eventsDF.type == 'sent']
        recv_eventsDF = eventsDF.loc[eventsDF.type == 'recv']
        recv_eventsDF = recv_eventsDF.drop(['event'], axis=1)

        merged_gop_eventsDF = pd.merge(sent_eventsDF, recv_eventsDF, on='eventno')
        merged_gop_eventsDF.columns = ['sentype', 'event', 'eventno', 'sentts', 'recvtype', 'recvts']
        merged_gop_eventsDF['motion2photon'] = merged_gop_eventsDF.apply(
            lambda x: (x.recvts - x.sentts) * 1000 + vp8_encode_delay, axis=1)
        mtpDF = pd.concat([mtpDF, merged_gop_eventsDF], ignore_index=True)

    return mtpDF

def computeMTP_bo(dir_names):
    #Buffer Occupancy Motion to Photon Calculation
    column_names = ['sentype', 'event', 'eventno', 'sentts', 'recvtype', 'recvts', 'motion2photon']
    mtpDF = pd.DataFrame(columns=column_names)
    for dir_name in dir_names:
        # Nebula Motion to Photon Calculation
        eventsDF = pd.read_csv(dir_name + '/event.bo.cl.log', sep=',')
        sent_eventsDF = eventsDF.loc[eventsDF.type == 'sent']
        recv_eventsDF = eventsDF.loc[eventsDF.type == 'recv']
        recv_eventsDF = recv_eventsDF.drop(['event'], axis=1)

        merged_bo_eventsDF = pd.merge(sent_eventsDF, recv_eventsDF, on='eventno')
        merged_bo_eventsDF.columns = ['sentype', 'event', 'eventno', 'sentts', 'recvtype', 'recvts']
        merged_bo_eventsDF['motion2photon'] = merged_bo_eventsDF.apply(
            lambda x: (x.recvts - x.sentts) * 1000 + vp8_encode_delay, axis=1)
        mtpDF = pd.concat([mtpDF, merged_bo_eventsDF], ignore_index=True)

    return mtpDF

def computeMTP_webRTC(dir_names):
    # WebRTC Client Display Delay
    column_names = ['frame_no', 'rendrdelay', 'rendrts', 'dispdelay', 'dispts','motion2photon']
    mtpDF = pd.DataFrame(columns=column_names)
    for dir_name in dir_names:
        display_rtcDF = pd.read_csv(dir_name+'/display.rtc.log', sep=',')
        display_rtcDF.drop(['timebase', 'pts'], axis=1, inplace=True)
        print(display_rtcDF)
        # WebRTC Server Rendering Delay
        render_rtcDF = pd.read_csv(dir_name+'/render.rtc.sr.log', sep=',')
        render_rtcDF.drop(['timebase', 'pts'], axis=1, inplace=True)
        print(render_rtcDF)
        merged_rtcDF = pd.merge(render_rtcDF, display_rtcDF, on='frame_no')
        print(merged_rtcDF)
        merged_rtcDF.columns = ['frame_no', 'rendrdelay', 'rendrts', 'dispdelay', 'dispts']
        merged_rtcDF['motion2photon'] = merged_rtcDF.apply(lambda x: x.dispts - x.rendrts, axis=1)
        mtpDF = pd.concat([mtpDF, merged_rtcDF], ignore_index=True)

    return mtpDF


#Round Trip Time
def computeRTT_nebula(dir_names):
    #Nebula RTT
    column_names = ['seconds','ts','rtt']
    rttDF = pd.DataFrame(columns=column_names)
    for dir_name in dir_names:
        # Nebula Motion to Photon Calculation
        nebulaRTTDF = pd.read_csv(dir_name + '/rtt.sr.log', sep=',')
        rttDF = pd.concat([rttDF, nebulaRTTDF], ignore_index=True)

    return rttDF

def computeRTT_gop(dir_names):
    # Nebula RTT
    column_names = ['seconds', 'ts', 'rtt']
    rttDF = pd.DataFrame(columns=column_names)
    for dir_name in dir_names:
        # Nebula Motion to Photon Calculation
        gopRTTDF = pd.read_csv(dir_name + '/rtt.gop.sr.log', sep=',')
        rttDF = pd.concat([rttDF, gopRTTDF], ignore_index=True)

    return rttDF

def computeRTT_bo(dir_names):
    # BO RTT
    column_names = ['seconds', 'ts', 'rtt']
    rttDF = pd.DataFrame(columns=column_names)
    for dir_name in dir_names:
        # Nebula Motion to Photon Calculation
        boRTTDF = pd.read_csv(dir_name + '/rtt.bo.sr.log', sep=',')
        rttDF = pd.concat([rttDF, boRTTDF], ignore_index=True)

    return rttDF

def computeRTT_tcp(dir_names):
    # TCP CUBIC RTT
    column_names = ['seconds', 'ts', 'rtt']
    rttDF = pd.DataFrame(columns=column_names)
    for dir_name in dir_names:
        # Nebula Motion to Photon Calculation
        tcpRTTDF = pd.read_csv(dir_name + '/rtt.tcp.sr.log', sep=',')
        rttDF = pd.concat([rttDF, tcpRTTDF], ignore_index=True)

    return rttDF

def computeRTT_rtc(dir_names):
    # WebRTC RTT
    column_names = ['seconds','delay','client_ping_ts','server_pong_ts','client_pang_ts']
    rttDF = pd.DataFrame(columns=column_names)
    for dir_name in dir_names:
        # Nebula Motion to Photon Calculation
        rtcRTTDF = pd.read_csv(dir_name + '/rtt.rtc.sr.log', sep=',')
        rtcRTTDF = rtcRTTDF.loc[rtcRTTDF.delay < 1000]  # remove delays beyond RTT timer
        rttDF = pd.concat([rttDF, rtcRTTDF], ignore_index=True)

    return rttDF


currDir = os.path.dirname(os.path.realpath(__file__))

#Nebula PSNR aggregation
def aggregatePSNR_nebula(dir_names):
    column_names = ['frameno', 'psnr']
    psnrDF =  pd.DataFrame(columns = column_names)
    for dir_name in dir_names:
        Nebula_CSV_PATH = os.path.join(currDir, dir_name, 'psnr.nebula.csv')
        # Read PSNR CSV
        nebulaDF = pd.read_csv(Nebula_CSV_PATH, sep=',')
        nebulaDF.columns = ['frameno', 'psnr']
        psnrDF = pd.concat([psnrDF, nebulaDF], ignore_index=True)
    return psnrDF

#GoP  PSNR aggregation
def aggregatePSNR_gop(dir_names):
    column_names = ['frameno', 'psnr']
    psnrDF =  pd.DataFrame(columns = column_names)
    for dir_name in dir_names:
        ESCOT_CSV_PATH = os.path.join(currDir, dir_name, 'psnr.gop.csv')
        # Read PSNR CSV
        escotDF = pd.read_csv(ESCOT_CSV_PATH, sep=',')
        escotDF.columns = ['frameno', 'psnr']
        psnrDF = pd.concat([psnrDF, escotDF], ignore_index=True)
    return psnrDF

#TCP  PSNR aggregation
def aggregatePSNR_tcp(dir_names):
    column_names = ['frameno', 'psnr']
    psnrDF =  pd.DataFrame(columns = column_names)
    for dir_name in dir_names:
        TCP_CSV_PATH = os.path.join(currDir, dir_name, 'psnr.tcp.csv')
        # Read PSNR CSV
        tcpDF = pd.read_csv(TCP_CSV_PATH, sep=',')
        tcpDF.columns = ['frameno', 'psnr']
        psnrDF = pd.concat([psnrDF, tcpDF], ignore_index=True)
    return psnrDF

#BO PSNR aggregation
def aggregatePSNR_bo(dir_names):
    column_names = ['frameno', 'psnr']
    psnrDF =  pd.DataFrame(columns = column_names)
    for dir_name in dir_names:
        BO_CSV_PATH = os.path.join(currDir, dir_name, 'psnr.bo.csv')
        # Read PSNR CSV
        boDF = pd.read_csv(BO_CSV_PATH, sep=',')
        boDF.columns = ['frameno', 'psnr']
        psnrDF = pd.concat([psnrDF, boDF], ignore_index=True)
    return psnrDF


#WebRTC PSNR aggregation
def aggregatePSNR_webrtc(dir_names):
    column_names = ['frameno', 'psnr']
    psnrDF =  pd.DataFrame(columns = column_names)
    for dir_name in dir_names:
        WebRTC_CSV_PATH = os.path.join(currDir, dir_name, 'psnr.webrtc.csv')
        # Read PSNR CSV
        rtcDF = pd.read_csv(WebRTC_CSV_PATH, sep=',')
        rtcDF.columns = ['frameno', 'psnr']
        psnrDF = pd.concat([psnrDF, rtcDF], ignore_index=True)
    return psnrDF


#Experiments directories
experiments_dir_names = ['ethdata8'] #'ethdata6/7/8' are more authentic,

#Round Trip Time statsitics
nebulaRTTDF = computeRTT_nebula(experiments_dir_names)
tcpRTTDF = computeRTT_tcp(experiments_dir_names)
gopRTTDF = computeRTT_gop(experiments_dir_names)
boRTTDF = computeRTT_bo(experiments_dir_names)
rtcRTTDF = computeRTT_rtc(experiments_dir_names)

stats_rtt_nebula = nebulaRTTDF.describe()
stats_rtt_tcp = tcpRTTDF.describe()
stats_rtt_gop = gopRTTDF.describe()
stats_rtt_bo = boRTTDF.describe()
stats_rtt_rtc = rtcRTTDF.describe()

rttMeans = (stats_rtt_nebula['rtt']['mean'],stats_rtt_tcp['rtt']['mean'],stats_rtt_gop['rtt']['mean'],
           stats_rtt_bo['rtt']['mean'],stats_rtt_rtc['delay']['mean'])

rttStds = (stats_rtt_nebula['rtt']['std'],stats_rtt_tcp['rtt']['std'],stats_rtt_gop['rtt']['std'],
           stats_rtt_bo['rtt']['std'],stats_rtt_rtc['delay']['std'])


#Motion to Photon statsitics
merged_eventsDF = computeMTP_nebula(experiments_dir_names)
merged_tcpeventsDF = computeMTP_tcp(experiments_dir_names)
merged_gopeventsDF = computeMTP_gop(experiments_dir_names)
merged_boeventsDF = computeMTP_bo(experiments_dir_names)
merged_rtcDF = computeMTP_webRTC(experiments_dir_names)

#Apply special filter to WebRTC
merged_rtcDF = merged_rtcDF.loc[merged_rtcDF.motion2photon < 1500]  # remove MTP beyond RTT timer

stats_nebulaDF = merged_eventsDF.describe()
stats_tcpDF = merged_tcpeventsDF.describe()
stats_gopDF = merged_gopeventsDF.describe()
stats_boDF = merged_boeventsDF.describe()
stats_rtcDF = merged_rtcDF.describe()


mtpMeans = (stats_nebulaDF['motion2photon']['mean'],stats_tcpDF['motion2photon']['mean'],stats_gopDF['motion2photon']['mean'],
           stats_boDF['motion2photon']['mean'],stats_rtcDF['motion2photon']['mean'])

mtpStds = (stats_nebulaDF['motion2photon']['std'],stats_tcpDF['motion2photon']['std'],stats_gopDF['motion2photon']['std'],
           stats_boDF['motion2photon']['std'],stats_rtcDF['motion2photon']['std'])



#Visual Quality (PSNR) statsitics
nebulapsnrDF = aggregatePSNR_nebula(experiments_dir_names)
escotpsnrDF = aggregatePSNR_gop(experiments_dir_names)
tcppsnrDF = aggregatePSNR_tcp(experiments_dir_names)
bopsnrDF = aggregatePSNR_bo(experiments_dir_names)
webrtcpsnrDF = aggregatePSNR_webrtc(experiments_dir_names)
webrtcpsnrDF = webrtcpsnrDF.loc[webrtcpsnrDF.frameno<1000] #Frames after 1000 are not synced
######
stats_nebulapsnrDF = nebulapsnrDF.describe()
stats_tcppsnrDF = tcppsnrDF.describe()
stats_goppsnrDF = escotpsnrDF.describe()
stats_bopsnrDF = bopsnrDF.describe()
stats_rtcpsnrDF = webrtcpsnrDF.describe()

#Compute Mean
psnrMeans = (stats_nebulapsnrDF['psnr']['mean'],stats_tcppsnrDF['psnr']['mean'],stats_goppsnrDF['psnr']['mean'],
           stats_bopsnrDF['psnr']['mean'],stats_rtcpsnrDF['psnr']['mean'])

#Compute STD
psnrStds = (stats_nebulapsnrDF['psnr']['std'],stats_tcppsnrDF['psnr']['std'],stats_goppsnrDF['psnr']['std'],
           stats_bopsnrDF['psnr']['std'],stats_rtcpsnrDF['psnr']['std'])

# Plot figure
ind = ['Nebula', 'TCP/Cubic', 'ESCOT', 'BO', 'WebRTC']
width = 0.4  # the width of the bars: can also be len(x) sequence

# fig, (ax1, ax2) = plt.subplots(2, sharex=True)
fig, axes = plt.subplots(2)
plt.margins(0.01, 0)
# color='skyblue': indianred, dodgerblue, turquoise, mediumseagreen, lightgreen
lowersmtp = np.minimum(mtpStds, mtpMeans)
lowersrtt = np.minimum(rttStds, rttMeans)
p1 = axes[0].bar(ind, mtpMeans, width, yerr=[lowersmtp, mtpStds], log=False, capsize=16,
             color='lightgreen', error_kw=dict(elinewidth=2, ecolor='mediumseagreen'), label='Motion-to-Photon Latency')
p2 = axes[0].bar(ind, rttMeans, width, yerr=[lowersrtt, rttStds], log=False, capsize=16,
             color='indianred',error_kw=dict(elinewidth=2, ecolor='brown'), label='Network RTT')

plt.margins(0.01, 0)

# Optional code - Make plot look nicer
i = 0.1
for row in mtpMeans:
    axes[0].text(i, row, "{0:.1f}".format(row), color='gray', ha="center", fontsize=16)
    i = i + 1
axes[0].spines['right'].set_visible(False)
axes[0].spines['top'].set_visible(False)
axes[0].set_title('Emulated Network Constrains', fontsize=18)
axes[0].set_ylabel('RTT | MTP (ms)', fontsize=15)
axes[0].set_xticklabels('', fontsize=16)
leg = axes[0].legend(prop={'size': 10})
plt.setp(axes[0].get_yticklabels(), fontsize=14)
# axes[0].set_yscale('log')

###### PSNR
lowers = np.minimum(psnrStds, psnrMeans)
p3 = axes[1].bar(ind, psnrMeans, width, yerr=[lowers, psnrStds], log=False, capsize=16,
             error_kw=dict(elinewidth=3, ecolor='black'))
# Optional code - Make plot look nicer
plt.margins(0.01, 0)
i = 0.12
for row in psnrMeans:
    axes[1].text(i, row, "{0:.1f}".format(row), color='gray', ha="center", fontsize=16)
    i = i + 1
axes[1].spines['right'].set_visible(False)
axes[1].spines['top'].set_visible(False)
axes[1].set_ylabel('PSNR (dB)', fontsize=15)
# plt.xticks(fontsize= 18)
# plt.yticks(fontsize= 18)
plt.setp(axes[1].get_xticklabels(), fontsize=16)
plt.setp(axes[1].get_yticklabels(), fontsize=14)

# plt.savefig('mtp_rtt_wifi.png', bbox_inches='tight')
# fig.savefig('mtp_psnr_eth.eps', format='eps',bbox_inches='tight')
# plt.savefig('mtp_psnr_eth.pdf', bbox_inches='tight')
plt.show()