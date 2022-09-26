import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
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
        merged_tcp_eventsDF['motion2photon'] = merged_tcp_eventsDF.apply(
            lambda x: (x.recvts - x.sentts) * 1000 + vp8_encode_delay, axis=1)
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
        # WebRTC Server Rendering Delay
        render_rtcDF = pd.read_csv(dir_name+'/render.rtc.sr.log', sep=',')
        render_rtcDF.drop(['timebase', 'pts'], axis=1, inplace=True)

        merged_rtcDF = pd.merge(render_rtcDF, display_rtcDF, on='frame_no')
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


#Experiments directories
experiments_dir_names = ['wifidata5','wifidata6','wifidata7','wifidata8','wifidata11','wifidata12']
exper_mtp_dir_names_rtc = ['wifidata7','wifidata8','wifidata11','wifidata12']
exper_rtt_dir_names_rtc = ['wifidata11','wifidata12']

#Round Trip Time statsitics
nebulaRTTDF = computeRTT_nebula(experiments_dir_names)
tcpRTTDF = computeRTT_tcp(experiments_dir_names)
gopRTTDF = computeRTT_gop(experiments_dir_names)
boRTTDF = computeRTT_bo(experiments_dir_names)
rtcRTTDF = computeRTT_rtc(exper_rtt_dir_names_rtc)

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
merged_rtcDF = computeMTP_webRTC(exper_mtp_dir_names_rtc)

stats_nebulaDF = merged_eventsDF.describe()
stats_tcpDF = merged_tcpeventsDF.describe()
stats_gopDF = merged_gopeventsDF.describe()
stats_boDF = merged_boeventsDF.describe()
stats_rtcDF = merged_rtcDF.describe()


mtpMeans = (stats_nebulaDF['motion2photon']['mean'],stats_tcpDF['motion2photon']['mean'],stats_gopDF['motion2photon']['mean'],
           stats_boDF['motion2photon']['mean'],stats_rtcDF['motion2photon']['mean'])

mtpStds = (stats_nebulaDF['motion2photon']['std'],stats_tcpDF['motion2photon']['std'],stats_gopDF['motion2photon']['std'],
           stats_boDF['motion2photon']['std'],stats_rtcDF['motion2photon']['std'])

print(mtpStds)
# Plot figure
ind = ['Nebula', 'TcpCubic', 'ESCOT', 'BO', 'WebRTC']
width = 0.4  # the width of the bars: can also be len(x) sequence

# fig, (ax1, ax2) = plt.subplots(2, sharex=True)
fig = plt.figure(figsize=(16, 8))
ax = fig.add_subplot(111)
# color='skyblue': indianred, dodgerblue, turquoise, mediumseagreen, lightgreen
lowersmtp = np.minimum(mtpStds, mtpMeans)
lowersrtt = np.minimum(rttStds, rttMeans)
p1 = ax.bar(ind, mtpMeans, width, yerr=[lowersmtp, mtpStds], log=False, capsize=3,
             color='dodgerblue', error_kw=dict(elinewidth=2, ecolor='black'))
p2 = ax.bar(ind, rttMeans, width, yerr=[lowersrtt, rttStds], log=False, capsize=3,
             color='indianred',error_kw=dict(elinewidth=2, ecolor='brown'))

plt.margins(0.01, 0)

# Optional code - Make plot look nicer
i = 0.15
for row in mtpMeans:
    plt.text(i, row, "{0:.1f}".format(row), color='black', ha="center", fontsize=18)
    i = i + 1

# i=0.15
# totop = 60
# for rlnc,vpx in zip (rlncMeans,vpxMeans):
#     plt.text(i,rlnc + vpx, "{0:.1f}".format(rlnc+vpx), color='black', ha="center", fontsize=22)
#     i = i + 1

ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
plt.tick_params(axis="y", labelsize=20, labelcolor="black")
plt.tick_params(axis="x", labelsize=20, labelcolor="black")
plt.ylabel('Round Trip Time (ms)', fontsize=20)
plt.title('Eduroam WiFi', fontsize=20)
plt.ylabel('RTT/Motion to Photon (ms)', fontsize=20)

# plt.savefig('mtp_rtt_wifi.png', bbox_inches='tight')
# fig.savefig('mtp_rtt_wifi.eps', format='eps',bbox_inches='tight')
plt.show()