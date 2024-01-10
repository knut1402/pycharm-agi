##### inflation historical + fwd 1y plotting
import matplotlib.pyplot as plt

xt = infl_zc_swap_build('HICPxT', b=0)
rpi = infl_zc_swap_build('UKRPI', b=0)
cpi = infl_zc_swap_build('USCPI', b=0)

### Define start historic dates and length of fwd projection
start_dates = [ql.Date(1,6,2010) + ql.Period(int(i),ql.Months) for i in np.arange(200)]

a1 = [Infl_ZC_Pricer(xt, st_date=start_dates[i], tenor=1, lag = 3, not1 = 10, use_forecast = 0, use_mkt_fixing = 1) for i in np.arange(1,len(start_dates))]
dates1 = [a1[i].base + ql.Period(12,ql.Months) for i in np.arange(len(a1))]
dates2 = [ql_to_datetime(dates1[i]) for i in np.arange(len(a1))]
xt_rates = [a1[i].zc_rate for i in np.arange(len(a1))]

a2 = [Infl_ZC_Pricer(rpi, st_date=start_dates[i], tenor=1, lag = 2, not1 = 10, use_forecast = 0, use_mkt_fixing = 1) for i in np.arange(len(start_dates)-1)]
dates3 = [a2[i].base + ql.Period(12,ql.Months) for i in np.arange(len(a2))]
dates4 = [ql_to_datetime(dates3[i]) for i in np.arange(len(a2))]
rpi_rates = [a2[i].zc_rate for i in np.arange(len(a2))]

a3 = [Infl_ZC_Pricer(cpi, st_date=start_dates[i], tenor=1, lag = 3, not1 = 10, use_forecast = 1, use_mkt_fixing = 0) for i in np.arange(1,len(start_dates))]
dates5 = [a3[i].base + ql.Period(12,ql.Months) for i in np.arange(len(a3))]
dates6 = [ql_to_datetime(dates5[i]) for i in np.arange(len(a3))]
cpi_rates = [a3[i].zc_rate for i in np.arange(len(a3))]

plt.figure(figsize=(10,8))
plt.plot(dates2[0:152], xt_rates[0:152],  c = 'navajowhite')
plt.plot(dates2[151:], xt_rates[151:], label ='EUR HICPxT',  c = 'darkorange')
plt.plot(dates2[0:152], rpi_rates[0:152],   c = 'lightgreen')
plt.plot(dates2[151:], rpi_rates[151:], label = 'UK RPI',   c = 'green')
plt.plot(dates2[0:152], cpi_rates[0:152], c = 'lightsteelblue')
plt.plot(dates2[151:], cpi_rates[151:], label = 'US CPI', c = 'blue')
#plt.axvline(x= ql_to_datetime(ql.Date(1,6,2023)), linewidth = 0.7, c = 'black', linestyle = '--')
plt.axhline(y= 2.0, linewidth = 0.7, c = 'black', linestyle = '--')
plt.axhline(y= 3.0, linewidth = 0.7, c = 'black', linestyle = '--')
plt.scatter(ql_to_datetime(ql.Date(1,11,2023)), 5.3 ,marker='o', s = 12, c = 'green')
plt.scatter(ql_to_datetime(ql.Date(1,11,2023)), 2.4 ,marker='o', s = 12, c = 'darkorange')
plt.scatter(ql_to_datetime(ql.Date(1,11,2023)), 3.1 ,marker='o', s = 12, c = 'blue')
plt.legend()
#plt.grid(visible=True, linestyle='--', linewidth=0.2)
plt.ylabel("%", color="black", fontsize=12)
plt.title('Market Implied Inflation Expectations', c = 'darkblue')
#plt.xticks(rotation = 90)
#plt.xticks(fontsize=7.5)
#plt.yticks(fontsize=7.5)
plt.show()

dates2[151]


####### RPI mkt vs barcap
start_dates = [ql.Date(1,6,2021) + ql.Period(int(i),ql.Months) for i in np.arange(36)]

a4 = [Infl_ZC_Pricer(rpi, st_date=start_dates[i], tenor=1, lag = 2, not1 = 10, use_forecast = 1, use_mkt_fixing = 0) for i in np.arange(len(start_dates)-1)]
dates3 = [a4[i].base + ql.Period(12,ql.Months) for i in np.arange(len(a4))]
dates4 = [ql_to_datetime(dates3[i]) for i in np.arange(len(a4))]
rpi_rates_bcap = [a4[i].zc_rate for i in np.arange(len(a4))]

a2 = [Infl_ZC_Pricer(rpi, st_date=start_dates[i], tenor=1, lag = 2, not1 = 10, use_forecast = 0, use_mkt_fixing = 1) for i in np.arange(len(start_dates)-1)]
dates3 = [a2[i].base + ql.Period(12,ql.Months) for i in np.arange(len(a2))]
dates4 = [ql_to_datetime(dates3[i]) for i in np.arange(len(a2))]
rpi_rates = [a2[i].zc_rate for i in np.arange(len(a2))]



