### testing only!
#ois_db.to_pickle('SOFR_1.pkl')
#sofr_1 = pd.read_pickle("SOFR_1.pkl")

today = ql.Date(datetime.datetime.now().day, datetime.datetime.now().month, datetime.datetime.now().year)
##### ois
sofr_h = pd.read_pickle("./DataLake/SOFR_H.pkl")
sonia_h = pd.read_pickle("./DataLake/SONIA_H.pkl")
ester_h = pd.read_pickle("./DataLake/ESTER_H.pkl")


sofr_h = df_test

sofr_live = ois_dc_build('SOFR_DC', b=0)
sofr_h.iloc[-21]['Fwd_Rates']
sofr_h.iloc[-21]['Swap_Rates']
Swap_Pricer( [[ ois_from_nodes(sofr_h.iloc[-21],ccy('SONIA_DC',today)) ,0,4]], fixed_leg_freq = 0).rate

sofr_h.index[-21]


#### libor
usd3m_h = pd.read_pickle("./DataLake/USD_3M_H.pkl")

Swap_Pricer( [[ libor_from_nodes( usd3m_h.iloc[4500] , ois_hist) ,15,1]], fixed_leg_freq = 0).rate
usd3m_h.iloc[4500]['Fwd_Rates']
usd3m_h.iloc[4500]['Swap_Rates']




######## plot curve from nodes !!! ( sanity check tool)


a = 'USD_3M'
node_hist = pd.read_pickle("./DataLake/"+a+"_H.pkl")
c = ccy(a, today)
ois_hist = hist[c.dc_index]

node = node_hist.iloc[5000]
node.name
bcrv = libor_from_nodes( node , c, ois_hist)
node['Table']
node['Swap_Rates']
ql.Settings.instance().evaluationDate = bcrv.trade_date

dates_in2 = ql.MakeSchedule(bcrv.ref_date, c.cal.advance(bcrv.ref_date, ql.Period('5Y')), ql.Period('1D'))
r1 = [100*bcrv.curve[0].forwardRate( d1, c.cal.advance(d1, ql.Period('3M')), ql.Actual360(), ql.Simple).rate() for d1 in dates_in2]
r2 = [100*bcrv.curve[1].forwardRate( d1, c.cal.advance(d1, ql.Period('3M')), ql.Actual360(), ql.Simple).rate() for d1 in dates_in2]
x = [ np.round((ql_to_datetime(d)-ql_to_datetime(bcrv.ref_date)).days/365,5) for d in dates_in2]

plt.plot(x,r1)
plt.plot(x,r2)
plt.title(a+':   '+node.name)
plt.show()


eur_6m_live = swap_build('EUR_6M', b=0)
eur_6m_live.rates
eur_6m_live.nodes
Swap_Pricer( [[ eur_6m_live ,0,2]], fixed_leg_freq = 0).dates


bcrv.trade_date
bcrv.ref_date
bcrv.nodes



def ois_from_nodes(a,conv):
#    a = sonia_h.iloc[3500]
#    c = ccy(a['Index'], today)
    c = conv
    d1 = a.name

    trade_date = ql.Date(int(d1.split('/')[0]), int(d1.split('/')[1]), int(d1.split('/')[2]))
    ref_date = c.cal.advance(trade_date,2,ql.Days)
    ref_fix = a['Fixing']
    tab = a['Table']
    swap_rates = a['Swap_Rates']
    swap_rates.columns = ['Tenor','SwapRate']
    curve_ccy = con.ref(c.bbg_curve,'CRNCY')['value'][0]

    q_dates = [datetime_to_ql(a['Dates'][j]) for j in np.arange(len(a['Dates']))]
    l_rates = a['Rates']

    ois_curve = ql.MonotonicLogCubicDiscountCurve(q_dates, l_rates, ql.Actual360(), ql.UnitedStates(ql.UnitedStates.FederalReserve))

    class ois_from_nodes():
        def __init__(self):
            self.tab = a.Table[['Tenor','Rate']]
            self.trade_date = trade_date
            self.ref_date = ref_date
            self.trade_date = trade_date
            self.ref_fix = ref_fix
            self.table = tab
            self.rates = swap_rates
            self.curve = ois_curve
            self.nodes = tuple(zip(q_dates, l_rates))
            self.rates = swap_rates
            self.table = a.Table
            self.cal = c.cal
            self.index = c.index
            self.ois_index = a['Index']
            self.fixing = c.fixing
            self.ois_trigger = c.ois_trigger
            self.ccy = curve_ccy
            self.bbgplot_tickers = c.bbgplot_tickers

    return ois_from_nodes()


