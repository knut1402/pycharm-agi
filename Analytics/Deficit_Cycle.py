#### budget deficit vs unemployment cycle

latest = '20230910'

x1 = con.bdh('EHBBUS Index' , 'PX_LAST', '19841231', latest, longdata = True)
x2 = con.bdh('EHUPUS Index' , 'PX_LAST', '19841231', latest, longdata = True)
x5 = con.bdh('USUDMAER Index' , 'PX_LAST', '19841231', latest, longdata = True)
x4 = con.bdh('FDTR Index' , 'PX_LAST', '19841231', latest, longdata = True)
x4['ff_chg'] = x4['value'].diff(250)

x7 = x5[::-1][::3][::-1]
x7['u6_chg'] = x7['value'].diff(4)

x3 = pd.DataFrame()
x3['u3'] = x2['value']
x3['u3_chg'] = x2['value'].diff(4)
x3['deficit'] = x1['value']
x3['deficit_chg'] = x1['value'].diff(4)
x3['date'] = x2['date']
x3['ind'] = -1*x3['u3_chg']*x3['deficit_chg']

x3[-15:]
np.max(x3['deficit_chg'])
np.max(x3['u3_chg'])

fig, ax1 = plt.subplots(figsize=(10,8))
plt.scatter(x3['u3_chg'],x3['deficit_chg'] )
#plt.legend(loc = 'upper left')
plt.ylabel("deficit _ 3m chg", color="black", fontsize=10)
plt.xlabel("u3 _ 3m chg", color="black", fontsize=10)
plt.title('US Defict vs US U3', color = 'darkblue')
plt.annotate('Source: Bloomberg', (0,0), (0,-20), fontsize=6, xycoords='axes fraction', textcoords='offset points', va='top', style='italic')
plt.show()



fig, ax1 = plt.subplots(3,1,figsize=(10,8))
ax1[0].plot(x3['date'],x3['deficit_chg'], lw = 2, c = 'blue' )
ax2 = ax1[0].twinx()
ax2.plot(x4['date'],x4['value'], c = 'red' )
ax1[1].scatter(x3['date'],x3['u3_chg'], s = 2, c = 'red' )
ax1[2].scatter(x3['date'],x3['ind'], s = 2, c = 'green' )
ax3 = ax1[2].twinx()
ax3.plot(x4['date'],x4['value'], c = 'blue' )
#plt.legend(loc = 'upper left')
#ax1[0].set_ylabel("deficit _ 3m chg", color="black", fontsize=10)
#ax1[1].set_ylabel("u2 _ 3m chg", color="black", fontsize=10)
ax1[0].set_title('US Defict vs US U3', color = 'darkblue')
plt.annotate('Source: Bloomberg', (0,0), (0,-20), fontsize=6, xycoords='axes fraction', textcoords='offset points', va='top', style='italic')
plt.show()



fig, ax1 = plt.subplots(figsize=(10,8))
ax1.plot(x3['date'],x3['deficit_chg'], lw = 2, c = 'blue', label = 'Chg in Deficit: 6m' )
#ax2 = ax1.twinx()
ax1.plot(x4['date'],x4['ff_chg'], c = 'red', label = 'Chg in Fed Funds: 6m' )
ax1.axhline(y= 0.0, color = 'black', lw = 0.8)
ax3 = ax1.twinx()
ax3.plot(x3['date'],-x3['u3_chg'], c = 'green', label = 'Chg in U3: 6m, Inv' )

#ax3.spines['right'].set_position(('axes', 1.06))
ax1.tick_params(colors='red')
ax3.tick_params(colors='green')
ax1.legend(loc = 'upper left')
#ax2.legend(loc = (0.01,0.9))
ax3.legend(loc = (0.01,0.86))

#ax1[0].set_ylabel("deficit _ 3m chg", color="black", fontsize=10)
#ax1[1].set_ylabel("u2 _ 3m chg", color="black", fontsize=10)
ax1.set_title('US: Defict, U3, FF', color = 'darkblue')
plt.annotate('Source: Bloomberg', (0,0), (0,-20), fontsize=6, xycoords='axes fraction', textcoords='offset points', va='top', style='italic')
plt.show()



fig, ax1 = plt.subplots(figsize=(10,8))
ax1.plot(x3['date'],x3['deficit_chg'], lw = 2, c = 'blue', label = 'Deficit' )
ax2 = ax1.twinx()
ax2.plot(x4['date'],x4['value'], c = 'red', label = 'Fed Funds' )
ax2.set_ylim(-2, 10)
ax1.axhline(y= 0.0, color = 'black', lw = 0.8)
#ax3 = ax1.twinx()
#ax1.plot(x3['date'],-x3['u3_chg'], c = 'green', label = 'U3: Inv' )
ax1.plot(x7['date'],-x7['u6_chg'], c = 'limegreen', label = 'U6: Inv' )

#ax3.spines['right'].set_position(('axes', 1.06))
#ax1.tick_params(colors='red')
#ax3.tick_params(colors='green')
ax1.legend(loc = 'upper left')
#ax2.legend(loc = (0.01,0.9))
#ax3.legend(loc = (0.01,0.86))

#ax1[0].set_ylabel("deficit _ 3m chg", color="black", fontsize=10)
#ax1[1].set_ylabel("u2 _ 3m chg", color="black", fontsize=10)
ax1.set_title('US: Defict, U3, FF - 12m Chg', color = 'darkblue')
plt.annotate('Source: Bloomberg', (0,0), (0,-20), fontsize=6, xycoords='axes fraction', textcoords='offset points', va='top', style='italic')
plt.show()

np.min(x3['deficit_chg'])






####### tes dv01

issue_dt = '20211115'
px_at_issuance = con.ref('US91282CDJ71 Govt',['PX_LAST'], ovrds =[(('SETTLE_DT',issue_dt))])['value'][0]
con.ref('US91282CDJ71 Govt', ['YAS_BOND_YLD','YAS_RISK'], ovrds =[('PX_BID',px_at_issuance),(('SETTLE_DT',issue_dt))])



