plt.figure(figsize=(10,8))
plt.plot(dates4[0:20], rpi_rates[0:20],   c = 'lightgreen')
plt.plot(dates4[19:], rpi_rates[19:], label = 'UK RPI - Mkt',   c = 'green')
plt.plot(dates4[0:20], rpi_rates_bcap[0:20], c = 'lightsteelblue')
plt.plot(dates4[19:], rpi_rates_bcap[19:], label = 'UK RPI - Barcap', c = 'blue')
#plt.axvline(x= ql_to_datetime(ql.Date(1,6,2023)), linewidth = 0.7, c = 'black', linestyle = '--')
plt.axhline(y= 2.0, linewidth = 0.7, c = 'black', linestyle = '--')
plt.axhline(y= 3.0, linewidth = 0.7, c = 'black', linestyle = '--')
plt.scatter(ql_to_datetime(ql.Date(1,11,2023)), 5.3 ,marker='o', s = 12, c = 'green')
#plt.scatter(ql_to_datetime(ql.Date(1,11,2023)), 2.4 ,marker='o', s = 12, c = 'darkorange')
#plt.scatter(ql_to_datetime(ql.Date(1,11,2023)), 3.1 ,marker='o', s = 12, c = 'blue')
plt.legend()
#plt.grid(visible=True, linestyle='--', linewidth=0.2)
plt.ylabel("%", color="black", fontsize=12)
plt.title('Market Implied Inflation Expectations', c = 'darkblue')
#plt.xticks(rotation = 90)
#plt.xticks(fontsize=7.5)
#plt.yticks(fontsize=7.5)
plt.show()


len(rpi_rates)
dates3[20]









###### Save in dataframe
cpi_df = pd.DataFrame()
cpi_df['date'] = dates2
cpi_df['eur_1y_zc'] = xt_rates
#cpi_df['gbp_dates'] = dates4
cpi_df['gbp_1y_zc'] = rpi_rates
#cpi_df['usd_dates'] = dates6
cpi_df['usd_1y_zc'] = cpi_rates

cpi_df[146:160]

####### Save to excel
cpi_df.to_excel("inflation_yoy_output.xlsx") 

####### Look at current prints / fixings
cpi_df[-85:-60]


###### Plot History + Fwds
plt.plot(dates2, xt_rates, label ='EUR HICPxT', linewidth = 0.75, c = 'blue')
plt.plot(dates2, rpi_rates, label = 'UK RPI',  linewidth = 0.75, c = 'red')
plt.plot(dates2, cpi_rates, label = 'US CPI', c = 'black', linewidth = 0.75)
plt.legend(fontsize = 8)

plt.plot(dates2[-50:], xt_rates[-50:], label ='EUR HICPxT', linewidth = 0.75, c = 'blue')
plt.plot(dates2[-50:], rpi_rates[-50:], label = 'UK RPI',  linewidth = 0.75, c = 'red')
plt.plot(dates2[-50:], cpi_rates[-50:], label = 'US CPI', c = 'black', linewidth = 0.75)
plt.legend(fontsize = 8)
plt.show()

################   changes in enery indices


df_en = con.bdh(['UKRPFUEL Index','UKHPDK9T Index','CPELEMU Index','CPRPENER Index', 'CPELESI Index', 'CPELBEI Index'] , 'PX_LAST', '20170101', '20231130')
df_en2 = pd.DataFrame()

df_en2['UK RPI'] = df_en['UKRPFUEL Index'].pct_change(periods = 12)['PX_LAST'].tolist()[12:]
df_en2['UK CPI'] = df_en['UKHPDK9T Index'].pct_change(periods = 12)['PX_LAST'].tolist()[12:]
df_en2['EZ HICP'] = df_en['CPELEMU Index'].pct_change(periods = 12)['PX_LAST'].tolist()[12:]
df_en2['US CPI'] = df_en['CPRPENER Index'].pct_change(periods = 12)['PX_LAST'].tolist()[12:]
df_en2['Spain HICP'] = df_en['CPELESI Index'].pct_change(periods = 12)['PX_LAST'].tolist()[12:]
df_en2['Belgium HICP'] = df_en['CPELBEI Index'].pct_change(periods = 12)['PX_LAST'].tolist()[12:]

df_en2 = 100*df_en2

plt.plot(df_en.index[12:], df_en2['UK RPI'], label = 'UK RPI - Fuel')
plt.plot(df_en.index[12:], df_en2['UK CPI'], label = 'UK CPI - Energy')
plt.plot(df_en.index[12:], df_en2['EZ HICP'], label = 'EU HICP - Energy')
plt.plot(df_en.index[12:], df_en2['US CPI'], label = 'US CPI - Energy')
plt.plot(df_en.index[12:], df_en2['Spain HICP'], label = 'Spain HICP - Energy')
plt.plot(df_en.index[12:], df_en2['Belgium HICP'], label = 'Belgium  HICP - Energy')
plt.title('Main Energy subcomponents YoY ')
plt.grid(visible=True, linestyle='--', linewidth=0.2)
plt.legend()
plt.show()

