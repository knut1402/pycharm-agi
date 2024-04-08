##### RPI constant month plotting
import pandas as pd

latest = '20240131'    ##### get data up to this date - bbg format

#### RPI: Mar25
o1 = con.bdh('.RPI0325 U Index' , 'PX_LAST', '20220420', latest, longdata = True)
o2 = con.bdh('BPSWIF3 INFA Index' , 'PX_LAST', '20230420', latest, longdata = True)
f3 = con.bdh('FNZ3 Comdty', 'PX_LAST', '20220420', latest, longdata = True)
o2['value'] = o2['value']/100
o3 = o1[o1['date'] < '2023-04-20']
o4 = pd.concat([o3,o2])
o4 = o4.reset_index(drop=True)
o5 = o1[o1['date'] > '2023-04-20']


x1 = con.bdh('.XT0525 U Index' , 'PX_LAST', '20220420', latest, longdata = True)
x2 = con.bdh('EUSWIF3 INFA Index' , 'PX_LAST', '20230420', latest, longdata = True)
x2['value'] = x2['value']/100
x3 = x1[x1['date'] < '2023-04-20']
x4 = pd.concat([x3,x2])
x4 = x4.reset_index(drop=True)


fig, ax1 = plt.subplots(figsize=(10,8))
ax1.plot(o4['date'],o4['value'], label ='Mar24 RPI Market Fixing: 4.55%')
ax1.plot(o5['date'],o5['value'], label ='Mar25 RPI Market Fixing: 4.37%')
ax1.plot(x4['date'],x4['value'], label ='Mar24 HICPxT Market Fixing: 3.00%')
ax1.axhline(y= 5.3, color = 'black', lw = 0.5, label = 'Barclays Forecast for RPI Mar24: 5.3%')
ax1.axhline(y= 2.56, color = 'black', lw = 0.5, label = 'Barclays Forecast for xT Mar24: 2.56%')
ax1.set_ylabel("RPI", color="steelblue", fontsize=14)
ax1.tick_params(colors='steelblue')
plt.legend(loc = 'upper left')
ax2 = ax1.twinx()
ax2.plot(f3['date'],f3['value'], color='red', label ='FNZ3')
ax2.set_ylabel("FN", color="red", fontsize=14)
ax2.tick_params(colors='red')
plt.legend()
plt.title('Mar24 RPI/xT, Mar25 RPI, Gas', color = 'Blue')
plt.show()







#### RPI: Oct23


o1 = con.bdh('.RPI1023 U Index' , 'PX_LAST', '20220101', latest, longdata = True)
o2 = con.bdh('BPSWIF10 INFA Index' , 'PX_LAST', '20221116', latest, longdata = True)
f3 = con.bdh('FNV3 Comdty', 'PX_LAST', '20220101', latest, longdata = True)
o2['value'] = o2['value']/100
o3 = o1[o1['date'] < '2022-11-16']
o4 = pd.concat([o3,o2])
o4 = o4.reset_index(drop=True)

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


#### RPI: Apr23
o1 = con.bdh('.RPI0423 U Index' , 'PX_LAST', '20220101', latest, longdata = True)
o2 = con.bdh('BPSWIF4 INFA Index' , 'PX_LAST', '20220515', latest, longdata = True)
f3 = con.bdh('FNJ3 Comdty', 'PX_LAST', '20220101', latest, longdata = True)
o2['value'] = o2['value']/100
o3 = o1[o1['date'] < '2022-11-16']
o4 = pd.concat([o1,o2])
o4 = o4.reset_index(drop=True)

fig, ax1 = plt.subplots(figsize=(10,8))
ax1.plot(o4['date'],o4['value'], label ='Oct23 RPI')
ax1.set_ylabel("RPI", color="blue", fontsize=14)
plt.legend(loc = 'upper left')
ax2 = ax1.twinx()
ax2.plot(f3['date'],f3['value'], color='red', label ='FNV3')
ax2.set_ylabel("FN", color="red", fontsize=14)
plt.legend()
plt.title('Snap back to reality, ope there goes gravity', color = 'Green')
plt.show()


#### HICPxT: Oct23
o1 = con.bdh('.XT1023 U Index' , 'PX_LAST', '20220101', latest, longdata = True)
o2 = con.bdh('EUSWIF10 INFA Index' , 'PX_LAST', '20221117', latest, longdata = True)
f3 = con.bdh('TTFUM8 OECM Index', 'PX_LAST', '20220101', latest, longdata = True)
o2['value'] = o2['value']/100
o3 = o1[o1['date'] < '2022-11-17']
o4 = pd.concat([o3,o2])
o4 = o4.reset_index(drop=True)

fig, ax1 = plt.subplots(figsize=(10,8))
ax1.plot(o4['date'],o4['value'], label ='Oct23 HICPxT')
ax1.set_ylabel("xt", color="blue", fontsize=14)
plt.legend(loc = 'upper left')
ax2 = ax1.twinx()
ax2.plot(f3['date'],f3['value'], color='red', label ='TTF Oct23')
ax2.set_ylabel("TTF", color="red", fontsize=14)
plt.legend()
plt.title('Snap back to reality, ope there goes gravity', color = 'Green')
plt.show()



