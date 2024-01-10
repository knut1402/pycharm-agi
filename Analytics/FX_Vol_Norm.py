from scipy.stats import zscore

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




