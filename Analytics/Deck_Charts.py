
latest = '20240131'

### china credit impulse
x1 = con.bdh('CHBGREVO Index' , 'PX_LAST', '20120101', latest, longdata = True)

fig, ax1 = plt.subplots(figsize=(10,8))
ax1.plot(x1['date'],x1['value'], label ='China Credit Impulse')
ax1.axvline(x= ql_to_datetime(ql.Date(31,10,2021)), color = 'black')
ax1.set_ylabel("Index", color="black", fontsize=14)
plt.legend(loc = 'upper left')
plt.title('China Credit Impulse', color = 'darkblue')
plt.annotate('Source: Bloomberg', (0,0), (0,-20), fontsize=6, xycoords='axes fraction', textcoords='offset points', va='top', style='italic')
plt.show()




### cnh basket
x2 = con.bdh('.CNYBASK U Index' , 'PX_LAST', '20120101', latest, longdata = True)

fig, ax1 = plt.subplots(figsize=(10,8))
ax1.plot(x2['date'],x2['value'], label ='CNY Basket')
ax1.axvline(x= ql_to_datetime(ql.Date(31,10,2021)), color = 'black')
ax1.set_ylabel("CNY", color="black", fontsize=14)
plt.legend(loc = 'upper left')
plt.title('CFETS Equivalent CNY Basket', color = 'darkblue')
plt.annotate('Source: Nomura, Bloomberg', (0,0), (0,-20), fontsize=6, xycoords='axes fraction', textcoords='offset points', va='top', style='italic')
plt.show()

#### usd/cnh + vol
x3 = con.bdh('USDCNH Curncy' , 'PX_LAST', '20120101', latest, longdata = True)
x4 = con.bdh('USDCNHV6M Curncy' , 'PX_LAST', '20120101', latest, longdata = True)

fig, ax1 = plt.subplots(2,1,figsize=(10,8),  gridspec_kw={ 'height_ratios':[2,1]})
ax1[0].plot(x3['date'],x3['value'], label ='USD/CNH')
ax1[0].axvline(x= ql_to_datetime(ql.Date(31,10,2021)), color = 'black')
ax1[0].set_ylabel("USD/CNH", color="black", fontsize=14)
ax1[1].plot(x4['date'],x4['value'], label ='6m IV')
ax1[1].axvline(x= ql_to_datetime(ql.Date(31,10,2021)), color = 'black')
ax1[1].set_ylabel("Imp. Vol.", color="black", fontsize=14)
ax1[0].legend(loc = 'upper left')
ax1[1].legend(loc = 'upper left')
ax1[0].set_title('USDCNH and 6m Implied Volatility', color = 'darkblue')
plt.annotate('Source: Bloomberg', (0,0), (0,-20), fontsize=6, xycoords='axes fraction', textcoords='offset points', va='top', style='italic')
plt.show()


#### fed 6th meet
x2 = con.bdh('.FED6 U Index' , 'PX_LAST', '20060101', latest, longdata = True)

fig, ax1 = plt.subplots(figsize=(10,8))
ax1.plot(x2['date'],x2['value'], label ='.FED6')
ax1.axvline(x= ql_to_datetime(ql.Date(4,5,2023)), color = 'black', lw = 0.5)
ax1.axhline(y= 0, color = 'black', lw = 0.5, ls = '-.')
ax1.set_ylabel("bps", color="black", fontsize=14)
#plt.grid(linestyle='--', linewidth=0.3)
plt.legend(loc = 'upper left')
plt.title('Fed Implied Base Rate move to 6th FOMC', color = 'darkblue')
plt.annotate('Source: Bloomberg', (0,0), (0,-20), fontsize=6, xycoords='axes fraction', textcoords='offset points', va='top', style='italic')
plt.show()


#### hy & xover
data = pd.ExcelFile("./DataLake/cds_data.xlsx")
data_df = pd.read_excel(data,"Series")
data_df.columns = ['date', 'cdx_hy', 'itrx_xover']
x6 = con.bdh('USRINDEX Index' , 'PX_LAST', '20040324', latest, longdata = True)

fig, ax1 = plt.subplots(figsize=(10,8))
ax1.plot(data_df['date'],data_df['itrx_xover'], label ='XOVER')
ax1.plot(data_df['date'],data_df['cdx_hy'], label ='CDX HY')
ax1.axvline(x= ql_to_datetime(ql.Date(4,5,2023)), color = 'black', lw = 0.5)
ax1.set_ylabel("bps", color="black", fontsize=14)
ax2 = ax1.twinx()
ax2.plot(x6['date'],x6['value'], color='gray', label ='Recession Ind', lw = 0.5)
#plt.grid(linestyle='--', linewidth=0.3)
ax1.legend(loc = 'upper left')
ax2.legend(loc = 'upper right')
plt.title('CDS Indices', color = 'darkblue')
plt.annotate('Source: Barclays Trading, IHS Markit', (0,0), (0,-20), fontsize=6, xycoords='axes fraction', textcoords='offset points', va='top', style='italic')
plt.show()


