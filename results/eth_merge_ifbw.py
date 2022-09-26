import os
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


currDir = os.path.dirname(os.path.realpath(__file__))
# os.chdir(rootDir)
print(os.getcwd())

def getMu_nebula(exper_dir_name):
    LOG_PATH = os.path.join(currDir, exper_dir_name, 'ifbw.cl.log')
    thourghputDF = pd.read_csv(LOG_PATH)
    thourghputDF['Nebula'] = thourghputDF['bw'].apply(lambda x: x / 1024.0)
    thourghputDF.drop(['bw', 'seconds'], axis=1, inplace=True)

    return thourghputDF

def getMu_gop(exper_dir_name):
    LOG_PATH = os.path.join(currDir, exper_dir_name, 'ifbw.gop.cl.log')
    thourghputDF = pd.read_csv(LOG_PATH)
    thourghputDF['ESCOT'] = thourghputDF['bw'].apply(lambda x: x/1024.0)
    thourghputDF.drop(['bw', 'seconds'], axis=1, inplace=True)

    return thourghputDF

def getMu_bo(exper_dir_name):
    LOG_PATH = os.path.join(currDir, exper_dir_name, 'ifbw.bo.cl.log')
    thourghputDF = pd.read_csv(LOG_PATH)
    thourghputDF['BO'] = thourghputDF['bw'].apply(lambda x: x/1024.0)
    thourghputDF.drop(['bw', 'seconds'], axis=1, inplace=True)

    return thourghputDF

def getMu_tcp(exper_dir_name):
    LOG_PATH = os.path.join(currDir, exper_dir_name, 'ifbw.tcp.cl.log')
    thourghputDF = pd.read_csv(LOG_PATH)
    thourghputDF['TCP/Cubic'] = thourghputDF['bw'].apply(lambda x: x/1024.0)
    thourghputDF.drop(['bw', 'seconds'], axis=1, inplace=True)

    return thourghputDF

def getMu_webrtc(exper_dir_name):
    LOG_PATH = os.path.join(currDir, exper_dir_name, 'ifbw.rtc.cl.log')
    thourghputDF = pd.read_csv(LOG_PATH)
    thourghputDF.drop('frame_no', axis=1, inplace=True)
    thourghputDF = thourghputDF.groupby(['seconds']).mean().reset_index()
    thourghputDF['WebRTC'] = thourghputDF['bw'].apply(lambda x: x / 1024.0)
    thourghputDF.drop(['bw', 'seconds'], axis=1, inplace=True)

    return thourghputDF

def getLink_bw(exper_dir_name):
    LOG_PATH = os.path.join(currDir, exper_dir_name, 'link_bandwidth.txt')
    bwDF = pd.read_csv(LOG_PATH)
    bwDF.drop(['timestamp','minsec'], axis=1, inplace=True)
    bwDF = bwDF.groupby(['seconds']).mean().reset_index()
    bwDF.rename(columns={'optB': 'bw'}, inplace= True)
    return bwDF


exper_dir_name = 'ethdata6'
video_long = 59 #Take only 60 seconds = video-long time /or 540
nebulaMuDF = getMu_nebula(exper_dir_name)
nebulaMuDF = nebulaMuDF.loc[nebulaMuDF.index<=video_long]
gopMuDF = getMu_gop(exper_dir_name)
gopMuDF = gopMuDF.loc[gopMuDF.index<=video_long]
boMuDF = getMu_bo(exper_dir_name)
boMuDF = boMuDF.loc[boMuDF.index<=video_long]
tcpMuDF = getMu_tcp(exper_dir_name)
tcpMuDF = tcpMuDF.loc[tcpMuDF.index<=video_long]
webrtcMuDF = getMu_webrtc(exper_dir_name)
webrtcMuDF = webrtcMuDF.loc[webrtcMuDF.index<=video_long]

allbwDF = pd.concat([nebulaMuDF, gopMuDF, boMuDF, tcpMuDF, webrtcMuDF], axis=1)
print(allbwDF)
#Link Bandwidth
bwDF = getLink_bw(exper_dir_name)
bwDF = bwDF.loc[bwDF.index<=video_long]

fig = plt.figure(figsize=(12, 6), tight_layout=True)
ax = fig.add_subplot(111)

# plot lines
sns.set(font_scale=1.6)
# sns.set_theme(style="darkgrid")
# sns.set(style="whitegrid")
paper_rc = {'lines.linewidth': 2, 'lines.markersize': 8,'legend.fontsize': 18,
          'legend.handlelength': 2}
sns.set_context("paper", rc=paper_rc)

p = sns.lineplot(data=allbwDF, linewidth=3, markers=True, palette='colorblind') #palette=[hls, Dark2, Set1, tab10,Paired],  dashes=False
p.fill_between(bwDF.index, 0, bwDF['bw'], facecolor='lightgray',interpolate=True)
p.set_xlabel("Time (sec)", fontsize=18)
p.set_ylabel("Throughput (Mbps)", fontsize=18)
p.set_title("Bandwidth Utilization", fontsize=18)

p.tick_params(axis='both', which='major', labelsize=15)
p.spines['right'].set_visible(False)
p.spines['top'].set_visible(False)
p.legend(title_fontsize=20,framealpha=0.0, ncol=3, fancybox=True,loc='upper right')

plt.savefig('bw_usage_eth.pdf', bbox_inches='tight')
fig.savefig('bw_usage_eth.eps', format='eps',bbox_inches='tight')
plt.show()