##### HICPxT: Nov23
o1 = con.bdh('.XT1123 U Index' , 'PX_LAST', '20220101', latest, longdata = True)
o2 = con.bdh('EUSWIF11 INFA Index' , 'PX_LAST', '20221216', latest, longdata = True)
f3 = con.bdh('FNX3 Comdty', 'PX_LAST', '20220101', latest, longdata = True)
o2['value'] = o2['value']/100
o3 = o1[o1['date'] < '2022-12-16']
o4 = pd.concat([o3,o2])
o4 = o4.reset_index(drop=True)

fig, ax1 = plt.subplots(figsize=(10,8))
ax1.plot(o4['date'],o4['value'], label ='Nov23 XT')
ax1.set_ylabel("xt", color="blue", fontsize=14)
plt.legend(loc = 'upper left')
ax2 = ax1.twinx()
ax2.plot(f3['date'],f3['value'], color='red', label ='FNX3')
ax2.set_ylabel("FN", color="red", fontsize=14)
plt.legend()
plt.title('Snap back to reality, ope there goes gravity', color = 'Green')
plt.show()









################### fWD FIXINGS ONLY

hicp_xt_fix = ['EUSWIF8 INFA Curncy', 'EUSWIF9 INFA Curncy', 'EUSWIF10 INFA Curncy', 'EUSWIF11 INFA Curncy', 'EUSWIF12 INFA Curncy', 'EUSWIF1 INFA Curncy',
              'EUSWIF2 INFA Curncy', 'EUSWIF3 INFA Curncy', 'EUSWIF4 INFA Curncy', 'EUSWIF5 INFA Curncy', 'EUSWIF6 INFA Curncy',
              'EUSWIF7 INFA Curncy', 'EUSWIH8 INFA Curncy', 'EUSWIH9 INFA Curncy', 'EUSWIH10 INFA Curncy', 'EUSWIH11 INFA Curncy',
              'EUSWIH12 INFA Curncy', 'EUSWIH1 INFA Curncy', 'EUSWIH2 INFA Curncy', 'EUSWIH3 INFA Curncy', 'EUSWIH4 INFA Curncy',
              'EUSWIH5 INFA Curncy', 'EUSWIH6 INFA Curncy', 'EUSWIH7 INFA Curncy']

a1 = [con.bdh( hicp_xt_fix[i], 'PX_LAST', '20230915', '20230915', longdata = True)['value'][0] for i in np.arange(len(hicp_xt_fix))]

hicp = pd.DataFrame()
hicp['fixing_ticker'] = hicp_xt_fix
hicp['month'] = ['Aug-23', 'Sep-23', 'Oct-23', 'Nov-23', 'Dec-23', 'Jan-24', 'Feb-24', 'Mar-24', 'Apr-24', 'May-24', 'Jun-24', 'Jul-24', 'Aug-24',
                 'Sep-24', 'Oct-24', 'Nov-24', 'Dec-24', 'Jan-25', 'Feb-25', 'Mar-25', 'Apr-25', 'May-25', 'Jun-25', 'Jul-25']
hicp['fixing_rate'] = a1

a2 = [0.01*a1[i] for i in np.arange(0,12)]
for i in np.arange(12,24):
    a2.append(100*((((1+a1[i]/10000)**2) / (1+a1[(i-12)]/10000)) - 1))

hicp['fixing_yoy'] = a2


rpi_fix = ['BPSWIF8 INFA Curncy', 'BPSWIF9 INFA Curncy', 'BPSWIF10 INFA Curncy', 'BPSWIF11 INFA Curncy', 'BPSWIF12 INFA Curncy', 'BPSWIF1 INFA Curncy',
           'BPSWIF2 INFA Curncy', 'BPSWIF3 INFA Curncy', 'BPSWIF4 INFA Curncy', 'BPSWIF5 INFA Curncy', 'BPSWIF6 INFA Curncy',
           'BPSWIF7 INFA Curncy', 'BPSWIH8 INFA Curncy', 'BPSWIH9 INFA Curncy', 'BPSWIH10 INFA Curncy', 'BPSWIH11 INFA Curncy',
           'BPSWIH12 INFA Curncy', 'BPSWIH1 INFA Curncy', 'BPSWIH2 INFA Curncy', 'BPSWIH3 INFA Curncy', 'BPSWIH4 INFA Curncy',
           'BPSWIH5 INFA Curncy', 'BPSWIH6 INFA Curncy', 'BPSWIH7 INFA Curncy']

b1 = [con.bdh( rpi_fix[i], 'PX_LAST', '20230915', '20230915', longdata = True)['value'][0] for i in np.arange(len(rpi_fix))]

rpi = pd.DataFrame()
rpi['fixing_ticker'] = rpi_fix
rpi['month'] = ['Aug-23', 'Sep-23', 'Oct-23', 'Nov-23', 'Dec-23', 'Jan-24', 'Feb-24', 'Mar-24', 'Apr-24', 'May-24', 'Jun-24', 'Jul-24', 'Aug-24',
                 'Sep-24', 'Oct-24', 'Nov-24', 'Dec-24', 'Jan-25', 'Feb-25', 'Mar-25', 'Apr-25', 'May-25', 'Jun-25', 'Jul-25']
