import numpy as np
import pandas as pd
from scipy.stats import zscore
from Utilities import *
## BBG API
con = pdblp.BCon(debug=False, port=8194, timeout=50000)
con.start()


start = '20160101'
latest = '20240102'
tenor = '1Y'


eurusd = con.bdh('EURUSDV'+tenor+' BGN Curncy' , 'PX_LAST', start, latest, longdata = True)
eurusd['v_zscore'] = zscore(eurusd['value'])
gbpusd = con.bdh('GBPUSDV'+tenor+' BGN Curncy' , 'PX_LAST', start, latest, longdata = True)
gbpusd['v_zscore'] = zscore(gbpusd['value'])
usdjpy = con.bdh('USDJPYV'+tenor+' BGN Curncy' , 'PX_LAST', start, latest, longdata = True)
usdjpy['v_zscore'] = zscore(usdjpy['value'])
usdcad = con.bdh('USDCADV'+tenor+' BGN Curncy' , 'PX_LAST', start, latest, longdata = True)
usdcad['v_zscore'] = zscore(usdcad['value'])
audusd = con.bdh('AUDUSDV'+tenor+' BGN Curncy' , 'PX_LAST', start, latest, longdata = True)
audusd['v_zscore'] = zscore(audusd['value'])
usdchf = con.bdh('USDCHFV'+tenor+' BGN Curncy' , 'PX_LAST', start, latest, longdata = True)
usdchf['v_zscore'] = zscore(usdchf['value'])
usdsek = con.bdh('USDSEKV'+tenor+' BGN Curncy' , 'PX_LAST', start, latest, longdata = True)
usdsek['v_zscore'] = zscore(usdsek['value'])
usdcnh = con.bdh('USDCNHV'+tenor+' BGN Curncy' , 'PX_LAST', start, latest, longdata = True)
usdcnh['v_zscore'] = zscore(usdcnh['value'])

usdmxn = con.bdh('USDMXNV'+tenor+' BGN Curncy' , 'PX_LAST', start, latest, longdata = True)
usdmxn['v_zscore'] = zscore(usdmxn['value'])
usdbrl = con.bdh('USDBRLV'+tenor+' BGN Curncy' , 'PX_LAST', start, latest, longdata = True)
usdbrl['v_zscore'] = zscore(usdbrl['value'])
usdphp = con.bdh('USDPHPV'+tenor+' BGN Curncy' , 'PX_LAST', start, latest, longdata = True)
usdphp['v_zscore'] = zscore(usdphp['value'])
usdzar = con.bdh('USDZARV'+tenor+' BGN Curncy' , 'PX_LAST', start, latest, longdata = True)
usdzar['v_zscore'] = zscore(usdzar['value'])
usdkrw = con.bdh('USDKRWV'+tenor+' BGN Curncy' , 'PX_LAST', start, latest, longdata = True)
usdkrw['v_zscore'] = zscore(usdkrw['value'])




fig, ax1 =  plt.subplots(2,2,figsize=(20,16))
ax1[0,0].plot(eurusd['date'],eurusd['v_zscore'], label ='EURUSD')
ax1[0,0].plot(gbpusd['date'],gbpusd['v_zscore'], label ='GBPUSD')
ax1[0,0].plot(usdjpy['date'],usdjpy['v_zscore'], label ='USDJPY')
ax1[0,1].plot(usdcad['date'],usdcad['v_zscore'], label ='USDCAD')
ax1[0,1].plot(audusd['date'],audusd['v_zscore'], label ='AUDUSD')
ax1[0,1].plot(usdchf['date'],usdchf['v_zscore'], label ='USDCHF')
ax1[0,1].plot(usdsek['date'],usdsek['v_zscore'], label ='USDSEK')
ax1[0,0].plot(usdcnh['date'],usdcnh['v_zscore'], label ='USDCNH')
ax1[1,0].plot(usdmxn['date'],usdmxn['v_zscore'], label ='USDMXN')
ax1[1,0].plot(usdbrl['date'],usdbrl['v_zscore'], label ='USDBRL')
ax1[1,1].plot(usdphp['date'],usdphp['v_zscore'], label ='USDPHP')
ax1[1,0].plot(usdzar['date'],usdzar['v_zscore'], label ='USDZAR')
ax1[1,1].plot(usdkrw['date'],usdkrw['v_zscore'], label ='USDKRW')
#ax1.axvline(x= ql_to_datetime(ql.Date(4,5,2023)), color = 'black', lw = 0.5)
ax1[0,0].set_ylabel("z-score", color="black", fontsize=14)
#plt.grid(linestyle='--', linewidth=0.3)
ax1[0,0].legend(loc = 'upper right')
ax1[0,1].legend(loc = 'upper right')
ax1[1,0].legend(loc = 'upper right')
ax1[1,1].legend(loc = 'upper right')
ax1[0,0].set_title('USD 1y Implied', color = 'darkblue')
plt.show()


###### fx flies vs realised
start = '20061201'
latest = '20240319'

today = ql.Date(datetime.datetime.now().day, datetime.datetime.now().month, datetime.datetime.now().year)
c = ccy('SOFR_DC', today)