#### tips jan 23
x2 = con.bdh('.TIP23S U Index' , 'PX_LAST', '20200228', '20220630', longdata = True)

fig, ax1 = plt.subplots(figsize=(10,8))
ax1.plot(x2['date'],x2['value'], label ='TIPS Jan 23')
ax1.axvline(x= ql_to_datetime(ql.Date(20,7,2021)), color = 'black')
ax1.axvline(x= ql_to_datetime(ql.Date(10,11,2021)), color = 'black')
ax1.set_ylabel("BEI (bps)", color="black", fontsize=14)
plt.legend(loc = 'upper left')
#plt.grid(linestyle='--', linewidth=0.3)
plt.title('TIPS Jan 23 Breakeven', color = 'darkblue')
plt.annotate('Source: Bloomberg', (0,0), (0,-20), fontsize=6, xycoords='axes fraction', textcoords='offset points', va='top', style='italic')
plt.show()


#### aud surprises
x1 = con.bdh('CESIAUD Index', 'PX_LAST', '20200815', '20230315', longdata = True)
x2 = con.bdh('CECIDAUD Index', 'PX_LAST', '20200815', '20230315', longdata = True)

fig, ax1 = plt.subplots(figsize=(10,8))
ax1.plot(x1['date'],x1['value'], label ='AUD Date Surprise')
ax1.plot(x2['date'],x2['value'], label ='AUD Data Change')
ax1.axvline(x= ql_to_datetime(ql.Date(1,11,2021)), color = 'black', lw = 0.5)
ax1.axvline(x= ql_to_datetime(ql.Date(15,2,2022)), color = 'black', lw = 0.5)
ax1.set_ylabel("Index", color="black", fontsize=14)
plt.legend(loc = 'upper right')
#plt.grid(linestyle='--', linewidth=0.3)
plt.title('AUD Data Picking up', color = 'darkblue')
plt.annotate('Source: Citi, Bloomberg', (0,0), (0,-20), fontsize=6, xycoords='axes fraction', textcoords='offset points', va='top', style='italic')
plt.show()


#### 2s5s curves
data = pd.ExcelFile("./DataLake/curve_2s5s.xlsx")
data_df = pd.read_excel(data,"Series")
data_df.columns = ['date', 'usd', 'gbp', 'aud', 'cad']


fig, ax1 = plt.subplots(figsize=(10,8))
ax1.plot(data_df['date'],data_df['usd'], label ='USD')
ax1.plot(data_df['date'],data_df['gbp'], label ='GBP', c= 'lightblue')
ax1.plot(data_df['date'],data_df['cad'], label ='CAD', c= 'lightgreen')
ax1.plot(data_df['date'],data_df['aud'], label ='AUD', c = 'red')
ax1.axvline(x= ql_to_datetime(ql.Date(1,1,2022)), color = 'black', lw = 0.5)
ax1.axvline(x= ql_to_datetime(ql.Date(1,4,2022)), color = 'black', lw = 0.5)
ax1.set_ylabel("bps", color="black", fontsize=14)
ax1.legend(loc = 'upper right')
plt.title('2s5s Curve', color = 'darkblue')
#plt.grid(linestyle='--', linewidth=0.3)
plt.annotate('Source: Barclays Trading, IHS Markit', (0,0), (0,-20), fontsize=6, xycoords='axes fraction', textcoords='offset points', va='top', style='italic')
plt.show()


#### household spending
x1 = con.bdh('USXITORL Index', 'PX_LAST', '20140631', latest, longdata = True)
x2 = con.bdh('USDPCSAM Index', 'PX_LAST', '20140631', latest, longdata = True)

x1['reval'] = 100*x1['value'] / x1['value'][0]
x2['reval'] = 100*x2['value'] / x2['value'][0]


fig, ax1 = plt.subplots(figsize=(10,8))
ax1.plot(x1['date'],x1['reval'], label ='US Real Personal Consumption Expenditure')
ax1.plot(x2['date'],x2['reval'], label ='US Real Personal Disposable Income')
#ax1.axvline(x= ql_to_datetime(ql.Date(1,11,2021)), color = 'black', lw = 0.5)
#ax1.axvline(x= ql_to_datetime(ql.Date(15,2,2022)), color = 'black', lw = 0.5)
ax1.set_ylabel("Re-Indexed in June-2014", color="black", fontsize=10)
plt.legend(loc = 'upper left')
#plt.grid(linestyle='--', linewidth=0.3)
plt.title('US household real PCE and PDI', color = 'darkblue')
plt.annotate('Source: Bloomberg', (0,0), (0,-20), fontsize=6, xycoords='axes fraction', textcoords='offset points', va='top', style='italic')
plt.show()