len(df_en2['UK RPI'])
df_en[-20:]
df_en2[-20:]


##### plotting drawdown

df_en3 = pd.DataFrame()
df_en3['UK RPI'] = df_en['UKRPFUEL Index']
df_en3['UK CPI'] = df_en['UKHPDK9T Index']
df_en3['EZ HICP'] = df_en['CPELEMU Index']
df_en3['US CPI'] = df_en['CPRPENER Index']
df_en3['Spain HICP'] = df_en['CPELESI Index']
df_en3['Belgium HICP'] = df_en['CPELBEI Index']

df_en4 = pd.DataFrame()

df_en4['UK RPI'] = [ 100*( df_en3['UK RPI'][i] - df_en3['UK RPI'][0:i+1].max() )/ df_en3['UK RPI'][0:i].max() for i in np.arange(len(df_en3))][1:]
df_en4['UK CPI'] = [ 100*( df_en3['UK CPI'][i] - df_en3['UK CPI'][0:i+1].max() )/ df_en3['UK CPI'][0:i].max() for i in np.arange(len(df_en3))][1:]
df_en4['EZ HICP'] = [ 100*( df_en3['EZ HICP'][i] - df_en3['EZ HICP'][0:i+1].max() )/ df_en3['EZ HICP'][0:i].max() for i in np.arange(len(df_en3))][1:]
df_en4['US CPI'] = [ 100*( df_en3['US CPI'][i] - df_en3['US CPI'][0:i+1].max() )/ df_en3['US CPI'][0:i].max() for i in np.arange(len(df_en3))][1:]
df_en4['Spain HICP'] = [ 100*( df_en3['Spain HICP'][i] - df_en3['Spain HICP'][0:i+1].max() )/ df_en3['Spain HICP'][0:i].max() for i in np.arange(len(df_en3))][1:]
df_en4['Belgium HICP'] = [ 100*( df_en3['Belgium HICP'][i] - df_en3['Belgium HICP'][0:i+1].max() )/ df_en3['Belgium HICP'][0:i].max() for i in np.arange(len(df_en3))][1:]

plt.plot(df_en.index[1:], df_en4['UK RPI'], label = 'UK RPI - Fuel')
plt.plot(df_en.index[1:], df_en4['UK CPI'], label = 'UK CPI - Energy')
plt.plot(df_en.index[1:], df_en4['EZ HICP'], label = 'EU HICP - Energy')
plt.plot(df_en.index[1:], df_en4['US CPI'], label = 'US CPI - Energy')
plt.plot(df_en.index[1:], df_en4['Spain HICP'], label = 'Spain HICP - Energy')
plt.plot(df_en.index[1:], df_en4['Belgium HICP'], label = 'Belgium HICP - Energy')
plt.title('Energy subcomponents - Drawdowns')
plt.grid(visible=True, linestyle='--', linewidth=0.2)
plt.legend()
plt.show()




############### plotting index


f3 = con.bdh('FN1 Comdty', 'PX_LAST', '20170101', '20231130', longdata = True)

f3.index = f3['date']
f4 = f3.resample('M').last()
df_en3 = pd.DataFrame()
df_en3['UK RPI'] = df_en['UKRPFUEL Index']
df_en3['UK CPI'] = df_en['UKHPDK9T Index']
df_en3['EZ HICP'] = df_en['CPELEMU Index']
df_en3['US CPI'] = df_en['CPRPENER Index']

df_en3['UK RPI'] = 100*(df_en3['UK RPI'] / df_en3['UK RPI'][0])
df_en3['UK CPI'] = 100*(df_en3['UK CPI'] / df_en3['UK CPI'][0])
df_en3['EZ HICP'] = 100*(df_en3['EZ HICP'] / df_en3['EZ HICP'][0])
df_en3['US CPI'] = 100*(df_en3['US CPI'] / df_en3['US CPI'][0])
df_en3['FN1'] = f4['value'][:-1]

plt.plot(df_en3.index, df_en3['UK RPI'], label = 'UK RPI - Fuel')
plt.plot(df_en3.index, df_en3['UK CPI'], label = 'UK CPI - Energy')
plt.plot(df_en3.index, df_en3['EZ HICP'], label = 'EU HICP - Fuel')
plt.plot(df_en3.index, df_en3['US CPI'], label = 'US CPI - Energy')
plt.plot(df_en3.index, df_en3['FN1'], label = 'Nat Gas')
plt.title('Main Energy subcomponents YoY ')
plt.grid(visible=True, linestyle='--', linewidth=0.2)
plt.legend()
plt.show()



