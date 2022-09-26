import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
# import seaborn as sns
import os

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


experiments_dir_names = ['wifidata5','wifidata6','wifidata7','wifidata8','wifidata11']
#PSNR statsitics
nebulaDF = aggregatePSNR_nebula(experiments_dir_names)
escotDF = aggregatePSNR_gop(experiments_dir_names)
tcpDF = aggregatePSNR_tcp(experiments_dir_names)
boDF = aggregatePSNR_bo(experiments_dir_names)
webrtcDF = aggregatePSNR_webrtc(experiments_dir_names)
######
stats_nebulaDF = nebulaDF.describe()
stats_tcpDF = tcpDF.describe()
stats_gopDF = escotDF.describe()
stats_boDF = boDF.describe()
stats_rtcDF = webrtcDF.describe()

#Compute Mean
mtpMeans = (stats_nebulaDF['psnr']['mean'],stats_tcpDF['psnr']['mean'],stats_gopDF['psnr']['mean'],
           stats_boDF['psnr']['mean'],stats_rtcDF['psnr']['mean'])

#Compute STD
mtpStds = (stats_nebulaDF['psnr']['std'],stats_tcpDF['psnr']['std'],stats_gopDF['psnr']['std'],
           stats_boDF['psnr']['std'],stats_rtcDF['psnr']['std'])


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
plt.ylabel('PSNR (dB)', fontsize=24)

# plt.title('Motion to Photo (ms)', fontsize=22)
# plt.legend(loc='upper left', ncol=1,labels=['Video coding', 'FEC coding'],
#           prop={'size': 22})
# plt.savefig('psnr_wifi.pdf', bbox_inches='tight')
fig.savefig('psnr_wifi.eps', format='eps',bbox_inches='tight')
plt.show()