### consumer confidence
x1 = con.bdh('CONSSENT Index', 'PX_LAST', '20080715', latest, longdata = True)
x2 = con.bdh('CONCCONF Index', 'PX_LAST', '20080715', latest, longdata = True)
x3 = con.bdh('BCOM Index', 'PX_LAST', '20080715', latest, longdata = True)
x4 = con.bdh('EUCCEMU Index', 'PX_LAST', '20080715', latest, longdata = True)
x5 = con.bdh('UKCCI Index', 'PX_LAST', '20080715', latest, longdata = True)

fig, ax1 = plt.subplots(figsize=(10,8))
ax1.plot(x1['date'],x1['value'], label ='UoM Cons Conf')
ax1.plot(x2['date'],x2['value'], label ='Conf Board Cons Conf', c='gold')
ax1.plot(x4['date'],x4['value'], label ='EZ Cons Conf')
ax1.plot(x5['date'],x5['value'], label ='UK GfK Cons Conf')
ax1.set_ylabel("index", color="black", fontsize=10)
ax1.legend(loc = 'upper left')

#ax2 = ax1.twinx()
#ax2.plot(x2['date'],x2['value'], label ='Conf Board Cons Conf (R1)', c = 'blue')
#ax2.legend(loc =  (0.01,0.825))

ax3 = ax1.twinx()
ax3.plot(x3['date'],-x3['value'], label ='BCOM - Inverted (R)', c = 'red')
ax3.legend(loc =  (0.01,0.8))
#ax3.spines['right'].set_position(('axes', 1.06))
ax3.tick_params(colors='red')

ax1.axvline(x= ql_to_datetime(ql.Date(1,9,2022)), color = 'black', lw = 0.8)
ax1.axvline(x= ql_to_datetime(ql.Date(1,9,2023)), color = 'black', lw = 0.8)
#plt.grid(linestyle='--', linewidth=0.3)
plt.title('Consumer Sentiment vs Commodities ', color = 'darkblue')
plt.annotate('Source: UoM, Conference Board, EC, GfK, Bloomberg', (0,0), (0,-20), fontsize=6, xycoords='axes fraction', textcoords='offset points', va='top', style='italic')
plt.show()


### construction spending
x1 = con.bdh('CNSTPRRE Index', 'PX_LAST', '19970727', latest, longdata = True)
x2 = con.bdh('CNSTPRNR Index', 'PX_LAST', '19970727', latest, longdata = True)
x3 = con.bdh('CNSTPRMA Index', 'PX_LAST', '19970727', latest, longdata = True)

x4 = con.bdh('GDP CUR$ Index', 'PX_LAST', '19970727', latest, longdata = True)

x5 = [          0.1*  x1['value'][i]   /          x4['value'][np.argmin(abs(x1['date'][i]-x4['date']))          ] for i in np.arange(len(x1))]
x6 = [          0.1*  x2['value'][i]   /          x4['value'][np.argmin(abs(x2['date'][i]-x4['date']))          ] for i in np.arange(len(x1))]
x7 = [          0.1*  x3['value'][i]   /          x4['value'][np.argmin(abs(x3['date'][i]-x4['date']))          ] for i in np.arange(len(x1))]


fig, ax1 = plt.subplots(figsize=(10,8))
ax1.plot(x1['date'],x1['value'], label ='Private - Residential')
ax1.plot(x2['date'],x2['value']-x3['value'], label ='Private - Non-Residential ex Manufacturing')
ax1.plot(x3['date'],x3['value'], label ='Private - Manufacturing')
#ax1.axvline(x= ql_to_datetime(ql.Date(1,11,2021)), color = 'black', lw = 0.5)
#ax1.axvline(x= ql_to_datetime(ql.Date(15,2,2022)), color = 'black', lw = 0.5)
ax1.set_ylabel("$ (bln)", color="black", fontsize=10)
plt.legend(loc = 'upper left')
#plt.grid(linestyle='--', linewidth=0.3)
plt.title('US Construction Spending', color = 'darkblue')
plt.annotate('Source:US Census Bureau, Bloomberg', (0,0), (0,-20), fontsize=6, xycoords='axes fraction', textcoords='offset points', va='top', style='italic')
plt.show()

#### area % of GDP

fig, ax1 = plt.subplots(figsize=(10,8))
ax1.plot(x1['date'],(x5), label ='Private - Residential')
ax1.plot(x2['date'],x6, label ='Private - Non-Residential ex Manufacturing')
ax1.plot(x3['date'],x7, label ='Private - Manufacturing')
#ax1.axvline(x= ql_to_datetime(ql.Date(1,11,2021)), color = 'black', lw = 0.5)
#ax1.axvline(x= ql_to_datetime(ql.Date(15,2,2022)), color = 'black', lw = 0.5)
ax1.set_ylabel("% GDP", color="black", fontsize=10)
plt.legend(loc = 'upper left')
#plt.grid(linestyle='--', linewidth=0.3)
plt.title('US Construction Spending', color = 'darkblue')
plt.annotate('Source:US Census Bureau, Bloomberg', (0,0), (0,-20), fontsize=6, xycoords='axes fraction', textcoords='offset points', va='top', style='italic')
plt.show()









