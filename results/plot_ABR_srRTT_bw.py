import os
import matplotlib.pyplot as plt
import pandas as pd

currDir = os.path.dirname(os.path.realpath(__file__))
rootDir = os.path.abspath(os.path.join(currDir, '..'))
RTT_LOG_PATH = os.path.join(rootDir, 'MCGserver','rtt.sr.log')

nebula_rtt = pd.read_csv(RTT_LOG_PATH, sep=',')
nebula_rtt = (nebula_rtt.groupby(['seconds']).agg({'rtt':'mean'}).reset_index())
time_stamp = list(nebula_rtt['seconds'])
RTTs = list(nebula_rtt['rtt'])

#Plot Bitrate (throughput Mu vs source rate Re)
BW_LOG_PATH = os.path.join(rootDir, 'MCGserver','bw.sr.log')
nebula_br = pd.read_csv(BW_LOG_PATH, sep=',')
nebula_br = (nebula_br.groupby(['seconds']).agg({'channelrate':'mean','sourcerate':'mean'}).reset_index())
nebula_br['channelrate'] = nebula_br['channelrate'].apply(lambda x: x/1024 )
nebula_br['sourcerate'] = nebula_br['sourcerate'].apply(lambda x: x/1024 )

throughputs = list(nebula_br['channelrate'])
Re = list(nebula_br['sourcerate'])
time_stamp_2 = list(nebula_br['seconds'])

print(time_stamp)
print(RTTs)


fig, (ax1, ax2) = plt.subplots(2, sharex=True)

ax1.plot(time_stamp,RTTs)
ax1.set_ylabel('Roundtrip time (sec)')

lns1 = ax2.plot(time_stamp_2,throughputs, label = 'Mu')
lns2 = ax2.plot(time_stamp_2,Re, label = 'Re')
ax2.set_ylabel('Bitrate (Mb/s)')

#Plot Bitrate (throughput Mu vs source rate Re)
LinkBW_LOG_PATH = os.path.join(rootDir, '..', 'link_bandwidth.txt')
link_bw = pd.read_csv(LinkBW_LOG_PATH, sep=',')
lns3 = ax2.plot(link_bw['seconds'],link_bw['optB'], color='gray', label = 'link bw')
ax2.fill_between( link_bw['seconds'], 0, link_bw['optB'], facecolor='lightgray', interpolate=True)
print("[ lenMu:{}, lenRe:{}, link:{} ]".format(len(throughputs), len(Re),len(link_bw)))

# added these three lines
lns = lns1+lns2+lns3
labs = [l.get_label() for l in lns]
ax2.legend(lns, labs, loc=0)

# plt.savefig('rtt_Re_nebula.pdf', bbox_inches='tight')
plt.show()