def ois_from_hist(a, d1=0, d2=0):
#    a = sofr_h
#    d1 = '-5d'
#    d2 = '-1w'

    b = a[-1:]['Index'].iloc[0]
    today = ql.Date(datetime.datetime.now().day, datetime.datetime.now().month, datetime.datetime.now().year)
    c = ccy(b, today)

    if isinstance(d1, int) == True:
        if d1 == 0:
            start = 0
        else:
            start = len(a.index)+d1
    if isinstance(d1, str) == True:
        try:
            d11 = ql.Date(int(d1.split('-')[0]), int(d1.split('-')[1]), int(d1.split('-')[2]))
            start = -1*sum(a['Ref_Date'].date() > datetime.datetime.combine(ql_to_datetime(d11), datetime.datetime.min.time()) )+len(a.index)
        except:
            if d1[-1] in ('D', 'd'):
                unit = ql.Days
            elif d1[-1] in ('W', 'w'):
                unit = ql.Weeks
            elif d1[-1] in ('M', 'm'):
                unit = ql.Months
            elif d1[-1] in ('Y', 'y'):
                unit = ql.Years
            d12 = c.cal.advance(today, int(d1[0:-1]), unit)
            start = -1*sum(a['Ref_Date'] > datetime.datetime.combine(ql_to_datetime(d12), datetime.datetime.min.time()) )+len(a.index)

    if isinstance(d2, int) == True:
        end = len(a.index)+d2
    if isinstance(d2, str) == True:
        try:
            d21 = ql.Date(int(d2.split('-')[0]), int(d2.split('-')[1]), int(d2.split('-')[2]))
            end = -1 * sum(a['Ref_Date'] > datetime.datetime.combine(ql_to_datetime(d21), datetime.datetime.min.time()) ) + len(a.index)
        except:
            if d2[-1] in ('D', 'd'):
                unit = ql.Days
            elif d2[-1] in ('W', 'w'):
                unit = ql.Weeks
            elif d2[-1] in ('M', 'm'):
                unit = ql.Months
            elif d2[-1] in ('Y', 'y'):
                unit = ql.Years
            d22 = c.cal.advance(today, int(d2[0:-1]), unit)
            end = -1 * sum(a['Ref_Date'] > datetime.datetime.combine(ql_to_datetime(d22), datetime.datetime.min.time()) ) + len(a.index)

    if end <= start:
        print('Error = Start Date > End Date;')

    s1 = [ois_from_nodes(a.iloc[i], b) for i in np.arange(start,end)]
    return s1

s_crvs =  ois_from_hist(sofr_h, d1=-400, d2 = -10)
len(s_crvs)



def ois_from_hist2(a, d1):
    '''Specific Dates ONLY'''
#    a = sofr_h
#    d1 = ['10-05-2023', '21-04-2023']

    b = a[-1:]['Index'].iloc[0]
    try:
        x2 = sofr_h.index.get_indexer(d1)
    except:
        x2 = []
        for i in d1:
            d2 = ql.Date(int(i.split('-')[0]), int(i.split('-')[1]), int(i.split('-')[2]))
            x2.append(-1 * sum(a['Ref_Date'] >= ql_to_datetime(d2)) + len(a.index))

    s1 = [ois_from_nodes(a.iloc[i], b) for i in x2]
    return s1



def quick_swap(a, u1=ql.Years, u2=ql.Years, spread =0, fly = 0):
    ''' Quick Swap only works when actual dates do not need to be specified. settlement_days not specified currently '''
    output_rate=[]
    for k in np.arange(len(a)):
        termStructure = ql.YieldTermStructureHandle(a[k][0].curve)
        index = a[k][0].index(termStructure)
        engine = ql.DiscountingSwapEngine(termStructure)
        start = ql.Period(a[k][1], u1)
        swapTenor = ql.Period(a[k][2], u2)
        swap = ql.MakeVanillaSwap(swapTenor, index, 0.0, start, pricingEngine=engine, settlementDays=2)
        output_rate.append(100*swap.fairRate())

    if spread == 1:
        output_rate = [100*(output_rate[1]-output_rate[0])]
    if fly == 1:
        output_rate = [np.round(np.dot(np.array(output_rate), np.array([-100, 200, -100])), 3)]
    return output_rate




