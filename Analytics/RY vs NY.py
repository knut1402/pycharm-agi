import numpy as np

us_ry = ['US91282CAQ42', 'US9128285W63', 'US91282CHP95', 'US912810TE82']
us_ny = ['US91282CAT80', 'US9128286B18', 'US91282CHT18', 'US912810TD00']

eu_ry = ['FR0013519253', 'IT0005246134' ,'FR001400JI88', 'IT0005436701']
eu_ny = ['FR0013508470', 'IT0004889033' ,'FR0013313582', 'IT0005425233']

uk_ry = ['GB00BYY5F144', 'GB00B3Y1JG82' ,'GB00B46CGH68', 'GB00B73ZYW09']
uk_ny = ['GB00BL68HJ26', 'GB00BLPK7227' ,'GB00B52WS153', 'GB00B6RNH572']

d1 = '20231021'
d2 = '20231206'


us_ry1 = [con.ref(us_ry[i]+' Govt', ['YAS_BOND_YLD'], ovrds =[(('SETTLE_DT',d1))])['value'][0] for i in np.arange(len(us_ry))]
us_ry2 = [con.ref(us_ry[i]+' Govt', ['YAS_BOND_YLD'], ovrds =[(('SETTLE_DT',d2))])['value'][0] for i in np.arange(len(us_ry))]

us_ny1 = [con.ref(us_ny[i]+' Govt', ['YAS_BOND_YLD'], ovrds =[(('SETTLE_DT',d1))])['value'][0] for i in np.arange(len(us_ny))]
us_ny2 = [con.ref(us_ny[i]+' Govt', ['YAS_BOND_YLD'], ovrds =[(('SETTLE_DT',d2))])['value'][0] for i in np.arange(len(us_ny))]

us_ry_chg = 100*(np.array(us_ry2) - np.array(us_ry1))
us_ny_chg = 100*(np.array(us_ny2) - np.array(us_ny1))
us_bei_chg = us_ny_chg-us_ry_chg

uk_ry1 = [con.ref(uk_ry[i]+' Govt', ['YAS_BOND_YLD'], ovrds =[(('SETTLE_DT',d1))])['value'][0] for i in np.arange(len(uk_ry))]
uk_ry2 = [con.ref(uk_ry[i]+' Govt', ['YAS_BOND_YLD'], ovrds =[(('SETTLE_DT',d2))])['value'][0] for i in np.arange(len(uk_ry))]

uk_ny1 = [con.ref(uk_ny[i]+' Govt', ['YAS_BOND_YLD'], ovrds =[(('SETTLE_DT',d1))])['value'][0] for i in np.arange(len(uk_ny))]
uk_ny2 = [con.ref(uk_ny[i]+' Govt', ['YAS_BOND_YLD'], ovrds =[(('SETTLE_DT',d2))])['value'][0] for i in np.arange(len(uk_ny))]

uk_ry_chg = 100*(np.array(uk_ry2) - np.array(uk_ry1))
uk_ny_chg = 100*(np.array(uk_ny2) - np.array(uk_ny1))
uk_bei_chg = uk_ny_chg-uk_ry_chg


eu_ry1 = [con.ref(eu_ry[i]+' Govt', ['YAS_BOND_YLD'], ovrds =[(('SETTLE_DT',d1))])['value'][0] for i in np.arange(len(eu_ry))]
eu_ry2 = [con.ref(eu_ry[i]+' Govt', ['YAS_BOND_YLD'], ovrds =[(('SETTLE_DT',d2))])['value'][0] for i in np.arange(len(eu_ry))]

eu_ny1 = [con.ref(eu_ny[i]+' Govt', ['YAS_BOND_YLD'], ovrds =[(('SETTLE_DT',d1))])['value'][0] for i in np.arange(len(eu_ny))]
eu_ny2 = [con.ref(eu_ny[i]+' Govt', ['YAS_BOND_YLD'], ovrds =[(('SETTLE_DT',d2))])['value'][0] for i in np.arange(len(eu_ny))]