#### yield rolling average
x1 = con.bdh('FDTR Index', 'PX_LAST', '19860131', latest, longdata = True)
x2 = con.bdh('GT10 Govt', 'PX_LAST', '19860131', latest, longdata = True)
x3 = con.bdh('GT2 Govt', 'PX_LAST', '19860131', latest, longdata = True)
x4 = con.bdh('BICLB10Y Index', 'PX_LAST', '19860131', latest, longdata = True)

x5 = pd.merge(x2, x4,  how='left', left_on='date', right_on = 'date')
x6 = x5.dropna()
x6['all_in'] = x6['value_x'] + 0.01*x6['value_y']
x7 = con.bdh('USRINDEX Index' , 'PX_LAST', '19860131', latest, longdata = True)


fig, ax1 = plt.subplots(figsize=(10,8))
ax1.plot(x2['date'],x2['value'].rolling(500).mean(), label ='UST 10Y', zorder=10)
ax1.plot(x3['date'],x3['value'].rolling(500).mean(), label ='UST 2Y', zorder=7)
ax1.plot(x6['date'],x6['all_in'].rolling(500).mean(), label ='US Corp BAA 10Y',zorder=8)
ax1.plot(x1['date'],x1['value'], label ='Fed Base Rate', c = 'black',zorder=9)
ax1.legend(loc = 'upper right')
ax1.set_ylabel("Yield (%)", color="black", fontsize=10)

ax2 = ax1.twinx()
ax2.plot(x7['date'],x7['value'], color='gray', label ='Recession Ind', lw = 0.5)
#ax1.fill_between(x7['date'],x7['value'], interpolate=True, color='lightgray', zorder=0)
ax2.legend(loc = 'lower left')
#plt.grid(linestyle='--', linewidth=0.3)
plt.title('Usnig 2y Moving Averages to factor in lags', color = 'darkblue')
plt.annotate('Source:Bloomberg', (0,0), (0,-20), fontsize=6, xycoords='axes fraction', textcoords='offset points', va='top', style='italic')
plt.show()



### leading indicators
x1 = con.bdh('NAPMPMI Index', 'PX_LAST', '20170601', latest, longdata = True)
x2 = con.bdh('MPMIEZMA Index', 'PX_LAST', '20170601', latest, longdata = True)
x3 = con.bdh('NAPMNEWO Index', 'PX_LAST', '20170601', latest, longdata = True)
x4 = con.bdh('GEIFOMEX Index', 'PX_LAST', '20170601', latest, longdata = True)
x5 = con.bdh('CHBGREVO Index', 'PX_LAST', '20170601', latest, longdata = True)
x6 = con.bdh('TWEOTTLY Index', 'PX_LAST', '20170601', latest, longdata = True)
x7 = con.bdh('PMISSURV Index', 'PX_LAST', '20170601', latest, longdata = True)


fig, ax1 = plt.subplots(figsize=(10,8))
ax1.plot(x1['date'],x1['value'], label ='US ISM Mfg', c = 'blue')
ax1.plot(x2['date'],x2['value'], label ='EZ Mfg PMI', c = 'forestgreen')
ax1.plot(x3['date'],x3['value'], label ='US ISM Mfg New Orders', c= 'gold')
ax1.plot(x4['date'],x4['value']+50.0, color='crimson', label ='German IFO Export Expectations')
ax1.plot(x7['date'],x7['value'], label ='Sweden Mfg PMI', c= 'lightgreen')
ax1.set_ylim(25, 80)
ax1.axhline(y= 50.0, color = 'black', lw = 0.5)
ax1.legend(loc = 'lower left')
ax1.set_ylabel("Index", color="black", fontsize=10)

ax1.set_title('Leading Indicators', color = 'darkblue')
plt.annotate('Source:Bloomberg', (0,0), (0,-20), fontsize=6, xycoords='axes fraction', textcoords='offset points', va='top', style='italic')
plt.show()



fig, ax1 = plt.subplots(figsize=(10,8))
ax1.plot(x5['date'],x5['value'], color='brown', label ='China Credit Impulse')
ax1.legend(loc =  "upper left")
ax2 = ax1.twinx()
ax2.plot(x6['date'],x6['value'], color='deeppink', label ='Taiwan Export Orders YoY (R)')
ax2.legend(loc =  (0.01,0.9))
ax2.tick_params(colors='deeppink')
ax2.set_ylabel("%", color="deeppink", fontsize=10)
ax1.set_title('Leading Indicators', color = 'darkblue')
plt.annotate('Source:Bloomberg', (0,0), (0,-20), fontsize=6, xycoords='axes fraction', textcoords='offset points', va='top', style='italic')
plt.show()



