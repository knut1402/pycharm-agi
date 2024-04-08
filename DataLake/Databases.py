####### List of Static Databases

import os
import pandas as pd
import numpy as np
import datetime
import pdblp
import runpy
import QuantLib as ql
import matplotlib as mpl
import matplotlib.pyplot as plt
from tabulate import tabulate
from Conventions import FUT_CT, ccy, ccy_infl


con = pdblp.BCon(debug=False, port=8194, timeout=50000)
con.start()

############################# INFLATION HISTORICAL FIXINGS
os.chdir('C:\\Users\A00007579\PycharmProjects\pythonProject\DataLake')
os.getcwd()

### HICPxT
a = 'ESTER_DC'
b=0
today = ql.Date(datetime.datetime.now().day,datetime.datetime.now().month,datetime.datetime.now().year)
c = ccy(a,today)

### handle dates
ref_date = c.cal.advance(today,b,ql.Days)
ref_date_1 = c.cal.advance(ref_date,-1,ql.Days)
settle_date = c.cal.advance(ref_date,2,ql.Days)
settle_date_1 = c.cal.advance(ref_date_1,2,ql.Days)

if ref_date.dayOfMonth() < 10:
    d0 = str(0)+str(ref_date.dayOfMonth())
else:
    d0 = str(ref_date.dayOfMonth())
if ref_date_1.dayOfMonth() < 10:
    d1 = str(0)+str(ref_date_1.dayOfMonth())
else:
    d1 = str(ref_date_1.dayOfMonth())
    
if ref_date.month() < 10:
    m0 = str(0)+str(ref_date.month())
else:
    m0 = str(ref_date.month())
if ref_date_1.month() < 10:
    m1 = str(0)+str(ref_date_1.month())
else:
    m1 = str(ref_date_1.month())
        
bbg_t = str(ref_date.year())+m0+d0
bbg_t_1 = str(ref_date.year())+m1+d1

### get historical data
inf_index = 'CPTFEMU Index'
last_month_dt = con.ref(inf_index, 'LAST_UPDATE_DT')['value'][0]
last_index_month = ql.Date(1,last_month_dt.month,last_month_dt.year)
inf_index_hist = pd.DataFrame()
schedule = ql.MakeSchedule(ql.Date(1,1,2000), last_index_month, ql.Period('1M'))
inf_index_hist['months'] = [schedule[i] for i in range(len(schedule))]
inf_index_hist['index'] = con.bdh(inf_index, 'PX_LAST','20000101',bbg_t, longdata=True)['value']
inf_index_hist['months'] = pd.to_datetime([str(inf_index_hist['months'][i]) for i in np.arange(len(inf_index_hist))])
###### BARCAP fixings forecast
forecast_schedule = schedule = ql.MakeSchedule(last_index_month+ql.Period('1M'), last_index_month+ql.Period('7M'), ql.Period('1M'))
forecast_index_hist = pd.DataFrame()
forecast_index_hist['months'] = [forecast_schedule[i] for i in range(len(forecast_schedule))]
forecast_index_hist['months'] = pd.to_datetime([str(forecast_index_hist['months'][i]) for i in np.arange(len(forecast_index_hist))])
forecast_index_hist['index'] = [125.05, 125.59, 125.78, 125.98, 125.76, 126.02, 126.15]
#### combine fixings:
#inf_index_hist = inf_index_hist.append(forecast_index_hist, ignore_index = True)
inf_index_hist =pd.concat([inf_index_hist, forecast_index_hist], ignore_index=True)
#### write to database
os.chdir('C:\\Users\A00007579\PycharmProjects\pythonProject\DataLake')
inf_index_hist.to_pickle('HICPxT_hist.pkl')

### FRCPI
a = 'EUR_3M'
b=0
today = ql.Date(datetime.datetime.now().day,datetime.datetime.now().month,datetime.datetime.now().year)
c = ccy(a,today)

### handle dates
ref_date = c.cal.advance(today,b,ql.Days)
ref_date_1 = c.cal.advance(ref_date,-1,ql.Days)
settle_date = c.cal.advance(ref_date,2,ql.Days)
settle_date_1 = c.cal.advance(ref_date_1,2,ql.Days)

if ref_date.dayOfMonth() < 10:
    d0 = str(0)+str(ref_date.dayOfMonth())
else:
    d0 = str(ref_date.dayOfMonth())