t10 = time.time()
s2 = ois_from_hist(sofr_h, d1=0, d2=0)
t11 = time.time()
t11-t10
len(s2)

Swap_Pricer([[s2[-1],0,2],[s2[-1],0,5]]).dates
Swap_Pricer([[s2[-1],0,2],[s2[-1],2,2], [s2[-1],5,5]]).rate

s2[-1].trade_date
s2[-1].ref_date


Swap_curve_fwd(s2[-1], [[2],[5],[10]], [1,-2,1], end_fwd_start = 10, interval = 1, fixed_leg_freq = 0).rate

quick_swap(s2[-1],5,5)
#print(swap.fixedDayCount().name())
#print([dt.ISO() for dt in swap.fixedSchedule()])
#print(swap.floatingDayCount().name())
#print([dt.ISO() for dt in swap.floatingSchedule()])


s3=[]
t0 = time.time()
s3 = [Swap_Pricer( [[s2[i],2,2]  for i in np.arange(len(s2))]).rate ]
t1 = time.time()
t1-t0


s3=[]
t0 = time.time()
s3 = [quick_swap( [[s2[i],2,2]] ) for i in np.arange(len(s2))]
t1 = time.time()
t1-t0

t10 = time.time()
s4 = [[s2[i] ,2,2] for i in np.arange(len(s2))]
s3=[]
s3 = quick_swap(s4)
t11 = time.time()
t11-t10


plt.plot([ ql_to_datetime(s2[i].ref_date) for i in np.arange(len(s2))],s3)
plt.xticks( rotation=90)
plt.show()


a5=quick_swap( [[s2[-1],2,2],[s2[-1],5,5]] )
(100*np.diff(np.array(a5))).tolist()

[np.round(np.dot(np.array(a5),np.array([-100,100])),3)]


quick_swap( [[s2[-1],0,2],[s2[-1],0,5]], spread=1 )
quick_swap( [[s2[-1],0,5],[s2[-1],0,10]], spread=1 )

quick_swap( [[s2[-1],0,2],[s2[-1],0,5], [s2[-1],0,10]], fly=1 )

Swap_Pricer([[s2[-1],0,2],[s2[-1],0,5], [s2[-1],0,10]]).table


c_usd.curncy
c_usd = ccy('SOFR_DC', today)
df1 = c_usd.hist

sofr_d1 = ois_dc_build('SOFR_DC', b='18-10-2023')

hist['Ref_Date'].tolist().index(ql_to_datetime(ql.Date(18,10,2023)))
sofr_d2 = ois_from_nodes(hist.iloc[6727],c_usd)



sofr_d1.trade_date
sofr_d2.trade_date

sofr_d1.ref_date
sofr_d2.ref_date

sofr_d1.ref_fix
sofr_d2.ref_fix

sofr_d1.curve
sofr_d2.curve

sofr_d1.nodes
sofr_d2.nodes

sofr_d1.rates
sofr_d2.rates

sofr_d1.table
sofr_d2.table

sofr_d1.cal
sofr_d2.cal

sofr_d1.index
sofr_d2.index

sofr_d1.ois_index
sofr_d2.ois_index

sofr_d1.fixing
sofr_d2.fixing

sofr_d1.ois_trigger
sofr_d2.ois_trigger

sofr_d1.ccy
sofr_d2.ccy

sofr_d1.bbgplot_tickers
sofr_d2.bbgplot_tickers








#fail
#len(fail)
#np.mean([fail[i][2] for i in np.arange(len(fail)) if fail[i][2] > 0.1])
#len([fail[i][2] for i in np.arange(len(fail)) if fail[i][2] > 0.1])

#c = ccy('SOFR_DC', today)
#100*a.curve[0].forwardRate( c.cal.advance(a.ref_date, ql.Period('1Y')), c.cal.advance(c.cal.advance(a.ref_date, ql.Period('1Y')), ql.Period('1Y')), ql.Actual360(), ql.Compounded).rate()
#100*a.curve[0].forwardRate( a.ref_date, c.cal.advance(a.ref_date, ql.Period('1Y')), ql.Actual360(), ql.Simple).rate()

#100*ql.MakeVanillaSwap(ql.Period('20Y'), ql.IborIndex(c.fixing, c.fixing_tenor, c.sett_d, c.curncy, c.cal, ql.ModifiedFollowing, True, c.floating[1], ql.YieldTermStructureHandle(a.curve[0])),
#                   0.0, ql.Period('0Y'),
#                   pricingEngine=ql.DiscountingSwapEngine(ql.YieldTermStructureHandle(a.curve[0])),
#                   settlementDays=2).fairRate()

