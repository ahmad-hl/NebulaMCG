import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
# import seaborn as sns
vp8_encode_delay =  20.8

#Nebula Motion to Photon Calculation
eventsDF = pd.read_csv(r'../inout_data/event.cl.log', sep=',')
sent_eventsDF = eventsDF.loc[eventsDF.type=='sent']
recv_eventsDF = eventsDF.loc[eventsDF.type=='recv']
recv_eventsDF = recv_eventsDF.drop(['event'], axis=1)

merged_eventsDF = pd.merge(sent_eventsDF, recv_eventsDF, on='eventno')
merged_eventsDF.columns = ['sentype', 'event', 'eventno', 'sentts','recvtype','recvts']
print(merged_eventsDF)
merged_eventsDF['motion2photon'] = merged_eventsDF.apply(lambda x: (x.recvts-x.sentts)*1000 + vp8_encode_delay , axis=1)
merged_eventsDF = merged_eventsDF.loc[merged_eventsDF.motion2photon<2000] #remove delays beyond RTT timer (1sec)

#TCP (CUBIC) Motion to Photon Calculation
tcpeventsDF = pd.read_csv(r'../inout_data/event.tcp.cl.log', sep=',')
sent_tcpeventsDF = tcpeventsDF.loc[tcpeventsDF.type=='sent']
recv_tcpeventsDF = tcpeventsDF.loc[tcpeventsDF.type=='recv']
recv_tcpeventsDF = recv_tcpeventsDF.drop(['event'], axis=1)

merged_tcpeventsDF = pd.merge(sent_tcpeventsDF, recv_tcpeventsDF, on='eventno')
merged_tcpeventsDF.columns = ['sentype', 'event', 'eventno', 'sentts','recvtype','recvts']
merged_tcpeventsDF['motion2photon'] = merged_tcpeventsDF.apply(lambda x: (x.recvts-x.sentts)*1000 +vp8_encode_delay , axis=1)
# merged_tcpeventsDF = merged_tcpeventsDF.loc[merged_tcpeventsDF.motion2photon<2000] #remove delays beyond RTT timer (1sec)

#GoP-based (ESCOT) Motion to Photon Calculation
gopeventsDF = pd.read_csv(r'../inout_data/event.gop.cl.log', sep=',')
sent_gopeventsDF = gopeventsDF.loc[gopeventsDF.type=='sent']
recv_gopeventsDF = gopeventsDF.loc[gopeventsDF.type=='recv']
recv_gopeventsDF = recv_gopeventsDF.drop(['event'], axis=1)

merged_gopeventsDF = pd.merge(sent_gopeventsDF, recv_gopeventsDF, on='eventno')
merged_gopeventsDF.columns = ['sentype', 'event', 'eventno', 'sentts','recvtype','recvts']

merged_gopeventsDF['motion2photon'] = merged_gopeventsDF.apply(lambda x: (x.recvts-x.sentts)*1000 + vp8_encode_delay , axis=1)
merged_gopeventsDF = merged_gopeventsDF.loc[merged_gopeventsDF.motion2photon<2000] #remove delays beyond RTT timer (1sec)


#Buffer Occupancy Motion to Photon Calculation
boeventsDF = pd.read_csv(r'../inout_data/event.bo.cl.log', sep=',')
sent_boeventsDF = boeventsDF.loc[boeventsDF.type=='sent']
recv_boeventsDF = boeventsDF.loc[boeventsDF.type=='recv']
recv_boeventsDF = recv_boeventsDF.drop(['event'], axis=1)

bovp8dispDF = pd.read_csv(r'../inout_data/perf.bo.cl.log', sep=',')
bovp8dispDF = bovp8dispDF.loc[bovp8dispDF.process=='vp8dec']
vp8disp_mean = bovp8dispDF['time'].mean()
vp8disp_mean = 20.8
avg_qframe = 10

merged_boeventsDF = pd.merge(sent_boeventsDF, recv_boeventsDF, on='eventno')
merged_boeventsDF.columns = ['sentype', 'event', 'eventno', 'sentts','recvtype','recvts']
merged_boeventsDF['motion2photon'] = merged_boeventsDF.apply(lambda x: (x.recvts-x.sentts)*1000 + vp8_encode_delay + vp8disp_mean*avg_qframe , axis=1)