if ref_date_1.dayOfMonth() < 10:
    d1 = str(0)+str(ref_date_1.dayOfMonth())
else:
    d1 = str(ref_date_1.dayOfMonth())
    
if ref_date.month() < 10:
    m0 = str(0)+str(ref_date.month())
else:
    m0 = str(ref_date.month())
if ref_date_1.month() < 10:
    m1 = str(0)+str(ref_date_1.month())
else:
    m1 = str(ref_date_1.month())
        
bbg_t = str(ref_date.year())+m0+d0
bbg_t_1 = str(ref_date.year())+m1+d1

### get historical data
inf_index = 'FRCPXTOB Index'
last_month_dt = con.ref(inf_index, 'LAST_UPDATE_DT')['value'][0]
last_index_month = ql.Date(1,last_month_dt.month,last_month_dt.year)
inf_index_hist = pd.DataFrame()
schedule = ql.MakeSchedule(ql.Date(1,1,2000), last_index_month, ql.Period('1M'))
inf_index_hist['months'] = [schedule[i] for i in range(len(schedule))]
inf_index_hist['index'] = con.bdh(inf_index, 'PX_LAST','20000101',bbg_t, longdata=True)['value']
inf_index_hist['months'] = pd.to_datetime([str(inf_index_hist['months'][i]) for i in np.arange(len(inf_index_hist))])

###### BARCAP fixings forecast
forecast_schedule = schedule = ql.MakeSchedule(last_index_month+ql.Period('1M'), last_index_month+ql.Period('6M'), ql.Period('1M'))
forecast_index_hist = pd.DataFrame()
forecast_index_hist['months'] = [forecast_schedule[i] for i in range(len(forecast_schedule))]
forecast_index_hist['months'] = pd.to_datetime([str(forecast_index_hist['months'][i]) for i in np.arange(len(forecast_index_hist))])
forecast_index_hist['index'] = [117.46, 117.71, 117.82, 118.24, 118.15, 118.64]
#### combine fixings:
inf_index_hist =pd.concat([inf_index_hist, forecast_index_hist], ignore_index=True)
#### write to database
os.chdir('C:\\Users\A00007579\PycharmProjects\pythonProject\DataLake')
inf_index_hist.to_pickle('FRCPI_hist.pkl')


### UKRPI
a = 'SONIA_DC'
b=0
today = ql.Date(datetime.datetime.now().day,datetime.datetime.now().month,datetime.datetime.now().year)
c = ccy(a,today)

### handle dates
ref_date = c.cal.advance(today,b,ql.Days)
ref_date_1 = c.cal.advance(ref_date,-1,ql.Days)
settle_date = c.cal.advance(ref_date,2,ql.Days)
settle_date_1 = c.cal.advance(ref_date_1,2,ql.Days)

if ref_date.dayOfMonth() < 10:
    d0 = str(0)+str(ref_date.dayOfMonth())
else:
    d0 = str(ref_date.dayOfMonth())
if ref_date_1.dayOfMonth() < 10:
    d1 = str(0)+str(ref_date_1.dayOfMonth())
else:
    d1 = str(ref_date_1.dayOfMonth())
    
if ref_date.month() < 10:
    m0 = str(0)+str(ref_date.month())
else:
    m0 = str(ref_date.month())
if ref_date_1.month() < 10:
    m1 = str(0)+str(ref_date_1.month())
else:
    m1 = str(ref_date_1.month())
        
bbg_t = str(ref_date.year())+m0+d0
bbg_t_1 = str(ref_date.year())+m1+d1

### get historical data
inf_index = 'UKRPI Index'
last_month_dt = con.ref(inf_index, 'LAST_UPDATE_DT')['value'][0]
last_index_month = ql.Date(1,last_month_dt.month,last_month_dt.year)
inf_index_hist = pd.DataFrame()
schedule = ql.MakeSchedule(ql.Date(1,1,2000), last_index_month, ql.Period('1M'))
inf_index_hist['months'] = [schedule[i] for i in range(len(schedule))]
inf_index_hist['index'] = con.bdh(inf_index, 'PX_LAST','20000101',bbg_t, longdata=True)['value']
inf_index_hist['months'] = pd.to_datetime([str(inf_index_hist['months'][i]) for i in np.arange(len(inf_index_hist))])

