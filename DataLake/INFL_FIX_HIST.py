import datetime
import pandas as pd
import pickle
from Utilities import *
from Conventions import FUT_CT,FUT_CT_Q, ccy, ccy_infl, hist

con = pdblp.BCon(debug=False, port=8194, timeout=50000)
con.start()
today = ql.Date(datetime.datetime.now().day, datetime.datetime.now().month, datetime.datetime.now().year)


##### create
crv = ['UKRPI','HICPxT']
#fixings_df = dict([(key, []) for key in crv])
for inf_crv in crv:
    os.chdir('C:\\Users\A00007579\PycharmProjects\pythonProject')
    inf_crv = 'HICPxT'
    c = ccy_infl(inf_crv, today)
    prints = pd.Series([datetime.datetime(int(c.print_dates[i][0:4]), int(c.print_dates[i][5:7]), int(c.print_dates[i][8:10])) for i in range(len(c.print_dates))])
    w1 = [(prints[-1:] + np.timedelta64(30 * i, 'D')).tolist()[0] for i in np.arange(1, 16)]
    w2 = [datetime.datetime(w1[i].year, w1[i].month, 20) for i in np.arange(len(w1))]
    prints = pd.Series(prints.tolist() + w2)
    df1 = pd.DataFrame()
    for m in np.arange(1,13):
        print(m)
#        m=1
        v1 = con.bdh([c.fix_ticker[0]+str(m)+c.fix_ticker[1], c.fix_ticker[0][:-1]+'H'+str(m)+c.fix_ticker[1]], 'PX_LAST', '20130601',bbg_date_str(today, ql_date=1), longdata=True)
        v1['ticker_code'] = [v1['ticker'][i][5] for i in np.arange(len(v1))]
        if m != 12:
            v2 = prints[[prints[i].month == m+1 for i in np.arange(len(prints))]].reset_index(drop=True)
        else:
            v2 = prints[[prints[i].month == 1 for i in np.arange(len(prints))]].reset_index(drop=True)
        v1['month_release'] = [prints[(v1['date'][i].month == prints.dt.month) & (v1['date'][i].year == prints.dt.year)].tolist()[0] for i in np.arange(len(v1))]
        v1['print_release'] = [v2[v1['date'][i] < v2].tolist()[v1['ticker_code'][i] == 'H'] for i in np.arange(len(v1))]
        if m != 12:
            v1['fix_month'] = [datetime.datetime((v1['print_release'][i].year ), m, 1) for i in np.arange(len(v1))]
        else:
            v1['fix_month'] = [datetime.datetime((v1['print_release'][i].year - 1), m, 1) for i in np.arange(len(v1))]
        v1['fix_month2'] = [v1['fix_month'][i].strftime('%b-%y') for i in np.arange(len(v1))]
        ##### clean data
        v3 = v1.groupby('date').apply(lambda x: ((x['ticker_code'] == 'H') & (len(x) == 1)))
        v3 = v3[v3 == 1]
        v1 = v1.drop(index=[v3.index[i][1] for i in np.arange(len(v3.index))]).reset_index(drop=True)
        #### compute fixings
        v1['fixing'] = np.round((v1[v1['ticker_code'] == 'F']['value'] / 100).tolist() + v1.groupby('date').apply(lambda x: get_1y1y_fwd((x['value'] / 100).tolist()) if len(x['value']) > 1 else np.NaN).dropna().tolist(),3)
        v1['gen_month'] = [(v1['fix_month'][i].month - v1['date'][i].month) + 12 * ((v1['fix_month'][i].month < v1['date'][i].month) and ((v1['fix_month'][i].year - v1['date'][i].year) > (v1['ticker_code'][i] == 'H'))) +
                           (v1['date'][i] < v1['month_release'][i]) + 12 * (v1['ticker_code'][i] == 'H') + 1 for i in np.arange(len(v1))]
        df1 = pd.concat([df1,v1], ignore_index=True)
    os.chdir('C:\\Users\A00007579\PycharmProjects\pythonProject\DataLake')
    df1.to_pickle(inf_crv+'_fixing_hist.pkl')
#    fixings_df[inf_crv] = df1