#Swap_Pricer([[a, 1, 1]]).rate[0]
#Swap_Pricer([[a, 0, 20]]).rate[0]


#time1 = time.time()
#r1 = []
#for i in np.arange(100):
#    a = libor_from_nodes(df_source.iloc[i], ois_hist)
#    r1.append( [df_source.iloc[i].name, Swap_Pricer([[a, 0, 20]]).rate[0] ] )
#time2 = time.time()
#print('time_taken:', time2-time1)

#time1 = time.time()
#r1 = [ [df_source.iloc[i].name, Swap_Pricer([[libor_from_nodes(df_source.iloc[i], ois_hist), 0, 20]]).rate[0]] for i in np.arange(100)]
#time2 = time.time()
#print('time_taken:', time2 - time1)


#def get_2y_swap_rate(crv):
#    sw1 = Swap_Pricer([[crv, 0, 2]])
#    return sw1.rate[0]

#time1 = time.time()
#crv = [libor_from_nodes(df_source.iloc[i], ois_hist) for i in np.arange(100)]
#time2 = time.time()
#print('time_taken:', time2 - time1)

# concurrent api calls
#with concurrent.futures.ThreadPoolExecutor(8) as executor:
#    yields = executor.map(get_2y_swap_rate, crv)
#strike_yield = list(yields)


#df_sofr = pd.read_pickle("./DataLake/SOFR_H.pkl")

#time1 = time.time()
#crv = [ois_from_nodes(df_sofr.iloc[i], ccy('SOFR_DC',today)) for i in np.arange(100)]
#time2 = time.time()
#print('time_taken:', time2 - time1)

#time1 = time.time()
#crv = [swap_build('EUR_6M',b=int(-i)) for i in np.arange(100)]
#time2 = time.time()
#print('time_taken:', time2 - time1)


#from functools import reduce

#sofr_live = ois_dc_build('SOFR_DC')
#f1 = Swap_Pricer([[sofr_live, 0, 5],[sofr_live, 0, 10]]).rate
#f2 = Swap_Pricer([[sofr_live, 2, 1],[sofr_live, 3, 1],[sofr_live, 4, 1]]).rate
#np.mean(f2)
#geometric_mean(f2)
#geometric_mean2(f2)

#Swap_Pricer([[sofr_live, 5, 5]]).rate

#def geometric_mean(g):
#    g1 = [ 1+(g[i]/100) for i in np.arange(len(g))]
#    g2 = reduce(lambda x, y: x * y, g1)
#    g3 = 100*((g2**(1/len(g)))-1)
#    return g3

#def geometric_mean2(g):
#    g1 = reduce(lambda x, y: x * y, g)
#    g2 = g1**(1/len(g))
#    return g2

#2*f1[1]-f1[0]
#(f1[1]**2)/f1[0]
######################################## plotting functions ######################################################

crv_list = ['SONIA_DC','ESTER_DC']
hist2 =  dict([(key, []) for key in crv_list])
#hist3 =  dict([(key, []) for key in crv_list])

for k in crv_list:
    for i in np.arange(len(hist[k])):
        hist[k]['Swap_Rates'][i].set_index('Tenor', inplace=True)
        hist[k]['Fwd_Rates'][i].set_index('Fwd', inplace=True)

#### if we need to go back to separate dataframes for par / fwds
#    hist2[k] = pd.concat( [hist[k]['Swap_Rates'][i] for i in np.arange(len(hist[k])) ], axis=1)
#    hist2[k].columns = hist[k].index
#    hist3[k] = pd.concat( [hist[k]['Fwd_Rates'][i] for i in np.arange(len(hist[k])) ], axis=1)['Rate']
#    hist3[k].columns = hist[k].index

    df1 = pd.concat( [hist[k]['Swap_Rates'][i] for i in np.arange(len(hist[k])) ], axis=1)
    df1.columns = hist[k].index
    df2 = pd.concat( [hist[k]['Fwd_Rates'][i] for i in np.arange(len(hist[k])) ], axis=1)['Rate']
    df2.columns = hist[k].index
    hist2[k] = pd.concat([df1,df2])



len(hist2['SONIA_DC'])
len(hist2['SONIA_DC'].columns)

hist2['SONIA_DC'].loc['2Y']['16/02/2024':]
list( map(hist2.get, crv_list) )[1].loc['2Y']
hist3['ESTER_DC'].loc['1y.1y']['16/02/2024':]

