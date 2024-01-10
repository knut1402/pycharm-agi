##### batch ois
import QuantLib
import pandas as pd

## 1. usd ois from jpm data query

df_usd = pd.read_csv("./DataLake/query-usd-ois.csv")
#df_usd = df_usd[-100:]
#df_usd.reset_index(inplace=True, drop=True)

today = ql.Date(datetime.datetime.now().day, datetime.datetime.now().month, datetime.datetime.now().year)
a = 'SOFR_DC'
c = ccy(a, today)
TU_Dict = {'D': 0, 'W': 1, 'M': 2, 'Y': 3}

sofr_db = pd.DataFrame()
sofr_db.index = df_usd['Date']

r_index = []
r_ref_date = []
r_dates = []
r_rates = []
r_fixing = []
r_tab = []
r_swap_rates = []

i=0
for i in np.arange(len(df_usd)):
    b= df_usd['Date'][i]
    print(b)
    ref_date = ql.Date(int(b.split('/')[0]), int(b.split('/')[1]), int(b.split('/')[2]))
    ref_date_1 = c.cal.advance(ref_date, -1, ql.Days)
    ql.Settings.instance().evaluationDate = ref_date

#### get o/n ois fixing
    OIS_ON = df_usd['1d'][i]
    deposits = {(0, 1, ql.Days): OIS_ON}
    for sett_num, n, unit in deposits.keys():
        deposits[(sett_num, n, unit)] = ql.SimpleQuote(
            deposits[(sett_num, n, unit)] / 100.0)

    helpers = [ ql.DepositRateHelper(
        ql.QuoteHandle(deposits[(sett_num, n, unit)]),
        ql.Period(n, unit),
        2,
        c.cal,
        ql.Following,
        False,
        c.floating[1],
            )
            for sett_num, n, unit in deposits.keys()]

    OIS_DC = c.index_a

#### get ois swap rates
    x1 = pd.DataFrame()
    x1['Tenor'] = [df_usd.columns[k].upper() for k in np.arange(2,len(df_usd.columns))]
    x1['Rate'] = [df_usd.iloc[i,j] for j in np.arange(2,len(df_usd.columns))]

    x1['TenorNum'] = pd.Series([int(x1['Tenor'][i][0:-1]) for i in range(len(x1))])
    x1['TenorUnit'] = pd.Series(dtype=float)
    x1['TenorUnit'] = [TU_Dict[x1['Tenor'].tolist()[i][-1]] for i in range(len(x1))]
    x1['List'] = [(x1['Rate'][i], (int(x1['TenorNum'][i]), int(x1['TenorUnit'][i]))) for i in range(len(x1))]
    L1 = x1['List'].tolist()

    helpers += [ql.OISRateHelper(c.sett_d, ql.Period(*tenor),
                                 ql.QuoteHandle(ql.SimpleQuote(rate / 100)), OIS_DC)
                for rate, tenor in L1]

# build curve
    OIS_DC_curve = ql.PiecewiseLogCubicDiscount(c.sett_d, c.cal, helpers, c.floating[1] )
    OIS_DC_curve.enableExtrapolation()

    n1 = OIS_DC_curve.nodes()
    r_index.append(a)
    r_fixing.append(OIS_ON)
    r_ref_date.append(ql_to_datetime(ref_date))
    r_tab.append(x1)
    r_swap_rates.append(x1[x1['TenorUnit']==3][['Tenor','Rate']].reset_index(drop=True))
    r_dates.append([datetime.datetime(n1[j][0].year(), n1[j][0].month(), n1[j][0].dayOfMonth()) for j in range(len(n1))])
    r_rates.append([n1[k][1] for k in range(len(n1))])

sofr_db['Ref_Date'] = r_ref_date
sofr_db['Dates'] = r_dates
sofr_db['Rates'] = r_rates
sofr_db['Swap_Rates'] = r_swap_rates
sofr_db['Index'] = r_index
sofr_db['Fixing'] = r_fixing
sofr_db['Table'] = r_tab

### testing only!
#sofr_db.to_pickle('SOFR_1.pkl')
#sofr_1 = pd.read_pickle("SOFR_1.pkl")


sofr_db.to_pickle('./DataLake/SOFR_H.pkl')
sofr_h = pd.read_pickle("./DataLake/SOFR_H.pkl")

sofr_live = ois_dc_build('SOFR_DC', b=0)

def ois_from_nodes(a,b):
#    a = sofr_h.iloc[9]
#    b = a['Index']

    today = ql.Date(datetime.datetime.now().day, datetime.datetime.now().month, datetime.datetime.now().year)
    c = ccy(b, today)
    d1 = a.name

    trade_date = ql.Date(int(d1.split('/')[0]), int(d1.split('/')[1]), int(d1.split('/')[2]))
    ref_date = c.cal.advance(trade_date,2,ql.Days)
    ref_fix = a['Fixing']
    tab = a['Table']
    swap_rates = a['Swap_Rates']
    swap_rates.columns = ['Tenor','SwapRate']
    curve_ccy = 'USD'

    q_dates = [datetime_to_ql(a['Dates'][j]) for j in np.arange(len(a['Dates']))]
    l_rates = a['Rates']

    ois_curve = ql.MonotonicLogCubicDiscountCurve(q_dates, l_rates, ql.Actual360(), ql.UnitedStates(ql.UnitedStates.FederalReserve))

    class ois_from_nodes():
        def __init__(self):
            self.trade_date = trade_date
            self.ref_date = ref_date
            self.ref_fix = ref_fix
            self.table = tab
            self.rates = swap_rates
            self.curve = ois_curve
            self.cal = c.cal
            self.index = c.index
            self.ois_index = b
            self.fixing = c.fixing
            self.ois_trigger = c.ois_trigger
            self.ccy = curve_ccy
    return ois_from_nodes()

def ois_from_hist(a, d1=0, d2=0):
    a = sofr_h
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
            start = -1*sum(a['Ref_Date'] > ql_to_datetime(d11))+len(a.index)
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
            start = -1*sum(a['Ref_Date'] > ql_to_datetime(d12))+len(a.index)

    if isinstance(d2, int) == True:
        end = len(a.index)+d2
    if isinstance(d2, str) == True:
        try:
            d21 = ql.Date(int(d2.split('-')[0]), int(d2.split('-')[1]), int(d2.split('-')[2]))
            end = -1 * sum(a['Ref_Date'] > ql_to_datetime(d21)) + len(a.index)
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
            end = -1 * sum(a['Ref_Date'] > ql_to_datetime(d22)) + len(a.index)

    if end <= start:
        print('Error = Start Date > End Date;')

    s1 = [ois_from_nodes(a.iloc[i], b) for i in np.arange(start,end)]
    return s1


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