##### update
def update_inflation_fixing_history(crv):
#    crv = ['UKRPI','HICPxT']
    today = ql.Date(datetime.datetime.now().day, datetime.datetime.now().month, datetime.datetime.now().year)
    for inf_crv in crv:
        os.chdir('C:\\Users\A00007579\PycharmProjects\pythonProject')
        inf_crv = crv[1]
        c = ccy_infl(inf_crv, today)
        prints = pd.Series([datetime.datetime(int(c.print_dates[i][0:4]), int(c.print_dates[i][5:7]), int(c.print_dates[i][8:10])) for i in range(len(c.print_dates))])
        w1 = [(prints[-1:] + np.timedelta64(30 * i, 'D')).tolist()[0] for i in np.arange(1, 16)]
        w2 = [datetime.datetime(w1[i].year, w1[i].month, 20) for i in np.arange(len(w1))]
        prints = pd.Series(prints.tolist() + w2)

        hist_saved = pd.read_pickle("./DataLake/"+inf_crv+"_fixing_hist.pkl")

        start_dt = hist_saved.sort_values('date')['date'].tolist()[-40].strftime('%Y%m%d')
        df1 = pd.DataFrame()
        for m in np.arange(1,13):
            v1 = con.bdh([c.fix_ticker[0]+str(m)+c.fix_ticker[1], c.fix_ticker[0][:-1]+'H'+str(m)+c.fix_ticker[1]], 'PX_LAST', start_dt, bbg_date_str(today, ql_date=1), longdata=True)
            v1['ticker_code'] = [v1['ticker'][i][5] for i in np.arange(len(v1))]
            if m != 12:
                v2 = prints[[prints[i].month == m+1 for i in np.arange(len(prints))]].reset_index(drop=True)
            else:
                v2 = prints[[prints[i].month == 1 for i in np.arange(len(prints))]].reset_index(drop=True)
            v1['month_release'] = [prints[(v1['date'][i].month == prints.dt.month) & (v1['date'][i].year == prints.dt.year)].tolist()[0] for i in np.arange(len(v1))]
            v1['print_release'] = [v2[v1['date'][i] < v2].tolist()[0] for i in np.arange(len(v1))]
            v1['fix_month'] = [datetime.datetime((v1['print_release'][i].year + (v1['ticker_code'][i] == 'H')), m, 1) for i in np.arange(len(v1))]
            v1['fix_month2'] = [v1['fix_month'][i].strftime('%b-%y') for i in np.arange(len(v1))]
            ##### clean data
            v3 = v1.groupby('date').apply(lambda x: ((x['ticker_code'] == 'H') & (len(x) == 1)))
            v3 = v3[v3 == 1]
            v1 = v1.drop(index=[v3.index[i][1] for i in np.arange(len(v3.index))]).reset_index(drop=True)
            #### compute fixings
            v1['fixing'] = np.round((v1[v1['ticker_code'] == 'F']['value'] / 100).tolist() + v1.groupby('date').apply(lambda x: get_1y1y_fwd((x['value'] / 100).tolist()) if len(x['value']) > 1 else np.NaN).dropna().tolist(),3)
            v1['gen_month'] = [(v1['fix_month'][i].month - v1['date'][i].month) + 12 * ((v1['fix_month'][i].month < v1['date'][i].month) and ((v1['fix_month'][i].year - v1['date'][i].year) > (v1['ticker_code'][i] == 'H'))) +
                               (v1['date'][i] < v1['month_release'][i]) + 12 * (v1['ticker_code'][i] == 'H') + 1 for i in np.arange(len(v1))]
            df1 = pd.concat([df1,v1], ignore_index=True)
        df2 = pd.concat([hist_saved[~hist_saved['date'].isin(v1['date'].unique())], df1 ], ignore_index=True)
        os.chdir('C:\\Users\A00007579\PycharmProjects\pythonProject\DataLake')
        df2.to_pickle(inf_crv+'_fixing_hist.pkl')
    return




c.fix_hist[~c.fix_hist['date'].isin([datetime.datetime(2024,3,7)])]
c.fix_hist[~c.fix_hist['date'].isin(v1['date'].unique())]




os.chdir('C:\\Users\A00007579\PycharmProjects\pythonProject\DataLake')
with open('infl_fixing_hist.pkl', 'wb') as handle:
    pickle.dump(fixings_df, handle, protocol=pickle.HIGHEST_PROTOCOL)

with open('infl_fixing_hist.pkl', 'rb') as handle:
    b1 = pickle.load(handle)


