

#c_list = ['USD_3M','USD_6M','EUR_6M','EUR_3M','GBP_3M','GBP_6M','CHF_3M','CHF_6M','JPY_6M','AUD_3M','AUD_6M','CAD_3M','NZD_3M',
#          'KRW_3M','SEK_3M','NOK_3M','NOK_6M','PLN_3M','PLN_6M','CZK_3M','CZK_6M','HUF_3M','HUF_6M','ZAR_3M','ILS_3M','RUB_3M','MXN_TIIE',
#          'EONIA_DC','ESTER_DC','SOFR_DC','SONIA_DC','AONIA_DC','FED_DC','NZD_OIS_DC','CHF_OIS_DC','SEK_OIS_DC','TONAR_DC','RUONIA_DC','COP_OIS_DC','CAD_OIS_DC']

#today = ql.Date(datetime.datetime.now().day,datetime.datetime.now().month,datetime.datetime.now().year)
import QuantLib as ql

sofr_1 = ql.DiscountCurve(ql.Date(2, 2, 2023), 0.2, ql.Actual365Fixed(), ql.TARGET())

#for i in c_list:
#    print(i,':')
#    a = ccy(i,today)
#    print(a.ois_trigger, a.fixing, a.curncy)

#'EONIA_DC'
#'FED_DC'

#c_list = ['CAD_OIS_DC','ESTER_DC','SOFR_DC','SONIA_DC','AONIA_DC','NZD_OIS_DC','CHF_OIS_DC','SEK_OIS_DC','TONAR_DC','RUONIA_DC','COP_OIS_DC']

#for i in c_list:
#    print(i,':')
#    a = ois_dc_build(i,0)
#    print(a.ref_date, a.ref_fix, a.rates)

'''
'GBP_3M' --- no tickers
'GBP_6M' --- no tickers
'CHF_3M','CHF_6M'  --- no tickers
'JPY_6M'  --- no tickers
'CAD_3M'  --- no tickers
'NOK_6M'  --- roots in curve constr
'PLN_3M'  --- tickers dont update intraday
'''
import QuantLib

#c_list = ['USD_3M','USD_6M','EUR_6M','EUR_3M', 'AUD_3M','AUD_6M', 'NZD_3M',
#          'KRW_3M','SEK_3M','NOK_3M','PLN_6M','CZK_3M','CZK_6M','HUF_3M','HUF_6M','ZAR_3M','ILS_3M','RUB_3M','MXN_TIIE']

#for i in c_list:
#    print(i,':')
#    a = swap_build(i,0)
#    print(a.ref_date, a.ref_fix, a.rates)


today = ql.Date(datetime.datetime.now().day,datetime.datetime.now().month,datetime.datetime.now().year)
#a = ois_dc_build('SOFR_DC',0)
#a2 = swap_table(a,[-1])

#a2.table

#curve_hmap(['SOFR_DC'], ois_flag=1)


#c1_list = ['FRCPI','HICPxT','UKRPI','USCPI','CACPI']

#for i in c1_list:
#    print(i,':')
#    a = ccy_infl(i,today)
#    print(a.index, a.base_month, a.ticker, a.last_fix_month, a.fixing_hist)

a=ccy_infl('HICPxT',today)

a3=a.fixing_hist

#a = pd.read_pickle('./DataLake/HICPxT_hist.pkl')
#a = pd.read_pickle('./DataLake/UKRPI_hist.pkl")


#os.getcwd()

#for i in c1_list:
#    print(i,':')
#    a = infl_zc_swap_build(i,0)
#    print(a.index, a.base_month, a.base_index, a.rates, a.last_pm)

#xt = infl_zc_swap_build('HICPxT',0)


a = bond_curve_build(['ITALY_NOM'], [0], ['1m'], 2.55, 2.75)

#    db_srch = ['ITALY_NOM']
#    db_srch = ['SWEDEN_NOM']
#    d1 = [0, '04-01-2022']
#    repo_rate = 0
#    fwd_repo_rate = 0
#    fwd_d = ['1m', '3m']


#print(a)

#plt.show()

a2 = pd.DataFrame([2,3,5])




b1 = {'a':1, 'b':2, 'c':3}


import matplotlib
import matplotlib.pyplot as plt

matplotlib.get_backend()
plt.interactive(False)


from matplotlib import pyplot as plt

plt.figure(1)
plt.scatter(1,2)
plt.show()


plt.figure(2)
plt.scatter(0,2)
plt.show()




plt.figure(1)
plt.show()





################### Saving curve nodes:

sofr = ois_dc_build('SOFR_DC')

n1 = sofr.nodes

sofr_db = pd.DataFrame()
dates = [datetime.datetime(n1[i][0].year(), n1[i][0].month(), n1[i][0].dayOfMonth()) for i in range(len(n1))]
rates = [n1[i][1] for i in range(len(n1))]
#sofr_db[sofr.trade_date] = zip(dates, rates)

sofr_db['dates'] = [datetime.datetime(n1[i][0].year(), n1[i][0].month(), n1[i][0].dayOfMonth()) for i in range(len(n1))]
sofr_db['rates'] = [n1[i][1] for i in range(len(n1))]

sofr_db.to_pickle('SOFR_1.pkl')

sofr_1 = pd.read_pickle("./SOFR_1.pkl")

q_dates = [datetime_to_ql(sofr_db['dates'][i]) for i in np.arange(len(sofr_1))]
l_rates = sofr_db['rates'].tolist()

sofr_1 = ql.MonotonicLogCubicDiscountCurve(q_dates, l_rates, ql.Actual360(), ql.UnitedStates(ql.UnitedStates.FederalReserve))


d17 = [ql.Date(25,5,1997) + ql.Period(int(i), ql.Years) for i in np.arange(30)]

[(100*(sofr.curve.forwardRate(d17[i], ql.UnitedStates(ql.UnitedStates.FederalReserve).advance(d17[i],1,ql.Years),
                              ql.Actual360(), ql.Simple).rate() - sofr_1.forwardRate(d17[i],
        ql.UnitedStates(ql.UnitedStates.FederalReserve).advance(d17[i],1,ql.Years), ql.Actual360(), ql.Simple).rate())) for i in np.arange(len(d17))]


[100*(sofr.curve.forwardRate(d17[i], ql.UnitedStates(ql.UnitedStates.FederalReserve).advance(d17[i],1,ql.Years), ql.Actual360(), ql.Simple).rate()) for i in np.arange(len(d17)) ]
[100*(sofr_1.forwardRate(d17[i], ql.UnitedStates(ql.UnitedStates.FederalReserve).advance(d17[i],1,ql.Years), ql.Actual360(), ql.Simple).rate()) for i in np.arange(len(d17)) ]



Swap_Pricer([[sofr, 5,5]], fixed_leg_freq = 0).rate

Swap_Pricer([[sofr_1, 5,5]], fixed_leg_freq = 0).rate


sofr_1.discount(ql.Date(25,8,2023))
sofr.curve.discount(ql.Date(25,8,2023))


c1 = ois_dc_build('EUR_3M', b=0)
c1.table

c1 = ois_dc_build('SEK_OIS_DC', b=0)
c1.table

c1 = swap_build('AUD_3M', b='15-02-2016')
c1.stir_rates




#########################

data = pd.ExcelFile("./DataLake/query-usd-ois.csv")
data_df = pd.read_excel(data,"EcoData")


df = pd.read_csv("./DataLake/query-usd-ois.csv")

type(df['Date'][0])














