time1 = time.time()
for k in crv_list:
    print(hist2[k].loc[['2Y','5Y','1y.1y']].T)
#    print(hist3[k].loc[['1y.1y','2y.1y']].T)
time2 = time.time()
print('time_taken:', time2 - time1)

hist2[k].loc[list(hist2[k].loc['2y.1y':'5y.1y',:].T)+['5Y']].T


f1 = ['2y', '10y']
f1 = ['2y.2y','5y.5y']
f1 = ['10y', '2y.2y']
f2=[]

for i in f1:
    if '.' in i:
        g1 = i.split('.')
        f2.append([ str(int(g1[0][0])+j)+'y.'+'1y' for j in np.arange(int(g1[1][0])) ])
    else:
        f2.append(i.upper())

for i,j in enumerate(f2):
    if isinstance(j, list):
        if f1[i] not in list(hist2['SONIA_DC'].index):
            hist2['SONIA_DC'].loc[f1[i]] = list(hist2['SONIA_DC'].loc[f2[1]].T.mean(axis=1).T)
        else:
            print('already generated')
    else:
        print('spot')




hist2['SONIA_DC'].loc[f2[1]].T.mean(axis=1)
list(hist2['SONIA_DC'].loc[f2[1]].T.mean(axis=1))

hist['ESTER_DC']['Table'].iloc[0]


##### convention utility

def hist(a):
    if a == 'USD_3M':
        batch_trigger = 0
    elif a == 'USD_6M':
        batch_trigger = 0
    elif a == 'EUR_3M':
        batch_trigger = 0
    elif a == 'EUR_6M':
        batch_trigger = 0
    elif a == 'GBP_3M':
        batch_trigger = 0
    elif a == 'GBP_6M':
        batch_trigger = 0
    elif a == 'CHF_3M':
        batch_trigger = 0
    elif a == 'CHF_3M':
        batch_trigger = 0
    elif a == 'JPY_6M':
        batch_trigger = 0
    elif a == 'AUD_3M':
        batch_trigger = 0
    elif a == 'AUD_6M':
        batch_trigger = 0
    elif a == 'CAD_3M':
        batch_trigger = 0
    elif a == 'NZD_3M':
        batch_trigger = 0
    elif a == 'KRW_3M':
        batch_trigger = 0
    elif a == 'SEK_3M':
        batch_trigger = 0
    elif a == 'NOK_3M':
        batch_trigger = 0
    elif a == 'NOK_6M':
        batch_trigger = 0
    elif a == 'PLN_3M':
        batch_trigger = 0
    elif a == 'PLN_6M':
        batch_trigger = 0
    elif a == 'CZK_3M':
        batch_trigger = 0
    elif a == 'CZK_6M':
        batch_trigger = 0
    elif a == 'HUF_3M':
        batch_trigger = 0
    elif a == 'HUF_6M':
        batch_trigger = 0
    elif a == 'ZAR_3M':
        batch_trigger = 0
    elif a == 'ILS_3M':
        batch_trigger = 0
    elif a == 'RUB_3M':
        batch_trigger = 0
    elif a == 'HUF_3M':
        batch_trigger = 0
    elif a == 'MXN_TIIE':
        batch_trigger = 0
    elif a == 'SOFR_DC':
        batch_trigger = 1
        batch_hist = pd.read_pickle("./DataLake/SOFR_H.pkl")
    elif a == 'FED_DC':
        batch_trigger = 0
    elif a == 'EONIA_DC':
        batch_trigger = 0
    elif a == 'ESTER_DC':
        batch_trigger = 0
    elif a == 'SONIA_DC':
        batch_trigger = 0
    elif a == 'AONIA_DC':
        batch_trigger = 0
    elif a == 'NZD_OIS_DC':
        batch_trigger = 0
    elif a == 'CAD_OIS_DC':
        batch_trigger = 0
    elif a == 'CHF_OIS_DC':
        batch_trigger = 0
    elif a == 'SEK_OIS_DC':
        batch_trigger = 0
    elif a == 'TONAR_DC':
        batch_trigger = 0
    elif a == 'COP_OIS_DC':
        batch_trigger = 0
    elif a == 'RUONIA_DC':
        batch_trigger = 0

    class hist_dict:
        def __init__(self):
            if batch_trigger == 1:
                self.hist = batch_hist
            else:
                print('no history...')

    return hist_dict()