###### BARCAP fixings forecast
forecast_schedule = schedule = ql.MakeSchedule(last_index_month+ql.Period('1M'), last_index_month+ql.Period('7M'), ql.Period('1M'))
forecast_index_hist = pd.DataFrame()
forecast_index_hist['months'] = [forecast_schedule[i] for i in range(len(forecast_schedule))]
forecast_index_hist['months'] = pd.to_datetime([str(forecast_index_hist['months'][i]) for i in np.arange(len(forecast_index_hist))])
forecast_index_hist['index'] = [380.9, 382.7, 384.7, 386.3, 387.4, 386.8, 388.0 ]
#### combine fixings:
inf_index_hist =pd.concat([inf_index_hist, forecast_index_hist], ignore_index=True)
#### write to database
os.chdir('C:\\Users\A00007579\PycharmProjects\pythonProject\DataLake')
inf_index_hist.to_pickle('UKRPI_hist.pkl')


### USCPI
a = 'SOFR_DC'
b=0
today = ql.Date(datetime.datetime.now().day,datetime.datetime.now().month,datetime.datetime.now().year)
c = ccy(a,today)

### handle dates
ref_date = c.cal.advance(today,b,ql.Days)
ref_date_1 = c.cal.advance(ref_date,-1,ql.Days)
settle_date = c.cal.advance(ref_date,2,ql.Days)
settle_date_1 = c.cal.advance(ref_date_1,2,ql.Days)

if ref_date.dayOfMonth() < 10:
    d0 = str(0)+str(ref_date.dayOfMonth())
else:
    d0 = str(ref_date.dayOfMonth())
if ref_date_1.dayOfMonth() < 10:
    d1 = str(0)+str(ref_date_1.dayOfMonth())
else:
    d1 = str(ref_date_1.dayOfMonth())
    
if ref_date.month() < 10:
    m0 = str(0)+str(ref_date.month())
else:
    m0 = str(ref_date.month())
if ref_date_1.month() < 10:
    m1 = str(0)+str(ref_date_1.month())
else:
    m1 = str(ref_date_1.month())
        
bbg_t = str(ref_date.year())+m0+d0
bbg_t_1 = str(ref_date.year())+m1+d1

### get historical data
inf_index = 'CPURNSA Index'
last_month_dt = con.ref(inf_index, 'LAST_UPDATE_DT')['value'][0]
last_index_month = ql.Date(1,last_month_dt.month,last_month_dt.year)
inf_index_hist = pd.DataFrame()
schedule = ql.MakeSchedule(ql.Date(1,1,2000), last_index_month, ql.Period('1M'))
inf_index_hist['months'] = [schedule[i] for i in range(len(schedule))]
inf_index_hist['index'] = con.bdh(inf_index, 'PX_LAST','20000101',bbg_t, longdata=True)['value']
inf_index_hist['months'] = pd.to_datetime([str(inf_index_hist['months'][i]) for i in np.arange(len(inf_index_hist))])
###### BARCAP fixings forecast
forecast_schedule = schedule = ql.MakeSchedule(last_index_month+ql.Period('1M'), last_index_month+ql.Period('9M'), ql.Period('1M'))
forecast_index_hist = pd.DataFrame()
forecast_index_hist['months'] = [forecast_schedule[i] for i in range(len(forecast_schedule))]
forecast_index_hist['months'] = pd.to_datetime([str(forecast_index_hist['months'][i]) for i in np.arange(len(forecast_index_hist))])
forecast_index_hist['index'] = [311.831, 312.815, 313.689, 314.787, 315.025, 315.613, 315.94, 315.709, 315.805 ]
#### combine fixings:
inf_index_hist =pd.concat([inf_index_hist, forecast_index_hist], ignore_index=True)
#### write to database
os.chdir('C:\\Users\A00007579\PycharmProjects\pythonProject\DataLake')
inf_index_hist.to_pickle('USCPI_hist.pkl')


### CADCPI
a = 'CAD_3M'
b=0
today = ql.Date(datetime.datetime.now().day,datetime.datetime.now().month,datetime.datetime.now().year)
c = ccy(a,today)

### handle dates
ref_date = c.cal.advance(today,b,ql.Days)
ref_date_1 = c.cal.advance(ref_date,-1,ql.Days)
settle_date = c.cal.advance(ref_date,2,ql.Days)
settle_date_1 = c.cal.advance(ref_date_1,2,ql.Days)