eu_ry_chg = 100*(np.array(eu_ry2) - np.array(eu_ry1))
eu_ny_chg = 100*(np.array(eu_ny2) - np.array(eu_ny1))
eu_bei_chg = eu_ny_chg-eu_ry_chg






mat = [2,5,10,30]
us_nom = us_ny_chg
us_bei = us_bei_chg
us_ry = us_ry_chg
uk_nom = uk_ny_chg
uk_bei = uk_bei_chg
uk_ry = uk_ry_chg
eu_nom = eu_ny_chg
eu_bei = eu_bei_chg
eu_ry = eu_ry_chg

ind = [x for x, _ in enumerate(mat)]

us_bei2 = us_bei + us_ry.clip(min=0)
uk_bei2 = uk_bei + uk_ry.clip(min=0)
eu_bei2 = eu_bei + eu_ry.clip(min=0)

plt.figure(figsize=(10,10))
plt.bar(ind, us_ry, width=0.2, label='usd:ry', color='blue',zorder=2)
plt.bar(ind, us_bei2, width=0.2, bottom = us_ry, label='usd:bei', color='#CD853F')
plt.scatter(ind, us_nom, label='usd:nom', color='blue', s=20,zorder=3)

plt.bar(np.array(ind)+0.25, uk_ry, width=0.2, label='uk:ry', color='green',zorder=2)
plt.bar(np.array(ind)+0.25, uk_bei2, width=0.2, bottom = uk_ry, label='uk:bei', color='#CD853F')
plt.scatter(np.array(ind)+0.25, uk_nom, label='uk:nom', color='green', s=20,zorder=3)

plt.bar(np.array(ind)+0.5, eu_ry, width=0.2, label='eu:ry', color='red',zorder=2)
plt.bar(np.array(ind)+0.5, eu_bei2, width=0.2, bottom = eu_ry, label='eu:bei', color='#CD853F')
plt.scatter(np.array(ind)+0.5, eu_nom, label='eu:nom', color='red', s=20,zorder=3)

plt.axhline(0, color='black')
plt.xticks(np.array(ind)+0.25, mat, rotation=0, fontsize=15)
plt.yticks(fontsize=15)
plt.ylabel("yield chg",fontsize=15)
plt.xlabel("maturity",fontsize=15)
plt.legend(loc="best",prop={'size': 12})
plt.title("Yield Chgs from peak 19th Oct",fontsize=15)
plt.show()



fig, ax1 = plt.subplots(3,1,figsize=(10,8))
ax1[0].bar(ind, us_ry, width=0.2, label='usd:ry', color='blue',zorder=2)
ax1[0].bar(ind, us_bei2, width=0.2, bottom = us_ry, label='usd:bei', color='#CD853F')
ax1[0].scatter(ind, us_nom, label='usd:nom', color='blue', s=20,zorder=3)
ax1[1].bar(np.array(ind)+0.25, uk_ry, width=0.2, label='uk:ry', color='green',zorder=2)
ax1[1].bar(np.array(ind)+0.25, uk_bei2, width=0.2, bottom = uk_ry, label='uk:bei', color='#CD853F')
ax1[1].scatter(np.array(ind)+0.25, uk_nom, label='uk:nom', color='green', s=20,zorder=3)
ax1[2].bar(np.array(ind)+0.5, eu_ry, width=0.2, label='eu:ry', color='red',zorder=2)
ax1[2].bar(np.array(ind)+0.5, eu_bei2, width=0.2, bottom = eu_ry, label='eu:bei', color='#CD853F')
ax1[2].scatter(np.array(ind)+0.5, eu_nom, label='eu:nom', color='red', s=20,zorder=3)
#plt.axhline(0, color='black')
#ax1[0].xticks(np.array(ind)+0.25, mat, rotation=0, fontsize=15)
#ax1[0].yticks(fontsize=15)
ax1[0].set_ylabel("yield chg",fontsize=15)
ax1[0].set_xlabel("maturity",fontsize=15)
ax1[0].legend(loc="best",prop={'size': 12})
#plt.title("Yield Chgs from peak 19th Oct",fontsize=15)
plt.show()

