import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

currDir = os.path.dirname(os.path.realpath(__file__))
WiFi_BW_CSV_PATH = os.path.join(currDir, 'EduroamPerf', 'wifi_bw.csv')
WiFi_RTT_CSV_PATH = os.path.join(currDir,'EduroamPerf', 'wifi_rtt.csv')
# Read PSNR CSV
wifiBw = pd.read_csv(WiFi_BW_CSV_PATH, sep=',')
wifiBw.columns = ['wifi_bw']
wifiRTT = pd.read_csv(WiFi_RTT_CSV_PATH, sep=',')
wifiRTT.columns = ['wifi_rtt']

wifiBw['seqno'] = wifiBw.index
wifiRTT['seqno'] = wifiRTT.index

wifiPerfDF = pd.merge(wifiBw, wifiRTT, on='seqno')
wifiPerfDF = wifiPerfDF[['seqno','wifi_bw','wifi_rtt']]
print(wifiPerfDF.head(5))



#Motion to Photon statsitics
stats_wifiPerfDF = wifiPerfDF.describe()
perfMeans = (stats_wifiPerfDF['wifi_bw']['mean'],stats_wifiPerfDF['wifi_rtt']['mean'])

perfStds = (stats_wifiPerfDF['wifi_bw']['std'],stats_wifiPerfDF['wifi_rtt']['std'])

# color='skyblue': indianred, dodgerblue, skyblue, turquoise, mediumseagreen, lightgreen
fig = plt.figure(figsize=(4, 3))
ax = fig.add_subplot(111)
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.spines['left'].set_visible(False)
width=0.3

ind = ['B (Mb/s)', 'RTT (ms)']
lowerPerfStd = np.minimum(perfStds, perfMeans)
p1 = plt.bar(ind, perfMeans, width, yerr=[lowerPerfStd, perfStds], log=False, capsize=3,
             color='dodgerblue', error_kw=dict(elinewidth=2, ecolor='black'))
# Optional code - Make plot look nicer
i = 0.12
for row in perfMeans:
    plt.text(i, row, "{0:.1f}".format(row), color='black', ha="center", fontsize=18)
    i = i + 1

i = -0.005
for perfStd,perfMean in zip(perfStds, perfMeans):
    plt.text(i, perfStd+perfMean, "+{0:.1f}".format(perfStd), color='gray', ha="center", fontsize=18)
    # plt.text(i,  perfMean - perfStd , "{0:.1f}-{1:.1f}".format(perfMean, perfStd), color='gray', ha="center", fontsize=16)
    i = i + 1

# plt.xticks(fontsize=18, rotation=30)
# plt.xticks(color='w')
plt.yticks(color='w')
plt.tick_params(left=False)
# fig.savefig('perf_wifi.eps', format='eps',bbox_inches='tight')
fig.savefig('perf_wifi.pdf',bbox_inches='tight')
plt.show()


