#### WIRP
import pandas as pd

curve = 'US'
method = '0'
inst = 'B'
datatype = 'FR'




x = con.bulkref('FDTR Index','ECO_FUTURE_RELEASE_DATE_LIST')['value']
y = pd.Series([ datetime.datetime(int(x[i][0:4]),int(x[i][5:7]),int(x[i][8:10])) for i in range(len(x)) ])
y = pd.DataFrame(y[y > (datetime.datetime.now()+pd.DateOffset(days=-1))], columns = ['Meets'])
y.reset_index(inplace=True, drop = True)

#y['Meets'][13].strftime("%b").upper()+y['Meets'][13].strftime("%Y")+' Index'

y1 = [curve+method+inst+datatype+' '+y['Meets'][i].strftime("%b").upper()+y['Meets'][i].strftime("%Y")+' Index' for i in np.arange(len(y)) ]

con.bdh(y1,'PX_LAST','20220810','20220810', longdata = True)

con.ref(y1[0], 'PX_LAST')['value'][0]


datetime.datetime.now().strftime("%b").upper()+datetime.datetime.now().strftime("%Y")


datetime.datetime.now()+datetime.timedelta(30).strftime("%b%Y")

datetime.datetime.now.AddMonths(1)


datetime.datetime.now().AddMonths(1)

relativedelta(months=3)

datetime.timedelta(3*365/12)


con.ref(bond_fut_dets[0]+' Govt', ['YLD_YTM_BID'], ovrds =[('PX_BID',fwd_px),(('SETTLE_DT',bbg_date_str(bond_fut_dets[1], ql_date=0)))])


con.ref('YMH4 Comdty', ['RISK_MID'], ovrds =[('MID',96.3)])


p = 95.865
b = (100-p)/200

p_range = np.arange(93, 100, 0.005)
c_value = [(3*(1-(  (1/(1+ ((100-p)/200)  ))**20))/  ((100-p)/200)  ) + 100*( (1/(1+ ((100-p)/200) ))**20) for p in p_range]

df1 = pd.DataFrame()
df1['fut_px'] = np.round(p_range,3)
df1['c_value'] = c_value
df1['tick_value'] = df1['c_value'].diff()
df1['dv01'] = df1['tick_value']*200   ######  this is 200 because tick size = 0.005.... change for other contracts !!



df1['c_value'].diff()


df1[df1['fut_px'] == 95.87]