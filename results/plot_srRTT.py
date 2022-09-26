import os
import matplotlib.pyplot as plt
import pandas as pd

currDir = os.path.dirname(os.path.realpath(__file__))
rootDir = os.path.abspath(os.path.join(currDir, '..'))
RTT_LOG_PATH = os.path.join(rootDir, 'inout_data','rtt.sr.log')

nebula_rtt = pd.read_csv(RTT_LOG_PATH, sep=',')
nebula_rtt = (nebula_rtt.groupby(['seconds']).agg({'rtt':'min'}).reset_index())

BW_LOG_PATH = os.path.join(rootDir, 'inout_data','bw.sr.log')
nebula_bw = pd.read_csv(BW_LOG_PATH, sep=',')
nebula_bw =  nebula_bw.loc[nebula_bw['channelrate']<200000] #200000 is intial bw

fig, (ax1, ax2) = plt.subplots(2, sharex=True)

ax1.plot(nebula_rtt['seconds'], nebula_rtt['rtt'])
ax1.set_ylabel('Roundtrip time (sec)')
ax2.plot(nebula_bw['seconds'], nebula_bw['channelrate']/1024)
ax2.set_ylabel('bandwidth (Mb/s)')


plt.savefig('rtt_tcp.pdf', bbox_inches='tight')
plt.show()
