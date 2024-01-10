##### historical regression analysis

latest = '20230711'
s3 = con.bdh('USOSFR3 Curncy' , 'PX_LAST', '20220703', latest, longdata = True)
s5 = con.bdh('USOSFR5 Curncy' , 'PX_LAST', '20220703', latest, longdata = True)
s7 = con.bdh('USOSFR7 Curncy' , 'PX_LAST', '20220703', latest, longdata = True)

d1 = pd.DataFrame()
d1['date'] = s5['date']

r1=[]
r2=[]
for i in np.arange(len(d1)):
    r1.append(100*(s7[s7['date'] == d1['date'][i]]['value'].tolist()[0] - s3[s3['date'] == d1['date'][i]]['value'].tolist()[0]))
    r2.append( s5[s5['date'] == d1['date'][i]]['value'].tolist()[0])

d1['usd_3s7s'] = r1
d1['usd_5s'] = r2


d2 = d1[d1['date'] < ql_to_datetime(ql.Date(1,3,2023))]
d3 = d1[d1['date'] > ql_to_datetime(ql.Date(28,2,2023))]

plt.figure(figsize=(18,12))
plt.scatter(d2['usd_5s'], d2['usd_3s7s'], c='b', s=7, label = "Jul-22 - Mar-23 coeff: "+ str(np.round(regr1.coef_[0],1)))
plt.plot(d2['usd_5s'], y1, color="blue", linewidth=3)
plt.scatter(d3['usd_5s'], d3['usd_3s7s'], c='r', s=7, label = "Mar-23 - Jul-23 coeff: "+ str(np.round(regr2.coef_[0],1)))
plt.plot(d3['usd_5s'], y2, color="red", linewidth=3)
plt.grid(linestyle='--', linewidth=0.3)
plt.xlabel('SOFR 5y (%)')
plt.ylabel('SOFR 3s7s Curve (bps)')
plt.title('SOFR Curve Beta')
#plt.tight_layout()
plt.legend()
plt.show()

#
from sklearn import linear_model
regr1 = linear_model.LinearRegression()
regr2 = linear_model.LinearRegression()

# Train the model using the training sets
regr1.fit( np.array(d2['usd_5s']).reshape(-1,1), np.array(d2['usd_3s7s']))
regr2.fit( np.array(d3['usd_5s']).reshape(-1,1), np.array(d3['usd_3s7s']))


y1 = regr1.predict(np.array(d2['usd_5s']).reshape(-1,1))
y2 = regr2.predict(np.array(d3['usd_5s']).reshape(-1,1))

plt.plot(np.array(d2['usd_5s']), y1)
plt.show()

regr1.coef_
regr2.coef_

sofr = ois_dc_build('SOFR_DC')

Swap_Pricer([[sofr,'21-09-2023',3],[sofr,'21-09-2023',7]]).table
Swap_Pricer([[sofr,'21-12-2023',3],[sofr,'21-12-2023',7]]).table
Swap_Pricer([[sofr,'21-03-2024',3],[sofr,'21-03-2024',7]]).table

#################### looking at rolling correlations betas
latest = '20230711'
f3 = con.bdh('USOSFR3 Curncy' , 'PX_LAST', '20120703', latest, longdata = True)
f5 = con.bdh('USOSFR5 Curncy' , 'PX_LAST', '20120703', latest, longdata = True)
f7 = con.bdh('USOSFR7 Curncy' , 'PX_LAST', '20120703', latest, longdata = True)

g1 = pd.DataFrame()
g1['date'] = f7['date']

g1 = pd.merge(f3, f5, on='date', how='outer')
g1 = pd.merge(g1, f7, on='date', how='outer')

g1 = g1.dropna()

g1['usd_3s7s'] = 100*(g1['value'] - g1['value_x'])
g1['usd_5s'] = g1['value_y']


c1 = []
c2 = []
window_size = 90
for i in np.arange(0,len(g1)-window_size):
    regr1.fit(np.array(g1['usd_5s']).reshape(-1, 1)[i:i+window_size], np.array(g1['usd_3s7s'])[i:i+window_size])
    c2.append(100*(g1['usd_5s'].iloc[i+window_size] - g1['usd_5s'].iloc[i] ))
    c1.append(regr1.coef_[0])

plt.figure(figsize=(18,12))
plt.scatter(g1['date'][:-window_size],c1, s=3, c='g')
plt.grid(linestyle='--', linewidth=0.3)
plt.axhline(0)
#plt.bar(g1['date'][:-window_size],c2)
plt.xlabel('Date')
plt.ylabel('Beta')
plt.title('rolling 90d correlation beta: 3s7s vs 5s')
plt.show()


plt.figure(figsize=(18,12))
plt.scatter(c2,c1, s=3, c='g')
#plt.bar(g1['date'][:-window_size],c2)
plt.xlabel('5y rate chg')
plt.ylabel('Beta')
plt.title('rolling 90d correlation beta: 3s7s vs 5s')
plt.show()


###### pearson's r = correl coeff
from scipy.stats import pearsonr

v1 = []
v2 = []
v3 = []
window_size = 50
for i in np.arange(0,len(g1)-window_size):
    v1.append(100 * (g1['usd_5s'].iloc[i + window_size] - g1['usd_5s'].iloc[i]))
    v3.append( g1['usd_3s7s'].iloc[i + window_size] - g1['usd_3s7s'].iloc[i])
    v2.append(pearsonr(g1['usd_5s'][i:i+window_size], g1['usd_3s7s'][i:i+window_size])[0])


plt.figure(figsize=(18,12))
plt.scatter(g1['date'][:-window_size],v2, s=3, c='g', label = 'Pearson R Coeff.')
plt.grid(linestyle='--', linewidth=0.3)
plt.axhline(0)
#plt.bar(g1['date'][:-window_size],np.array(v1)/100, label = str(window_size)+'d chg in 5s')
#plt.bar(g1['date'][:-window_size],np.array(v3)/100, label = str(window_size)+'d chg in 3s7s')
plt.xlabel('Date')
plt.ylabel('Correlation Coeff // %')
plt.title('rolling '+str(window_size)+'d Pearson correl: 3s7s vs 5s')
plt.legend()
plt.show()