rpi['fixing_rate'] = b1

b2 = [0.01*b1[i] for i in np.arange(0,12)]
for i in np.arange(12,24):
    b2.append(100*((((1+b1[i]/10000)**2) / (1+b1[(i-12)]/10000)) - 1))

rpi['fixing_yoy'] = b2


uscpi = pd.DataFrame()
uscpi['month'] = ['Aug-23', 'Sep-23', 'Oct-23', 'Nov-23', 'Dec-23', 'Jan-24', 'Feb-24', 'Mar-24', 'Apr-24', 'May-24', 'Jun-24', 'Jul-24', 'Aug-24',
                 'Sep-24', 'Oct-24', 'Nov-24', 'Dec-24', 'Jan-25', 'Feb-25', 'Mar-25', 'Apr-25', 'May-25', 'Jun-25', 'Jul-25']


uscpi_index = [296.171, 296.808, 298.012, 297.711, 296.797, 299.17, 300.84, 301.836, 303.363, 304.127, 305.109, 305.619, 307.026,
               307.11, 307.5, 307.2, 307.3, 308.5, 309.8 ,311.0, 311.9, 312.6 ,313.4, 313.8]

us_1y = 2.686
us_2y = 2.606
us_2y_fix = 305.109*((1+ (us_2y/100))**2)

us_1y1y = ((1+ (us_2y/100))**2) / ((1+ (us_1y/100))**1)
us_1y1y_mom = 100*((us_1y1y**(1/12))-1)

us_seas = [0.312, -0.1348, -0.1531, -0.1182, 0.3086, -0.7993, 0.442, 0.0323, 0.317, 0.0696, -0.0384, -0.2223]

fix_mom = np.array(us_1y1y_mom)+np.array(us_seas)

for i in np.arange(len(fix_mom)):
    uscpi_index.append(uscpi_index[-1]* (1+(fix_mom[i]/100)))

c1 = [100*((uscpi_index[i] / uscpi_index[(i-12)])-1 ) for i in np.arange(12,36)]

uscpi['fixing_yoy'] = c1


len(uscpi_index)
len(uscpi)
len(c1)




################# plotting

plt.figure(figsize=(10,8))
plt.plot(hicp['month'], hicp['fixing_yoy'], label = 'HICPxT',  c = 'blue')
plt.plot(rpi['month'], rpi['fixing_yoy'], label = 'RPI',  c = 'red')
plt.plot(uscpi['month'], uscpi['fixing_yoy'], label = 'USCPI',  c = 'green')
plt.legend()
plt.grid(visible=True, linestyle='--', linewidth=0.2)
plt.ylabel("%", color="black", fontsize=12)
plt.xlabel("Fixing Month", color="black", fontsize=12)
plt.title('Market Implied Inflation Fixings', c = 'darkblue')
plt.xticks(rotation = 90)
plt.ylim(1, 10)
#plt.xticks(fontsize=7.5)
#plt.yticks(fontsize=7.5)
plt.show()














############################# one specific fwd fixing from scratch!
m='10'
ticker = ['EUSWIF'+m+' INFF Curncy', 'EUSWIH'+m+' INFF Curncy']
today = ql.Date(datetime.datetime.now().day, datetime.datetime.now().month, datetime.datetime.now().year)

if int(m) < 8:
    m1 = '0'+str(int(m)+1)
else:
    m1 = str(int(m)+1)

if today.month() > int(m):
    yr_ct = 0
else:
    yr_ct = 1

d1 = str(today.year()-yr_ct)+m1+'20'
d2 = str(today.year()-yr_ct-1)+m1+'20'

o1 = con.bdh(ticker[0] , 'PX_LAST', d2, bbg_date_str(today, ql_date = 1), longdata = True)
o2 = con.bdh(ticker[1] , 'PX_LAST', d2, bbg_date_str(today, ql_date = 1), longdata = True)


df1 = pd.DataFrame()
df1['date'] = o1['date']
df1['f'] = o1['value']/100
df1['h'] = o2['value']/100
df1['fix'] = 0


for i in np.arange(len(df1)):
    if df1['date'][i] >  ql_to_datetime(ql.Date(int(d1[6:8]),int(d1[4:6])+1,int(d1[:4]))):
        df1['fix'][i] = df1['f'][i]
    else:
        df1['fix'][i] =  100*((((1 + (0.01*df1['h'][i]))**2) / ((1 + (0.01*df1['f'][i]))**1))-1)




fig, ax1 = plt.subplots(figsize=(10,8))
ax1.plot(df1['date'],df1['fix'], label ='Oct-24 XT')
ax1.set_ylabel("xt", color="blue", fontsize=14)
plt.legend(loc = 'upper left')
#ax2 = ax1.twinx()
#ax2.plot(f3['date'],f3['value'], color='red', label ='FNX3')
#ax2.set_ylabel("FN", color="red", fontsize=14)
plt.legend()
plt.title('Snap back to reality, ope there goes gravity', color = 'Green')
plt.show()