fig, ax1 = plt.subplots(1,2,figsize=(10,4))
ax1[0].plot(x1['date'],x1['value'], label ='US ISM Mfg', c = 'blue')
ax1[0].plot(x2['date'],x2['value'], label ='EZ Mfg PMI', c = 'forestgreen')
ax1[0].plot(x3['date'],x3['value'], label ='US ISM Mfg New Orders', c= 'gold')
ax1[0].plot(x4['date'],x4['value']+50.0, color='crimson', label ='German IFO Export Expectations')
ax1[0].plot(x7['date'],x7['value'], label ='Sweden Mfg PMI', c= 'lightgreen')
ax1[0].set_ylim(25, 80)
ax1[0].axhline(y= 50.0, color = 'black', lw = 0.5)
ax1[0].legend(loc = 'lower left')
ax1[0].set_ylabel("Index", color="black", fontsize=10)

ax1[1].plot(x5['date'],x5['value'], color='brown', label ='China Credit Impulse')
ax1[1].legend(loc =  (0.01,0.85))
ax2 = ax1[1].twinx()
ax2.plot(x6['date'],x6['value'], color='deeppink', label ='Taiwan Export Orders YoY (R)')
ax2.legend(loc =  (0.01,0.725))
ax2.tick_params(colors='deeppink')
ax2.set_ylabel("%", color="deeppink", fontsize=10)

#plt.grid(linestyle='--', linewidth=0.3)
ax1[0].set_title('Leading Indicators', color = 'darkblue')
plt.annotate('Source:Bloomberg', (0,0), (0,-20), fontsize=6, xycoords='axes fraction', textcoords='offset points', va='top', style='italic')
plt.show()




#### retail sales

x3 = con.bdh('GRFRIAYY Index' , 'PX_LAST', '20170601', latest, longdata = True)
x4 = con.bdh('RSWAEMUY Index' , 'PX_LAST', '20170601', latest, longdata = True)
x5 = con.bdh('REDSWYOY Index' , 'PX_LAST', '20010101', latest, longdata = True)
x6 = con.bdh('DTSRR1RB Index' , 'PX_LAST', '20170601', latest, longdata = True)

fig, ax1 = plt.subplots(2,1,figsize=(10,8),  gridspec_kw={ 'height_ratios':[2,1]})
ax1[0].plot(x5['date'],x5['value'], label ='US Weekly Retail Sales YoY')
ax1[0].axhline(y= 0.0, color = 'black', lw = 0.5)
ax1[0].set_ylabel("%", color="black", fontsize=10)
ax1[1].plot(x3['date'],x3['value'], label ='German Real Retail Sales', c='orange')
ax1[1].plot(x4['date'],x4['value'], label ='EZ Retail Sales Volume', c= 'blue')
ax2 = ax1[1].twinx()
ax2.plot(x6['date'],x6['value'], label ='UK CBI Reported Sales', c= 'limegreen')
ax2.legend(loc = 'lower right')
ax2.tick_params(colors='limegreen')

ax1[1].axhline(y= 0.0, color = 'black', lw = 0.5)
ax1[1].set_ylabel("%", color="black", fontsize=10)
ax1[0].legend(loc = 'upper left')
ax1[1].legend(loc = 'upper left')
ax1[0].set_title('Retail Sales', color = 'darkblue')
#ax1[0].grid(linestyle='--', linewidth=0.3)
#ax1[1].grid(linestyle='--', linewidth=0.3)
plt.annotate('Source:CBI, Johnson Redbook, Bloomberg', (0,0), (0,-20), fontsize=6, xycoords='axes fraction', textcoords='offset points', va='top', style='italic')
plt.show()




##### credit stds / spreads

x1 = con.bdh('SL% SMT% Index' , 'PX_LAST', '19940101', latest, longdata = True)
x2 = con.bdh('LF98OAS Index' , 'PX_LAST', '19940101', latest, longdata = True)
x3 = con.bdh('EBLS11NC Index' , 'PX_LAST', '20060101', latest, longdata = True)


data = pd.ExcelFile("./DataLake/cds_data.xlsx")
data_df = pd.read_excel(data,"Series")
data_df.columns = ['date', 'cdx_hy', 'itrx_xover']


fig, ax1 = plt.subplots(2,1,figsize=(10,8),  gridspec_kw={ 'height_ratios':[1,1]})
ax1[0].plot(x1['date'],x1['value'], label ='SLOOS - Some tightening')
ax2 = ax1[0].twinx()
ax2.plot(x2['date'],x2['value'], color='darkorange', label ='US Corp HY OAS')
ax2.legend(loc = (0.01,0.8))
ax2.tick_params(colors='darkorange')
ax1[0].set_ylabel("%", color="black", fontsize=10)

