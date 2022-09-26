import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


nebulaQoE = pd.read_csv(r'userstudy/nebulaQoE.csv', sep=',')
nebulaQoE.head()

# ax = sns.barplot(x="Solution", y="VQ", data=nebulaQoE, capsize=.2)
# ax = sns.barplot(x="Solution", y="Playability", data=nebulaQoE, capsize=.2)
# ax = sns.barplot(x="Solution", y="Score", data=nebulaQoE, capsize=.2)
# ax = sns.barplot(x="Solution", y="Success", data=nebulaQoE, capsize=.2)
# ax = sns.barplot(x="Solution", y="Mental", data=nebulaQoE, capsize=.2)
# ax = sns.barplot(x="Solution", y="Frustration", data=nebulaQoE, capsize=.2)


fig, axs = plt.subplots(2, 3, figsize=(10,6), squeeze=True)

sns.set(style="darkgrid")
sns.barplot(nebulaQoE['Solution'], nebulaQoE['VQ'], alpha=0.9,ax = axs[0][0], capsize=.2)
sns.barplot(nebulaQoE['Solution'], nebulaQoE['Playability'], alpha=0.9,ax = axs[0][1], capsize=.2)
sns.barplot(nebulaQoE['Solution'], nebulaQoE['Score'], alpha=0.9,ax = axs[0][2], capsize=.2)
sns.barplot(nebulaQoE['Solution'], nebulaQoE['Success'], alpha=0.9,ax = axs[1][0], capsize=.2)
sns.barplot(nebulaQoE['Solution'], nebulaQoE['Mental'], alpha=0.9,ax = axs[1][1], capsize=.2)
sns.barplot(nebulaQoE['Solution'], nebulaQoE['Frustration'], alpha=0.9,ax = axs[1][2], capsize=.2)
# plt.ylabel('Visual Quality', fontsize=12)
plt.xlabel('', fontsize=12)
plt.tight_layout()
plt.savefig('QoE.pdf', bbox_inches='tight')
plt.show()