pair = ['EURUSD', 'GBPUSD', 'USDJPY']#, 'USDCAD', 'AUDUSD', 'USDCHF', 'USDSEK', 'USDNOK', 'NZDUSD', 'USDBRL', 'USDMXN', 'USDZAR', 'EURCHF','EURHUF', 'EURPLN' ]
tenor = '6M'
real_tenor = '3M'
bfl_delta = 10

implied_pre = []
implied_pre_data = dict([(key, []) for key in pair])
realised_post = []
realised_data = dict([(key, []) for key in pair])
implied_post = []
implied_data = dict([(key, []) for key in pair])
bfly_pre = []
bfly_post = []

for j in np.arange(len(pair)):
    print(pair[j])
    j=1
    impl_v_ticker = pair[j]+'V'+tenor+' Curncy'
    bfly_ticker = pair[j]+str(bfl_delta)+'B'+tenor+' Curncy'
    real_v_ticker = pair[j]+'H'+real_tenor+' Curncy'

    bflv = con.bdh([bfly_ticker] , 'PX_LAST', start, latest, longdata = True)
    implv = con.bdh([impl_v_ticker] , 'PX_LAST', start, latest, longdata = True)
    realv = con.bdh([real_v_ticker] , 'PX_LAST', start, latest, longdata = True)

    start = max(bflv['date'][0],implv['date'][0],realv['date'][0]).strftime('%Y%m%d')
    start2 = ql.Date(int(start[6:8]),int(start[4:6]),int(start[:4]))
    bflv['date'] = [datetime_to_ql(bflv['date'][i]) for i in np.arange(len(bflv))]
    implv['date'] = [datetime_to_ql(implv['date'][i]) for i in np.arange(len(implv))]
    realv['date'] = [datetime_to_ql(realv['date'][i]) for i in np.arange(len(realv))]

    bflv = bflv[bflv['date'] >= start2 ]
    implv = implv[implv['date'] >= start2]
    realv = realv[realv['date'] >= start2]
    quantiles = bflv.quantile([.2, .4, 0.6, 0.8])

    for i in np.arange(len(quantiles)+1):
        print(i)
        i=0
        if i == 0:
            con1 = bflv[bflv['value'] < quantiles.iloc[0].value]['date'].tolist()
        elif i == len(quantiles):
            con1 = bflv[bflv['value'] > quantiles.iloc[-1].value]['date'].tolist()
        else:
            con1 = bflv[ (bflv['value'] < quantiles.iloc[i].value) & (bflv['value'] > quantiles.iloc[i-1].value)  ]['date'].tolist()

        con2 = [con1[i] + ql.Period(real_tenor) for i in np.arange(len(con1))]
        con3 = [con2[i] for i in np.arange(len(con2)) if con2[i] < today]

        implied_pre.append(implv[implv['date'].isin(con1)]['value'].mean())
        implied_pre_data[pair[j]].append(implv[implv['date'].isin(con1)]['value'].tolist())
        bfly_pre.append(bflv[bflv['date'].isin(con1)]['value'].mean())

        realised_post.append(realv[realv['date'].isin(con3)]['value'].mean())
        realised_data[pair[j]].append(realv[realv['date'].isin(con3)]['value'].tolist())

        implied_post.append(implv[implv['date'].isin(con3)]['value'].mean())
        implied_data[pair[j]].append(implv[implv['date'].isin(con3)]['value'].tolist())

        bfly_post.append(bflv[bflv['date'].isin(con3)]['value'].mean())


len(realised_data['EURUSD'][0])
len(implied_pre_data['EURUSD'][0])
len(implied_data['EURUSD'][0])

df = pd.DataFrame()
df['pair'] = flat_lst([[pair[i]]*5 for i in np.arange(len(pair))])
df['implied_tenor'] = [tenor]*len(realised_post)
df['realised_tenor'] = [real_tenor]*len(realised_post)
df['quantile'] = [1,2,3,4,5]*len(pair)
#df['q_value'] = ['<' + str(quantiles['value'].tolist()[0])]+ quantiles['value'].tolist()[1:]+['>' + str(quantiles['value'].tolist()[-1])]
df['impl_pre'] = implied_pre
df['impl_post'] = implied_post
df['imp_chg'] = np.array(implied_post) - np.array(implied_pre)
df['bfl_pre'] = bfly_pre
df['bfl_post'] = bfly_post
df['bfl_chg'] = np.array(bfly_post) - np.array(bfly_pre)
df['real'] = realised_post
df['value'] = np.array(realised_post) - np.array(implied_pre)

df.round(3)

df1 = df[(df['quantile'] == 1) | (df['quantile'] == 5)]

plt.scatter(df1['bfl_pre'],df1['value'], c = df1['quantile'], s=20)
plt.xlabel('FX Vol Convexity - mean by quantiles')
plt.ylabel('Realised - Implied (pre)')
plt.show()

plt.scatter(df['bfl_pre'],df['value'], c = df['quantile'], s=20)
plt.xlabel('FX Vol Convexity - mean by quantiles')
plt.ylabel('Realised - Implied (pre)')
plt.show()


implv['date'][0] == realv['date'][0]

bflv['date'][0]

