ax1[1].plot(x3['date'],x3['value'], label ='ECB BLS - Change in credit stds last 3m')
ax3 = ax1[1].twinx()
ax3.plot(data_df['date'],data_df['itrx_xover'], label ='ITRX XOVER', c= 'orangered')
ax3.legend(loc = (0.82,0.8))
ax3.tick_params(colors='orangered')

ax1[1].set_ylabel("% / bps", color="black", fontsize=10)
ax1[0].legend(loc = 'upper left')
ax1[1].legend(loc = 'upper right')
ax1[0].set_title('Credit Standards vs Spreads', color = 'darkblue')
#ax1[0].grid(linestyle='--', linewidth=0.3)
#ax1[1].grid(linestyle='--', linewidth=0.3)
plt.annotate('Source:Fed, ECB, Bloomberg', (0,0), (0,-20), fontsize=6, xycoords='axes fraction', textcoords='offset points', va='top', style='italic')
plt.show()



##### sloos
data = pd.ExcelFile("./DataLake/sloos2.xlsx")
data_df = pd.read_excel(data,"Series")
data_df.columns = ['date', 'sloos', 'loans']

x6 = con.bdh('USRINDEX Index' , 'PX_LAST', '20040324', latest, longdata = True)


fig, ax1 = plt.subplots(figsize=(10,8))
ax1.plot(data_df['date'][182:],-data_df['sloos'][182:], label ='SLOOS Tightening Stds 12m Lead - Inverted (L)')
ax1.set_ylabel("%", color="black", fontsize=12)
ax2 = ax1.twinx()
ax2.plot(data_df['date'][182:],data_df['loans'][182:], label ='C&I Loans YoY (Y)', c='darkorange')
ax2.tick_params(colors='darkorange')
#ax1.grid(linestyle='--', linewidth=0.3)
ax1.legend(loc = 'lower left')
ax2.legend(loc = (0.01,0.05))
plt.title('SLOOS vs C&I Loan Growth', color = 'darkblue')
plt.annotate('Source: Fed', (0,0), (0,-20), fontsize=6, xycoords='axes fraction', textcoords='offset points', va='top', style='italic')
plt.show()


##### risk premia
data = pd.ExcelFile("./DataLake/risk_premia.xlsx")
data_df = pd.read_excel(data,"Series")
data_df.columns = ['date', 'vix', 'jpm_fx','move','baa_oas','pmi']

x6 = con.bdh('USRINDEX Index' , 'PX_LAST', '20040324', latest, longdata = True)

fig, ax1 = plt.subplots(figsize=(10,8))
ax1.plot(data_df['date'],data_df['vix'], label ='VIX', c='indianred')
ax1.plot(data_df['date'],data_df['move'], label ='MOVE', c='cornflowerblue')
ax1.plot(data_df['date'],data_df['jpm_fx'], label ='JPM FX Vol Index', c='lightgreen')
ax1.plot(data_df['date'],data_df['baa_oas'], label ='US Corp BAA 10Y Spread', c='gold')
ax1.set_ylabel("z-score", color="black", fontsize=12)
ax1.grid(linestyle='--', linewidth=0.3)
ax1.axhline(y= 0.0, color = 'black', lw = 0.5, ls = '-.')
ax2 = ax1.twinx()
ax2.plot(data_df['date'],50-data_df['pmi'], label ='Global Mfg PMI - Inverted (R)', c='black')
ax2.set_yticks(ticks = [-10, -5, 0,5, 10, 15], labels = ['60','55','50', '45', '40', '35'])
ax2.tick_params(colors='black')
ax1.legend(loc = 'upper left')
ax2.legend(loc = (0.01,0.8))
ax1.set_title('Risk Premia vs Activity', color = 'darkblue')
plt.annotate('Source: Bloomberg', (0,0), (0,-20), fontsize=6, xycoords='axes fraction', textcoords='offset points', va='top', style='italic')
plt.show()


######## linker supply

data = pd.ExcelFile("./DataLake/linker_supply.xlsx")
data_df = pd.read_excel(data,"Series")
data_df.columns = ['date', 'linker']

data_df['year'] = [int(data_df['date'][i]) for i in np.arange(len(data_df))]

fig, ax1 = plt.subplots(figsize=(10,8))
ax1.bar(data_df['year'],data_df['linker'], label ='Gross UKTi Supply (mm)', width = 0.6)
ax1.set_ylabel("£ mm", color="black", fontsize=12)
ax1.set_xticks(ticks = [2005,2006,2007,2008,2009,2010,2011,2012,2013,2014,2015,2016,2017,2018,2019,2020,2021,2022,2023]
               , labels = ['2005','2006','2007','2008','2009','2010','2011','2012','2013','2014','2015','2016','2017','2018','2019','2020','2021','2022','2023']
               , rotation = 90)