if ref_date.dayOfMonth() < 10:
    d0 = str(0)+str(ref_date.dayOfMonth())
else:
    d0 = str(ref_date.dayOfMonth())
if ref_date_1.dayOfMonth() < 10:
    d1 = str(0)+str(ref_date_1.dayOfMonth())
else:
    d1 = str(ref_date_1.dayOfMonth())
    
if ref_date.month() < 10:
    m0 = str(0)+str(ref_date.month())
else:
    m0 = str(ref_date.month())
if ref_date_1.month() < 10:
    m1 = str(0)+str(ref_date_1.month())
else:
    m1 = str(ref_date_1.month())
        
bbg_t = str(ref_date.year())+m0+d0
bbg_t_1 = str(ref_date.year())+m1+d1

### get historical data
inf_index = 'CACPI Index'
last_month_dt = con.ref(inf_index, 'LAST_UPDATE_DT')['value'][0]
last_index_month = ql.Date(1,last_month_dt.month,last_month_dt.year)
inf_index_hist = pd.DataFrame()
schedule = ql.MakeSchedule(ql.Date(1,1,2000), last_index_month, ql.Period('1M'))
inf_index_hist['months'] = [schedule[i] for i in range(len(schedule))]
inf_index_hist['index'] = con.bdh(inf_index, 'PX_LAST','20000101',bbg_t, longdata=True)['value']
inf_index_hist['months'] = pd.to_datetime([str(inf_index_hist['months'][i]) for i in np.arange(len(inf_index_hist))])
###### BARCAP fixings forecast
#forecast_schedule = schedule = ql.MakeSchedule(last_index_month+ql.Period('1M'), last_index_month+ql.Period('7M'), ql.Period('1M'))
#forecast_index_hist = pd.DataFrame()
#forecast_index_hist['months'] = [forecast_schedule[i] for i in range(len(forecast_schedule))]
#forecast_index_hist['months'] = pd.to_datetime([str(forecast_index_hist['months'][i]) for i in np.arange(len(forecast_index_hist))])
#forecast_index_hist['index'] = [278.80,280.53,282.43,283.43,284.27,284.79, 285.26]
#### combine fixings:
#inf_index_hist =pd.concat([inf_index_hist, forecast_index_hist], ignore_index=True)
#### write to database

inf_index_hist.to_pickle('CACPI_hist.pkl')






os.chdir('C:\\Users\A00007579\PycharmProjects\pythonProject')   ######### <------- run last











#### building linker database
import os
os.getcwd()
os.chdir('C:\\Users\A00007579\OneDrive - Allianz Global Investors\Documents\Python archive\DataLake') 
#### EUR Linker     #########################################################################################################################################################################################################
euro_linker_db = pd.DataFrame()
euro_linker_db['linker_isin'] = ['DE0001030542 Govt', 'DE0001030567 Govt', 'DE0001030559 Govt', 'DE0001030583 Govt', 'DE0001030575 Govt',
                                 'FR0011427848 Govt', 'FR0013519253 Govt', 'FR0011008705 Govt', 'FR0013410552 Govt', 'FR0011982776 Govt',
                                 'FR0014001N38 Govt', 'FR0000188799 Govt', 'FR0013327491 Govt', 'FR0010447367 Govt', 'FR0013209871 Govt',
                                 'IT0005329344 Govt', 'IT0004243512 Govt', 'IT0005004426 Govt', 'IT0005415416 Govt', 'IT0004735152 Govt',
                                 'IT0005246134 Govt', 'IT0005387052 Govt', 'IT0005138828 Govt', 'IT0003745541 Govt', 'IT0004545890 Govt', 'IT0005436701 Govt',
                                 'ES0000012B70 Govt', 'ES00000126A4 Govt', 'ES00000128S2 Govt', 'ES00000127C8 Govt', 'ES0000012C12 Govt',
                                 'FR0010585901 Govt', 'FR0012558310 Govt', 'FR0013238268 Govt', 'FR0000186413 Govt', 'FR0014003N51 Govt']
