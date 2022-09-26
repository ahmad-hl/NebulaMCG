import os
import matplotlib.pyplot as plt
import pandas as pd


currDir = os.path.dirname(os.path.realpath(__file__))
LOG_PATH = os.path.join(currDir, 'ethdata1','bw.gop.sr.log')
# os.chdir(rootDir)
print(os.getcwd())

clThourghputDF = pd.read_csv(LOG_PATH)
print(clThourghputDF.head())

plt.plot(clThourghputDF['seconds'], clThourghputDF['sourcerate']/1024)
plt.ylabel('Eduroam throughput (Mbps)')
#
# LOG_PATH_2 = os.path.join(rootDir, 'client','plr.cl.log')
# cl_plrDF = pd.read_csv(LOG_PATH_2)
# cl_plrDF = cl_plrDF.loc[cl_plrDF['lostpkts'] >1]
# print('packet loss:')
# print(cl_plrDF.head())

plt.show()