plt.title('UK Linker Supply', color = 'darkblue')
plt.annotate('Source: UK DMO', (0,0), (0,-50), fontsize=6, xycoords='axes fraction', textcoords='offset points', va='top', style='italic')
plt.show()


#### 5y5y inflation
x1 = con.bdh('FWISEU55 Index' , 'PX_LAST', '20050601', latest, longdata = True)
x2 = con.bdh('FWISUS55 Index' , 'PX_LAST', '20050601', latest, longdata = True)
x3 = con.bdh('FWISBP55 Index' , 'PX_LAST', '20050601', latest, longdata = True)

fig, ax1 = plt.subplots(figsize=(10,8))
ax1.plot(x1['date'][::10],x1['value'][::10], label ='HICPxT', c='darkred')
ax1.plot(x2['date'][::10],x2['value'][::10], label ='USCPI', c='steelblue')
ax1.plot(x3['date'][::10],x3['value'][::10]-1.0, label ='UKCPI - assuming a 1% wedge', c='forestgreen')
ax1.axvline(x= ql_to_datetime(ql.Date(1,6,2021)), color = 'black', lw = 0.6)
ax1.axhline(y= 2.0, color = 'black', lw = 0.4, ls='-.')
ax1.set_ylabel("% / bps", color="black", fontsize=10)
ax1.legend(loc = 'upper left')
ax1.set_title('Mkt implied 5y5y inflation expectations', color = 'darkblue')
#ax1.grid(linestyle='--', linewidth=0.3)
plt.annotate('Source: Bloomberg', (0,0), (0,-20), fontsize=6, xycoords='axes fraction', textcoords='offset points', va='top', style='italic')
plt.show()


#### 5y5y inflation
x1 = con.bdh('FWISEU55 Index' , 'PX_LAST', '20050601', latest, longdata = True)
x2 = con.bdh('FWISUS55 Index' , 'PX_LAST', '20050601', latest, longdata = True)
x3 = con.bdh('FWISBP55 Index' , 'PX_LAST', '20050601', latest, longdata = True)

fig, ax1 = plt.subplots(figsize=(10,8))
ax1.plot(x1['date'][::10],x1['value'][::10], label ='HICPxT', c='darkred')
ax1.plot(x2['date'][::10],x2['value'][::10], label ='USCPI', c='steelblue')
ax1.plot(x3['date'][::10],x3['value'][::10]-1.0, label ='UKCPI - assuming a 1% wedge', c='forestgreen')
ax1.axvline(x= ql_to_datetime(ql.Date(1,6,2021)), color = 'black', lw = 0.6)
ax1.axhline(y= 2.0, color = 'black', lw = 0.4, ls='-.')
ax1.set_ylabel("% / bps", color="black", fontsize=10)
ax1.legend(loc = 'upper left')
ax1.set_title('Mkt implied 5y5y inflation expectations', color = 'darkblue')
#ax1.grid(linestyle='--', linewidth=0.3)
plt.annotate('Source: Bloomberg', (0,0), (0,-20), fontsize=6, xycoords='axes fraction', textcoords='offset points', va='top', style='italic')
plt.show()

#### gas
x1 = con.bdh('FN1 Comdty' , 'PX_LAST', '20190101', latest, longdata = True)

fig, ax1 = plt.subplots(figsize=(10,8))
ax1.plot(x1['date'][::10],x1['value'][::10], label ='FN1', c='blue')
ax1.axvline(x= ql_to_datetime(ql.Date(1,9,2021)), color = 'black', lw = 0.6)
ax1.axvline(x= ql_to_datetime(ql.Date(1,3,2022)), color = 'black', lw = 0.6)
ax1.set_ylabel("£ / therm", color="black", fontsize=10)
ax1.legend(loc = 'upper left')
ax1.set_title('UK Natural Gas Futures', color = 'darkblue')
#ax1.grid(linestyle='--', linewidth=0.3)
plt.annotate('Source: Bloomberg', (0,0), (0,-20), fontsize=6, xycoords='axes fraction', textcoords='offset points', va='top', style='italic')
plt.show()



######## eu lending

data = pd.ExcelFile("./DataLake/eu_loans.xlsx")
data_df = pd.read_excel(data,"Series")
data_df.columns = ['date', 'period', 'corp', 'hh', 'govt']

fig, ax1 = plt.subplots(3,1,figsize=(10,8))
ax1[0].bar(data_df['period'],data_df['hh'], label ='Households', width = 0.6, color= ['blue']*len(data_df))
ax1[1].bar(data_df['period'],data_df['corp'], label ='Non-Fiancial Corporations', width = 0.6, color= ['gold']*len(data_df))
ax1[2].bar(data_df['period'],data_df['govt'], label ='Government', width = 0.6, color= ['red']*len(data_df))