euro_linker_db['compar_isin'] = ['DE0001102309 Govt', 'DE0001102390 Govt', 'DE0001102499 Govt', 'DE0001102531 Govt', 'DE0001102341 Govt',
                                 'FR0011619436 Govt', 'FR0013508470 Govt', 'FR0011317783 Govt', 'FR0013407236 Govt', 'FR0011883966 Govt',
                                 'FR0012993103 Govt', 'FR0000187635 Govt', 'FR0013154044 Govt', 'FR0010773192 Govt', 'FR0013257524 Govt',
                                 'IT0005325946 Govt', 'IT0004356843 Govt', 'IT0005001547 Govt', 'IT0005370306 Govt', 'IT0004644735 Govt',
                                 'IT0004889033 Govt', 'IT0005383309 Govt', 'IT0005094088 Govt', 'IT0003535157 Govt', 'IT0004532559 Govt', 'IT0005425233 Govt',
                                 'ES0000012B62 Govt', 'ES00000126B2 Govt', 'ES0000012A89 Govt', 'ES00000127A2 Govt', 'ES00000128Q6 Govt',
                                 'FR0010466938 Govt', 'FR0012517027 Govt', 'FR0013286192 Govt', 'FR0000571218 Govt', 'FR0014002WK3 Govt']

l1 = [('linker_isin','SECURITY_NAME'),
      ('compar_isin','SECURITY_NAME'),
      ('linker_isin','COUNTRY'),
      ('linker_isin','REFERENCE_INDEX')]

for e1,f1 in l1:
    d1 = con.ref(euro_linker_db[e1].tolist(),[f1])
    d1 = d1.drop(columns = ['field'])
    d1.columns = [e1, f1]
    euro_linker_db = pd.merge(euro_linker_db, d1, on = e1 )

euro_linker_db.columns = ['linker_isin', 'compar_isin', 'linker', 'nominal', 'country', 'index']

euro_linker_db.to_pickle('euro_linker')
euro_linker_db = pd.read_pickle('euro_linker')


#### TIPS     #############################################################################################################################################################################################################

os.getcwd()
os.chdir('C:\\Users\A00007579\OneDrive - Allianz Global Investors\Documents\Python archive\DataLake') 

df_tips = pd.read_csv('tips_bbg_upload.csv', nrows=49)

tips_db = pd.DataFrame()
tips_db['linker_isin'] = df_tips['linker']
tips_db['compar_isin'] = df_tips['comparator']


l1 = [('linker_isin','linker','SECURITY_NAME'),
      ('compar_isin','nominal','SECURITY_DES'),
      ('linker_isin','country','COUNTRY'),
      ('linker_isin','index','REFERENCE_INDEX')]

for e1,f1,g1 in l1:
    d1 = con.ref(tips_db[e1].tolist(),[g1])
    d1 = d1.drop(columns = ['field'])
    tips_db[f1] = [d1[d1['ticker'] == tips_db[e1][i]]['value'].tolist()[0] for i in np.arange(len(tips_db))]
    
tips_db.columns = ['linker_isin', 'compar_isin', 'linker', 'nominal', 'country', 'index']

tips_db.to_pickle('tips')
tips_db = pd.read_pickle('tips')


#### RRB     #####################################################################################################################################################################################################################

os.getcwd()
os.chdir('C:\\Users\A00007579\OneDrive - Allianz Global Investors\Documents\Python archive\DataLake') 

rrb_db = pd.DataFrame()
rrb_db['linker_isin'] = ['CA135087VS05 Govt', 'CA135087WV25 Govt', 'CA135087XQ21 Govt', 'CA135087YK42 Govt', 'CA135087ZH04 Govt','CA135087B949 Govt', 'CA135087G997 Govt', 'CA135087M433 Govt']
rrb_db['compar_isin'] = ['CA135087L930 Govt', 'CA135087N266 Govt', 'CA135087XW98 Govt', 'CA135087YQ12 Govt', 'CA135087ZS68 Govt','CA135087D358 Govt', 'CA135087H722 Govt', 'CA135087M680 Govt']

l1 = [('linker_isin','SECURITY_NAME'),
      ('compar_isin','SECURITY_NAME'),
      ('linker_isin','COUNTRY'),
      ('linker_isin','REFERENCE_INDEX')]

for e1,f1 in l1:
    d1 = con.ref(rrb_db[e1].tolist(),[f1])
    d1 = d1.drop(columns = ['field'])
    d1.columns = [e1, f1]
    rrb_db = pd.merge(rrb_db, d1, on = e1 )

rrb_db.columns = ['linker_isin', 'compar_isin', 'linker', 'nominal', 'country', 'index']

rrb_db.to_pickle('rrbs')
rrb_db = pd.read_pickle('rrbs')