m = 1
v1 = con.bdh(['BPSWIF1 INFF Curncy','BPSWIH1 INFF Curncy'], 'PX_LAST', '20130601', bbg_date_str(today, ql_date=1), longdata=True)
v1['ticker_code'] = [v1['ticker'][i][5] for i in np.arange(len(v1))]
v2= prints[ [prints[i].month == m+1 for i in np.arange(len(prints))] ].reset_index(drop=True)
v1['print_release'] = [v2[v1['date'][i] < v2].tolist()[0] for i in np.arange(len(v1))]
v1['fix_month'] =  [ datetime.datetime( (v1['print_release'][i].year + (v1['ticker_code'][i] == 'H')) ,m,1)   for i in np.arange(len(v1))]
v1['fix_month2'] = [v1['fix_month'][i].strftime('%b-%y') for i in np.arange(len(v1))]

##### clean data
v2 = v1.groupby('date').apply(lambda x: ((x['ticker_code'] == 'H') & (len(x) == 1)))
v2 = v2[v2 == 1]
v1 = v1.drop(index=[v2.index[i][1] for i in np.arange(len(v2.index))]).reset_index(drop=True)

v1['fixing'] = np.round((v1[v1['ticker_code'] == 'F']['value']/100).tolist() + v1.groupby('date').apply(lambda x: get_1y1y_fwd((x['value']/100).tolist()) if len(x['value'])>1 else np.NaN).dropna().tolist(),3)

[(v1['fix_month'][i].month - v1['date'][i].month) for i in np.arange(len(v1))]

for i in np.arange(len(v1)):
    print(i, v1['date'][i],(v1['fix_month'][i].month - v1['date'][i].month))

v1[4250:4280]



r1 = v1[v1['fix_month2']=='Apr-23'].reset_index(drop=True)

r1['gen_month']= [ (r1['fix_month'][i].month - r1['date'][i].month) +
                      12*(   (r1['fix_month'][i].month < r1['date'][i].month)     and   ( (r1['fix_month'][i].year - r1['date'][i].year) >  (r1['ticker_code'][i] == 'H'))       ) +
                      (r1['date'][i] < r1['month_release'][i]) +
                      12*(r1['ticker_code'][i] == 'H') + 1 for i in np.arange(len(r1))]


r1['month_release']  = [prints[(r1['date'][i].month == prints.dt.month) & (r1['date'][i].year == prints.dt.year)].tolist()[0] for i in np.arange(len(r1))]










len(v1)
len((v1[v1['ticker_code'] == 'F']['value']/100).tolist())
v1.groupby('date').apply(lambda x: get_1y1y_fwd((x['value']/100).tolist()) if len(x['value'])>1 else np.NaN).dropna().tolist()

v1.groupby('date').apply(lambda x: x['ticker_code']=='F').sum()
v1.groupby('date').apply(lambda x: x['ticker_code']=='H').sum()

v1.groupby('date').apply(lambda x: len(x))
v1.groupby('date').apply(lambda x: x['ticker_code']=='H').sum()


v1.groupby('date').apply(lambda x: x['date'])

v5 = v1.groupby('date').apply(lambda x: ((x['ticker_code']=='H') & (len(x)==1)))
v6 = v5[v5==1]
[v6.index[i][1] for i in np.arange(len(v6.index))]



v1.groupby('date').apply(lambda x: len(x) == 2).sum()

v1.groupby('date').apply(lambda row: row.name)


v1[2775:2800]


v1[:50]
v1[220:270]
v1[-50:]


v3 = v1[v1['fix_month2'] == 'Apr-23'].reset_index(drop=True)

v3[:50]
v3[210:260]
v3[-50:]


a = ['UKRPI']
c = ccy_infl(a[0], today)

df_feed = c.fix_hist[c.fix_hist['fix_month2'] == 'Sep-24']
df_feed = c.fix_hist[c.fix_hist['gen_month'] == 12]


df_feed = df_feed.sort_values('date')
fig, ax1 = plt.subplots(figsize=(10,8))
ax1.plot(df_feed['date'],df_feed['fixing'], label ='##')
ax1.set_ylabel("rpi", color="blue", fontsize=14)
plt.legend(loc = 'upper left')
plt.legend()
plt.show()

c.fixing_hist[-50:]





x = con.bulkref('ECCPEMUY Index', 'ECO_FUTURE_RELEASE_DATE_LIST', ovrds=[("START_DT", '20130101'), ("END_DT", bbg_date_str(c.cal.advance(today,ql.Period('3Y')), ql_date=1) )])['value']
x2 = pd.Series([datetime.datetime(int(x[i][0:4]), int(x[i][5:7]), int(x[i][8:10])) for i in range(len(x))])

x2[-20:]

v4= x2[ [x2[i].month == 5 for i in np.arange(len(x2))] ].reset_index(drop=True)
v1['print_release'] = [v4[v1['date'][i] < v4].tolist()[0] for i in np.arange(len(v1))]






