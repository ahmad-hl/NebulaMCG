import numpy as np
from sklearn.linear_model import LinearRegression
import os
import pandas as pd

vp8_encode_delay =  20.8
currDir = os.path.dirname(os.path.realpath(__file__))
#Motion to Photon
def computeMTP_nebula(dir_names):

    column_names = ['Mu', 'Re', 'Rr', 'mtp', 'rtt', 'Qd']
    rateMuRttDF =  pd.DataFrame(columns = column_names)
    #Nebula Motion to Photon Calculation
    for dir_name in dir_names:
        #Nebula Motion to Photon Calculation
        LOG_EVENT_PATH = os.path.join(currDir, '..', 'results', dir_name, 'event.cl.log')
        eventsDF = pd.read_csv(LOG_EVENT_PATH, sep=',')
        sent_eventsDF = eventsDF.loc[eventsDF.type=='sent']
        recv_eventsDF = eventsDF.loc[eventsDF.type=='recv']
        recv_eventsDF = recv_eventsDF.drop(['event'], axis=1)
        merged_eventsDF = pd.merge(sent_eventsDF, recv_eventsDF, on='eventno')
        merged_eventsDF.columns = ['sentype', 'event', 'eventno', 'sentts','recvtype','recvts']
        merged_eventsDF = merged_eventsDF.assign(mtp = lambda x: (x.recvts-x.sentts)*1000 + vp8_encode_delay , axis=1)
        merged_eventsDF = merged_eventsDF.assign(seconds=lambda x: round(x.sentts) , axis=1)
        mtpDF = merged_eventsDF[['seconds','mtp']]
        LOG_THRO_PATH = os.path.join(currDir, '..', 'results', dir_name, 'bw.sr.log')
        thourghputDF = pd.read_csv(LOG_THRO_PATH)
        thourghputDF = thourghputDF.loc[thourghputDF.channelrate < 200000]
        rateDF = thourghputDF[['seconds', 'channelrate','sourcerate','redundancyrate']]
        mergedRateMuDF = pd.merge(rateDF, mtpDF, on='seconds')

        LOG_RTT_PATH = os.path.join(currDir, '..', 'results', dir_name, 'rtt.sr.log')
        RTTDF = pd.read_csv(LOG_RTT_PATH, sep=',')
        RTTDF = RTTDF[['seconds', 'rtt']]
        #Compute min RTT
        RTTmin = np.min(RTTDF['rtt'])
        mergedRateMu_RTTDF = pd.merge(mergedRateMuDF, RTTDF, on='seconds')

        # Group the data frame by month and item and extract a number of stats from each group
        mergedRateMu_RTTDF =  mergedRateMu_RTTDF.groupby(['seconds']).agg({'channelrate': 'mean', 'sourcerate': 'mean', 'redundancyrate': 'mean', 'mtp':'mean', 'rtt':'mean'})

        # Compute Queuing delay
        mergedRateMu_RTTDF = mergedRateMu_RTTDF.assign(Qd = lambda x: x.rtt - RTTmin )
        mergedRateMu_RTTDF = mergedRateMu_RTTDF.rename(columns={'channelrate': 'Mu','sourcerate': 'Re', 'redundancyrate': 'Rr' })
        mergedRateMu_RTTDF['Mu'] = mergedRateMu_RTTDF['Mu'].apply( lambda x: x/ 1024) #Kb/s --> Mb/s
        mergedRateMu_RTTDF['Re'] = mergedRateMu_RTTDF['Re'].apply(lambda x: x / 1024) #Kb/s --> Mb/s
        mergedRateMu_RTTDF['Rr'] = mergedRateMu_RTTDF['Rr'].apply(lambda x: x / 1024) #Kb/s --> Mb/s
        mergedRateMu_RTTDF = mergedRateMu_RTTDF.assign(R=lambda x: x.Rr + x.Re)       #R = Re+Rr
        rateMuRttDF = pd.concat([rateMuRttDF, mergedRateMu_RTTDF])

    return rateMuRttDF

dir_names = ['ethdata1','ethdata2','ethdata3','ethdata4','ethdata5','ethdata6','ethdata7','ethdata8','wifi_expr1','wifi_expr2','wifi_expr3']
rateMuRttDF = computeMTP_nebula(dir_names)
print(rateMuRttDF.head())
x=[]
y=[]
for Mu,R,rtt,Qd,mtp in zip(rateMuRttDF['Mu'],rateMuRttDF['R'],rateMuRttDF['rtt'],rateMuRttDF['Qd'], rateMuRttDF['mtp']):
    x.append([1/Mu,1/R,Qd])
    y.append(mtp)
x, y = np.array(x), np.array(y)
model = LinearRegression().fit(x, y)
r_sq = model.score(x, y)
print('R2:', r_sq, 'intercept:', model.intercept_,'slope:', model.coef_)