#WebRTC Motion to Photon Calculation

#WebRTC Client Display Delay
display_rtcDF = pd.read_csv(r'../inout_data/display.rtc.log', sep=',')
#WebRTC Server Rendering Delay
render_rtcDF = pd.read_csv(r'wifidata11/render.rtc.sr.log', sep=',')
#WebRTC RTT
rtt_rtcDF = pd.read_csv(r'wifidata7/rtt.rtc.log', sep=',')
rtt_rtcDF = rtt_rtcDF.loc[rtt_rtcDF.delay<1000] #remove delays beyond RTT timer (1sec)

merged_rtcDF = pd.merge(render_rtcDF, display_rtcDF, on='frame_no')
merged_rtcDF.columns = ['frame_no', 'rendrdelay', 'dispdelay']
merged_rtcDF['rendrlatency'] = merged_rtcDF.apply(lambda x: x.rendrdelay + x.dispdelay , axis=1)
merged_rtcDF['motion2photon'] = merged_rtcDF.apply(lambda x:  rtt_rtcDF["delay"].mean() - x.rendrdelay - x.dispdelay   , axis=1)

#Motion to Photon statsitics
stats_nebulaDF = merged_eventsDF.describe()
stats_tcpDF = merged_tcpeventsDF.describe()
stats_gopDF = merged_gopeventsDF.describe()
stats_boDF = merged_boeventsDF.describe()
stats_rtcDF = merged_rtcDF.describe()

#Compute Mean
mtpMeans = (stats_nebulaDF['motion2photon']['mean'],stats_tcpDF['motion2photon']['mean'],stats_gopDF['motion2photon']['mean'],
           stats_boDF['motion2photon']['mean'],stats_rtcDF['motion2photon']['mean'])

#Compute STD
mtpStds = (stats_nebulaDF['motion2photon']['std'],stats_tcpDF['motion2photon']['std'],stats_gopDF['motion2photon']['std'],
           stats_boDF['motion2photon']['std'],stats_rtcDF['motion2photon']['std'])

# sns.set(rc={'figure.figsize': (16, 8)}, style='ticks', font_scale=1.5, font='serif')
N = 5
ind = ['Nebula', 'TcpCubic', 'ESCOT', 'BO', 'WebRTC']
width = 0.4  # the width of the bars: can also be len(x) sequence

fig = plt.figure(figsize=(16, 8))
ax = fig.add_subplot(111)

# color='skyblue': indianred, dodgerblue, skyblue, turquoise, mediumseagreen, lightgreen
lowers = np.minimum(mtpStds, mtpMeans)
p1 = plt.bar(ind, mtpMeans, width, yerr=[lowers, mtpStds], log=False, capsize=16,
             error_kw=dict(elinewidth=3, ecolor='black'))
# p2 = plt.bar(ind, mtpMeans, width,
#              bottom=vpxMeans, yerr=rlncStds, log=False, capsize = 16, color='indianred', error_kw=dict(elinewidth=3,ecolor='black'))

plt.margins(0.01, 0)

# Optional code - Make plot look nicer
plt.xticks(rotation=0)
i = 0.15
for row in mtpMeans:
    plt.text(i, row, "{0:.1f}".format(row), color='black', ha="center", fontsize=22)
    i = i + 1

# i=0.15
# totop = 60
# for rlnc,vpx in zip (rlncMeans,vpxMeans):
#     plt.text(i,rlnc + vpx, "{0:.1f}".format(rlnc+vpx), color='black', ha="center", fontsize=22)
#     i = i + 1

ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
params = {'axes.titlesize': 24,
          'axes.labelsize': 24,
          'xtick.labelsize': 24,
          'ytick.labelsize': 24,
          'legend.fontsize': 24,
          'axes.spines.right': False,
          'axes.spines.top': False}
plt.rcParams.update(params)

# , labelrotation=20
plt.tick_params(axis="y", labelsize=24, labelcolor="black")
plt.tick_params(axis="x", labelsize=24, labelcolor="black")
plt.ylabel('Motion to Photon (ms)', fontsize=24)

plt.title('Eduroam WiFi', fontsize=22)
# plt.legend(loc='upper left', ncol=1,labels=['Video coding', 'FEC coding'],
#           prop={'size': 22})
plt.savefig('mtp.pdf', bbox_inches='tight')
plt.show()