ax1[0].legend(loc = 'upper left')
ax1[1].legend(loc = 'upper left')
ax1[2].legend(loc = 'upper left')
ax1[0].set_xticks(ticks = data_df['period'], labels = [""]*len(data_df), rotation = 90)
ax1[1].set_xticks(ticks = data_df['period'], labels = [""]*len(data_df), rotation = 90)
ax1[0].set_ylabel("EUR bln", color="black", fontsize=12)
ax1[1].set_ylabel("EUR bln", color="black", fontsize=12)
ax1[2].set_ylabel("EUR bln", color="black", fontsize=12)
ax1[2].set_xticks(ticks = data_df['period'], labels = list(data_df['period']), rotation = 90)
ax1[0].set_title('EU Lending - H1', color = 'darkblue')
plt.annotate('Source: ECB', (0,0), (0,-57), fontsize=6, xycoords='axes fraction', textcoords='offset points', va='top', style='italic')
plt.show()


#### JPM survey
x1 = con.bdh('TINSALNL Index' , 'PX_LAST', '20050101', latest, longdata = True)

fig, ax1 = plt.subplots(figsize=(10,8))
ax1.plot(x1['date'][::10],x1['value'][::10], label ='JPM All Investors Net Long', c='steelblue')
ax1.axhline(y= 0.0, color = 'black', lw = 0.4, ls='-.')
ax1.set_ylabel("%", color="black", fontsize=10)
ax1.legend(loc = 'lower right')
ax1.set_title('JPM Treasury Client Survey: All Investors: Net Long', color = 'darkblue')
plt.annotate('Source: JPM, Bloomberg', (0,0), (0,-20), fontsize=6, xycoords='axes fraction', textcoords='offset points', va='top', style='italic')
plt.show()


##### US Average Hourly Earnings
x1 = con.bdh('AHE TOTL Index' , 'PX_LAST', '20000101', latest, longdata = True)
x2 = con.bdh('CSXHSPCY Index' , 'PX_LAST', '20000101', latest, longdata = True)

x1['ahe_3m_ann'] = 400*x1['value'].pct_change(periods=3)

fig, ax1 = plt.subplots(figsize=(10,8))
ax1.plot(x1['date'],x1['ahe_3m_ann'], label ='AHE 3m Ann SA.: 4.8%', c='dodgerblue')
ax1.plot(x2['date']- datetime.timedelta(days=180),x2['value'], label ='CPI Supercore YoY - 6m Lag', c='red')
ax1.axhline(y= 3.5, color = 'black', lw = 0.4, ls='-.')
ax1.set_ylabel("%", color="black", fontsize=10)
ax1.set_ylim(0, 7.5)
ax1.legend(loc = 'upper left')
ax1.set_title('US AHE', color = 'darkblue')
plt.annotate('Source: JPM, Bloomberg', (0,0), (0,-20), fontsize=6, xycoords='axes fraction', textcoords='offset points', va='top', style='italic')
plt.show()







##### US HealthCare insurance
x1 = con.bdh('CPRMHEUS Index' , 'PX_LAST', '20000101', latest, longdata = True)

x1['hei_3m_ann'] = 400*x1['value'].pct_change(periods=3)
x1['hei_ann'] = 100*x1['value'].pct_change(periods=12)
x1['hei_mom'] = 100*x1['value'].pct_change(periods=1)

fig, ax1 = plt.subplots(figsize=(10,8))
ax1.plot(x1['date'],x1['hei_ann'], label ='US CPI: HealthCare Insurance YoY: -29.5%', c='dodgerblue')
ax1.bar(x1['date'],x1['hei_mom'], label ='US CPI: HealthCare Insurance MoM: -4%', width = 60)
ax1.plot(x2['date'],x2['value'], label ='CPI Supercore YoY', c='red')
#ax1.axhline(y= 3.5, color = 'black', lw = 0.4, ls='-.')
ax1.set_ylabel("%", color="black", fontsize=10)
ax1.set_ylim(-30, 30)
ax1.legend(loc = 'upper left')
ax1.set_title('US HealthCare PCI', color = 'darkblue')
plt.annotate('Source: JPM, Bloomberg', (0,0), (0,-20), fontsize=6, xycoords='axes fraction', textcoords='offset points', va='top', style='italic')
plt.show()








































fig, ax1 = plt.subplots(figsize=(10,8))
ax1.plot(o4['date'],o4['value'], label ='Oct23 RPI')
ax1.set_ylabel("RPI", color="blue", fontsize=14)
plt.legend(loc = 'upper left')
ax2 = ax1.twinx()
ax2.plot(f3['date'],f3['value'], color='red', label ='FNV3')
ax2.set_ylabel("FN", color="red", fontsize=14)
plt.legend()
plt.title('Gas prices imply downside risk to fixings in H2', color = 'Green')
plt.show()
