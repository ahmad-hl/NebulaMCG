import os
import matplotlib.pyplot as plt
import pandas as pd


currDir = os.path.dirname(os.path.realpath(__file__))
# os.chdir(rootDir)
print(os.getcwd())

def getMu_nebula(exper_dir_name):
    LOG_PATH = os.path.join(currDir, exper_dir_name, 'bw.sr.log')
    thourghputDF = pd.read_csv(LOG_PATH)
    thourghputDF['Mu'] = thourghputDF['sourcerate'].apply(lambda x: x / 1024)
    thourghputDF = thourghputDF.groupby(['seconds']).mean().reset_index()
    thourghputDF = thourghputDF[['seconds','Mu']]

    return thourghputDF

def getMu_gop(exper_dir_name):
    LOG_PATH = os.path.join(currDir, exper_dir_name, 'bw.gop.sr.log')
    thourghputDF = pd.read_csv(LOG_PATH)
    thourghputDF['Mu'] = thourghputDF['sourcerate'].apply(lambda x: x/1024)
    thourghputDF = thourghputDF.groupby(['seconds']).mean().reset_index()
    thourghputDF = thourghputDF[['seconds', 'Mu']]
    return thourghputDF

def getMu_bo(exper_dir_name):
    LOG_PATH = os.path.join(currDir, exper_dir_name, 'bw.bo.cl.log')
    clThourghputDF = pd.read_csv(LOG_PATH)
    clThourghputDF['Mu'] = clThourghputDF['bw'].apply(lambda x: x/1024)

    return clThourghputDF

def getMu_tcp(exper_dir_name):
    LOG_PATH = os.path.join(currDir, exper_dir_name, 'bw.tcp.cl.log')
    clThourghputDF = pd.read_csv(LOG_PATH)
    clThourghputDF['Mu'] = clThourghputDF['bw'].apply(lambda x: x/1024)

    return clThourghputDF

def getMu_webrtc(exper_dir_name):
    LOG_PATH = os.path.join(currDir, exper_dir_name, 'bw.rtc.cl.log')
    clThourghputDF = pd.read_csv(LOG_PATH)
    clThourghputDF.drop('frame_no',axis=1, inplace=True)
    clThourghputDF = clThourghputDF.groupby(['seconds']).mean().reset_index()
    clThourghputDF = clThourghputDF.rename(columns={'bw': 'Mu'})
    # clThourghputDF['Mu'] = clThourghputDF['Mu'].apply(lambda x: x + 0.4 * x) # Add 40% for RTP & RTCP packet headers and overhead

    return clThourghputDF

def getLink_bw(exper_dir_name):
    LOG_PATH = os.path.join(currDir, exper_dir_name, 'link_bandwidth.txt')
    bwDF = pd.read_csv(LOG_PATH)
    bwDF.drop(['timestamp','minsec'], axis=1, inplace=True)
    bwDF = bwDF.groupby(['seconds']).mean().reset_index()
    bwDF.rename(columns={'optB': 'bw'}, inplace= True)
    print(bwDF)
    return bwDF


exper_dir_name = 'ethdata6'
nebulaMuDF = getMu_nebula(exper_dir_name)
nebulaMuDF['ID'] = nebulaMuDF.index
nebulaMuDF = nebulaMuDF.loc[nebulaMuDF.ID<=60]
gopMuDF = getMu_gop(exper_dir_name)
gopMuDF['ID'] = gopMuDF.index
gopMuDF = gopMuDF.loc[gopMuDF.ID<=60]
boMuDF = getMu_bo(exper_dir_name)
boMuDF['ID'] = boMuDF.index
boMuDF = boMuDF.loc[boMuDF.ID<=60]
tcpMuDF = getMu_tcp(exper_dir_name)
tcpMuDF['ID'] = tcpMuDF.index
tcpMuDF = tcpMuDF.loc[tcpMuDF.ID<=60]
webrtcMuDF = getMu_webrtc(exper_dir_name)
webrtcMuDF['ID'] = webrtcMuDF.index
webrtcMuDF = webrtcMuDF.loc[webrtcMuDF.ID<=60]

#Link Bandwidth
bwDF = getLink_bw(exper_dir_name)
bwDF['ID'] = bwDF.index
bwDF = bwDF.loc[bwDF.ID<=60]

fig = plt.figure(figsize=(12,8))
ax = fig.add_subplot(111)

# plot lines
# color='skyblue': indianred, dodgerblue, turquoise, mediumseagreen, lightgreen
plt.plot(nebulaMuDF['ID'], nebulaMuDF['Mu'], color='mediumseagreen', linestyle="-", label='Nebula')
plt.plot(gopMuDF['ID'], gopMuDF['Mu'],color='black', linestyle="--", label='ESCOT')
plt.plot(boMuDF['ID'], boMuDF['Mu'], color='turquoise', linestyle="solid", label='BO')
plt.plot(tcpMuDF['ID'], tcpMuDF['Mu'], color='red', linestyle="dashdot", label='TCP(Cubic)')
plt.plot(webrtcMuDF['ID'], webrtcMuDF['Mu'], color='indianred', linestyle="solid", label='WebRTC')
# plt.plot(bwDF['ID'], bwDF['bw'], label='Link BW')
ax.fill_between(bwDF['ID'], 0, bwDF['bw'], facecolor='lightgray',interpolate=True)

plt.ylabel('Throughput (Mbps)')
plt.legend()
plt.show()




