##### eonia discount curve
##### outputs == Table of Rates, plot, reference date, reference fixing, *curve

import pandas as pd
import numpy as np
import datetime
#import tia
#from tia.bbg import LocalTerminal as LT
import pdblp
import QuantLib as ql
import matplotlib as mpl
import matplotlib.pyplot as plt
from Conventions import FUT_CT,FUT_CT_Q, ccy, hist
from Utilities import *

con = pdblp.BCon(debug=False, port=8194, timeout=50000)
con.start()


### Build from batch_hist
def ois_from_nodes(a,conv):
#    a = sofr_h.iloc[9]
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


### Build OIS Curve
def ois_dc_build(a,b=0):
    today = ql.Date(datetime.datetime.now().day,datetime.datetime.now().month,datetime.datetime.now().year)
    from_hist_flag = 0

#    a = 'SOFR_DC'
#    b=0
#    b = '18-10-2023'

    c = ccy(a,today)

    #### date handling for hist 
    if isinstance(b,int) == True:
        ref_date = c.cal.advance(today,b,ql.Days)
    else:
        ref_date = ql.Date(int(b.split('-')[0]),int(b.split('-')[1]),int(b.split('-')[2]))
    
    ref_date_1 = c.cal.advance(ref_date,-1,ql.Days)
    
    ql.Settings.instance().evaluationDate = ref_date
     
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

    ######## BATCH History implementation
    if c.batch_trigger == 1:
        crv_h = hist[a]

    try:
#    if ql_to_datetime(ref_date).strftime('%d/%m/%Y') in crv_h.index:
#        locat = hist(a).hist['Ref_Date'].tolist().index(ql_to_datetime(ref_date))
        output = ois_from_nodes(crv_h.loc[ql_to_datetime(ref_date).strftime('%d/%m/%Y')],c)
        print("*** !!! ois_curve retrieved from hist !!! ***")
        from_hist_flag = 1

    except:
        from_hist_flag = 0
        #### get o/n ois fixing
        try:
            OIS_ON = con.bdh(c.fixing, 'PX_LAST',bbg_t_1,bbg_t_1).iloc[0][0]
        except:
            OIS_ON = con.ref(c.fixing, 'PX_LAST')['value'][0]

        helpers = [ ql.DepositRateHelper(ql.QuoteHandle(ql.SimpleQuote(rate/100)),
                                         ql.Period(fixingDays,ql.Days), 0,
                                         c.cal, ql.Following, False, c.floating[1])
                    for rate, fixingDays in [(OIS_ON,0), (OIS_ON,1), (OIS_ON,2) ]]

        OIS_DC = c.index_a

        #### get ois swap rates
        obj = 'CURVE_TENOR_RATES'
        ticker = c.bbg_curve
        curve_ccy = con.ref(ticker,'CRNCY')['value'][0]
        inst = con.bulkref(ticker, obj)
        #inst
        x1 = inst['value'][inst['name']=='Tenor Ticker']
        x2 = inst['value'][inst['name']=='Tenor']

        #x1
        x1.drop(x1.index[0], inplace = True)
        x1 = x1.reset_index()
        x1.drop(columns= ['index'], inplace = True)

        x2.drop(x2.index[0], inplace = True)
        x2 = x2.reset_index()
        x2.drop(columns= ['index'], inplace = True)

        if a == 'ESTER_DC':                       ######## ESTER BBG Curve defaults to  - note index to get 2y rate explicit @ 15 !
            for i in np.arange(15,len(x1)):
                x1.iloc[i] = 'EESWE'+x2.iloc[i][0][:-1]+' BGN Curncy'

        if a == 'SEK_OIS_DC':                       ######## BGN and CMPN misses historic 2y rates
            for i in np.arange(len(x1)):
                x1.iloc[i] = x1.iloc[i][0].split()[0]+' BLC3 Curncy'

        if a == 'AONIA_DC':                       ######## BGN and CMPN misses historic 2y rates
            for i in np.arange(9,len(x1)):
                x1.iloc[i] = 'ADSO'+x2.iloc[i][0][:-1]+' ICPL Curncy'
        #### ad-hoc 18m ticker
            x1.iloc[8] = 'ADSO1F ICPL Curncy'



        x1['Tenor'] = x2

        if a == 'CAD_OIS_DC':
            x1 = pd.concat([x1[:14],c.add_tenors])
        else:
            x1 = pd.concat([x1,c.add_tenors])
        x1 = x1.reset_index()
        x1.drop(columns= ['index'], inplace = True)

        if a == 'CAD_OIS_DC':
            for i in np.arange(len(x1)):
                x1['value'].iloc[i] = x1['value'].iloc[i].split()[0]+' BLC3 Curncy'

        if a == 'RUONIA_DC':
            for i in np.arange(9,len(x1)):
                x1['value'].iloc[i] = x1['value'].iloc[i].split()[0][:2]+'SO'+str(i-6)+' BLC3 Curncy'

    #    if a == 'AONIA_DC':                       ######## BGN and CMPN misses historic 2y rates
    #        for i in np.arange(len(x1)):
    #            x1['value'].iloc[i] = x1['value'].iloc[i].split()[0]+' CBBT Curncy'


        x3 = con.bdh(x1['value'].tolist(),'PX_LAST',bbg_t,bbg_t, longdata = True)


        x1 = x1.set_index('value').join(x3.set_index('ticker'))
        x1= x1.dropna()
        x1.rename(columns={'value': 'Rate', }, inplace=True)
        x1 = x1.reset_index()
        x1.rename(columns={'value': 'TenorTicker', }, inplace=True)

        #x1
        #i=21
        #con.bdh(x1['value'][i].split()[0]+str(' BGN ')+x1['value'][i].split()[1],'PX_LAST',bbg_t,bbg_t).iloc[0][0]

        #x1['Rate'] = pd.Series([con.bdh(x1['value'][i].split()[0]+str(' BXSW ')+x1['value'][i].split()[1],'PX_LAST',bbg_t,bbg_t).iloc[0][0]
        #                             for i in range(len(x1))  ])
        x1['TenorNum'] = pd.Series([int(x1['Tenor'][i][0:-1]) for i in range(len(x1))])
        x1['TenorUnit'] = pd.Series( dtype=float)

        TU_Dict = {'D': 0, 'W': 1, 'M': 2, 'Y': 3}

        x1['TenorUnit'] = [TU_Dict[x1['Tenor'].tolist()[i][-1]] for i in range(len(x1))]


        x1['List'] = [ (x1['Rate'][i],(int(x1['TenorNum'][i]),int(x1['TenorUnit'][i]))) for i in range(len(x1)) ]
        L1 = x1['List'][1:].tolist()


        ####### 1w, 2w, 3w, 1m helpers only to be used for long lead date to meetign dates
        ############################### Helpers aggregate rate + maturities

        helpers += [ ql.OISRateHelper(c.sett_d, ql.Period(*tenor),
                                      ql.QuoteHandle(ql.SimpleQuote(rate/100)), OIS_DC)
                    for rate, tenor in L1]

        # get eom to last day of month
        end = ref_date + ql.Period(40,ql.Years)

        dates = [ql.Date(serial) for serial in range(ref_date.serialNumber(),end.serialNumber()+1) ]
        dates2 = [c.cal.isEndOfMonth(i) for i in dates ]
        dates3 = [dates[i] for i in range(len(dates)) if dates2[i]==True]
        #dates3

        # get 1st or 2nd of month being a w/e
        dates4 = [c.cal.isWeekend(i.weekday())  for i in dates ]
        dates5 = [dates[i] for i in range(len(dates)) if dates4[i]==True]

        dates6 = [dates5[i] for i in range(len(dates5)) if ( (dates5[i].dayOfMonth() == 1) or (dates5[i].dayOfMonth() == 2) )  ]
        #dates6
        #len(dates6)

        # what is monday after SOM is a holiday
        dates7 = [c.cal.isHoliday(i) for i in dates ]
        dates8 = [dates[i] for i in range(len(dates)) if dates7[i]==True]

        dates9 = [dates8[i] for i in range(len(dates8)) if dates8[i].dayOfMonth() < 4  ]
        dates10 = [dates9[i] for i in range(len(dates9)) if dates9[i].weekday() == 2  ]

        #dates10

        dates11 =  dates6 + dates10
        j_dates = dates3 + dates11

        #j_dates

        OIS_ME = c.eom
        OIS_QE = c.eoq
        OIS_YE = c.eoy


        bumps = []
        for i in range(len(dates3)):
            if dates3[i].month() == 12:
                x = ql.QuoteHandle(ql.SimpleQuote(1/(1+OIS_YE)))
            elif dates3[i].month() % 3 and dates3[i].month()!= 12:
                x = ql.QuoteHandle(ql.SimpleQuote(1/(1+OIS_QE)))
            else :
                x = ql.QuoteHandle(ql.SimpleQuote(1/(1+OIS_ME)))

            bumps.append(x)

        for i in range(len(dates11)):
            if dates11[i].month() == 1:
                x = ql.QuoteHandle(ql.SimpleQuote(1/(1+OIS_YE)))
            elif (dates11[i].month() -1) % 3 and dates11[i].month()!= 1:
                x = ql.QuoteHandle(ql.SimpleQuote(1/(1+OIS_QE)))
            else :
                x = ql.QuoteHandle(ql.SimpleQuote(1/(1+OIS_ME)))

            bumps.append(x)


        OIS_DC_curve = ql.PiecewiseLogCubicDiscount(c.sett_d, c.cal, helpers, c.floating[1] , bumps, j_dates)
        #EONIA_DC_curve = ql.PiecewiseCubicZero(0, ql.TARGET(), helpers, ql.Actual360())
        #EONIA_DC_curve = ql.PiecewiseLogLinearDiscount(0, ql.TARGET(), helpers, ql.Actual360(), ff_jumps, ff_jump_dates)
    #    OIS_DC_curve = ql.PiecewiseFlatForward(c.sett_d, c.cal, helpers, c.floating[1]  , bumps, j_dates)     ############### THIS WORKS FOR SOFR !
        #EONIA_DC_curve = ql.PiecewiseFlatForward(0, ql.TARGET(), helpers, ql.Actual360())
        OIS_DC_curve.enableExtrapolation()


    #    def swap_plot():
    #        d2 = OIS_DC_curve.referenceDate()
    #        d3 = d2 + ql.Period(40,ql.Years)
    #
    #        dates_in = [ ql.Date(serial) for serial in range(d2.serialNumber(),d3.serialNumber()+1) ]
    #
    #        rates_c = [100*OIS_DC_curve.forwardRate(d, c.cal.advance(d,1,ql.Days), c.floating[1], ql.Simple).rate()
    #                for d in dates_in ]
    #        yr_axis = [(dates_in[i]-dates_in[0])/365.25 for i in range(len(dates_in)) ]
    #
    #        plt.plot( yr_axis , rates_c , color = "blue")

    #    fig = swap_plot()
    #    d2 = OIS_DC_curve.referenceDate()
    #    d3 = d2 + ql.Period(3,ql.Months)

    #    dates_in = [ ql.Date(serial) for serial in range(d2.serialNumber(),d3.serialNumber()+1) ]

    #    rates_c_simple = [100*OIS_DC_curve.forwardRate(d, c.cal.advance(d,1,ql.Days), c.floating[1], ql.Simple).rate() for d in dates_in ]
    #    rates_c_compd = [100*OIS_DC_curve.forwardRate(d, c.cal.advance(d,1,ql.Days), c.floating[1], ql.Compounded).rate() for d in dates_in ]

    #    np.array(rates_c_compd) - np.array(rates_c_simple)

    ################# REPRICING STRIP
    #    100-100*OIS_DC_curve.forwardRate(ql.Date(15,12,2021), c.cal.advance(ql.Date(15,12,2021),3,ql.Months), c.floating[1], ql.Simple).rate()
    #    100-100*OIS_DC_curve.forwardRate(ql.Date(14,3,2022), c.cal.advance(ql.Date(14,3,2022),3,ql.Months), c.floating[1], ql.Simple).rate()
    #    100-100*OIS_DC_curve.forwardRate(ql.Date(20,6,2022), c.cal.advance(ql.Date(20,6,2022),3,ql.Months), c.floating[1], ql.Simple).rate()
    #    100-100*OIS_DC_curve.forwardRate(ql.Date(20,9,2022), c.cal.advance(ql.Date(20,9,2022),3,ql.Months), c.floating[1], ql.Simple).rate()
    #    100-100*OIS_DC_curve.forwardRate(ql.Date(14,12,2022), c.cal.advance(ql.Date(14,12,2022),3,ql.Months), c.floating[1], ql.Simple).rate()
    #    100-100*OIS_DC_curve.forwardRate(ql.Date(20,3,2023), c.cal.advance(ql.Date(20,3,2023),3,ql.Months), c.floating[1], ql.Simple).rate()
    #   100-100*OIS_DC_curve.forwardRate(ql.Date(19,6,2023), c.cal.advance(ql.Date(19,6,2023),3,ql.Months), c.floating[1], ql.Simple).rate()
    #    100-100*OIS_DC_curve.forwardRate(ql.Date(19,9,2023), c.cal.advance(ql.Date(19,9,2023),3,ql.Months), c.floating[1], ql.Simple).rate()
    #    100-100*OIS_DC_curve.forwardRate(ql.Date(19,12,2023), c.cal.advance(ql.Date(19,12,2023),3,ql.Months), c.floating[1], ql.Simple).rate()
    #    100-100*OIS_DC_curve.forwardRate(ql.Date(18,3,2024), c.cal.advance(ql.Date(18,3,2024),3,ql.Months), c.floating[1], ql.Simple).rate()



    ##### outputs     ===========         NEED TO GET RID OF THIS !!!!!!!         ==============
        x4 = con.bdh(x1['TenorTicker'].tolist(),'PX_LAST',bbg_t_1,bbg_t_1, longdata = True)

        x4 = x4.drop(['date', 'field'], axis=1)
        x1 = x1.set_index('TenorTicker').join(x4.set_index('ticker'))
        #x1= x1.dropna()
        x1.rename(columns={'value': 'Rate_1D', }, inplace=True)
        x1 = x1.reset_index()
        x1.rename(columns={'value': 'TenorTicker', }, inplace=True)
        x1['Chg_1d'] = 100*(x1['Rate']-x1['Rate_1D'])

        rates_tab_2y_index = x1[x1['Tenor'] == '2Y'].index[0]
        rates_tab = x1[['Tenor','Rate']][rates_tab_2y_index:]
        rates_tab = rates_tab.reset_index(drop=True)
        rates_tab.columns = ['Tenor','SwapRate']

        print("*** !!! ois_curve built !!! ***")

    class ois_build_output():
            def __init__(self):
                if from_hist_flag == 1:
                    self.tab = output.tab
                    self.ref_date = output.ref_date
                    self.ref_fix = output.ref_fix
                    self.trade_date = output.trade_date
                    self.curve = output.curve
                    self.nodes = output.nodes
                    self.rates = output.rates
                    self.table = output.table
                    self.cal = c.cal
                    self.index = c.index
                    self.ois_index = output.ois_index
                    self.fixing = c.fixing
                    self.ois_trigger = c.ois_trigger
                    self.ccy = output.ccy
                    self.bbgplot_tickers = c.bbgplot_tickers

                else:
                    self.tab = x1[['Tenor','Rate','Chg_1d']]
                    self.ref_date = OIS_DC_curve.referenceDate()
                    self.ref_fix = OIS_ON
                    self.trade_date = ref_date
                    self.curve = OIS_DC_curve
                    self.nodes = OIS_DC_curve.nodes()
                    self.rates = rates_tab
                    self.table = x1
                    self.cal = c.cal
                    self.index = c.index
                    self.ois_index = a
                    self.fixing = c.fixing
                    self.ois_trigger = c.ois_trigger
                    self.ccy = curve_ccy
                    self.bbgplot_tickers = c.bbgplot_tickers
                
    return ois_build_output()

#t1 = time.time()
#s1=ois_dc_build('SOFR_DC', b=0)
#t2 = time.time()
#print(t2-t1)

#t1 = time.time()
#crv_h = hist('SOFR_DC')
#t2 = time.time()
#print(t2-t1)

#t1 = time.time()
#s2=ois_dc_build('SOFR_DC', b='18-10-2023')
#t2 = time.time()
#print(t2-t1)



###### Get short end step pricing
def get_wirp(a):
#    a = [['SOFR_DC'], [datetime.date(2024, 2, 19), datetime.date(2024, 1, 8)]]
    today = ql.Date(datetime.datetime.now().day, datetime.datetime.now().month, datetime.datetime.now().year)
    d = a[1]
    print(d)
    df_l = dict([(key, []) for key in a[0]])
    x5 = dict([(key, []) for key in a[0]])

    for j in a[0]:
#        j = 'SOFR_DC'
        c = ccy(j, today)
        ticker = c.bbgplot_tickers[2]
        contrib = c.contrib[0]
        n_meets = c.contrib[1]
        base_ticker = c.base_ticker

        for i in np.arange(len(d)):
#            i = 0
            d1 = c.cal.advance(datetime_to_ql(d[i]), ql.Period('0D'))
            ### Get bbg tickers
            if c.curncy == ql.USDCurrency():
                t_list = [ticker+str(i)+' '+contrib+' Curncy' for i in range(1,n_meets) ]
            elif c.curncy == ql.EURCurrency() or c.curncy == ql.GBPCurrency():
                t_list = [ticker + str(i) + 'A ' + contrib + ' Curncy' for i in range(1, n_meets)]

            df1 = con.bdh(t_list, 'PX_LAST', bbg_date_str(d1), bbg_date_str(d1), longdata=True)
            df1.ticker = df1.ticker.astype("category")
            df1.ticker = df1.ticker.cat.set_categories(t_list)
            df1 = df1.sort_values(["ticker"])
            df1.reset_index(inplace=True, drop=True)

            ### Get FOMC Dates and set index
            if d1 == today:
                x = con.bulkref(base_ticker,'ECO_FUTURE_RELEASE_DATE_LIST')['value']
            else:
                x = con.bulkref(base_ticker,'ECO_FUTURE_RELEASE_DATE_LIST', ovrds=[("START_DT",bbg_date_str(d1)), ("END_DT",bbg_date_str(c.cal.advance(d1, ql.Period('2Y'))))])['value']

            x1 = np.array([ datetime.datetime.strptime(x[i], '%Y/%m/%d %H:%M:%S').date() for i in np.arange(len(x))])
            intra_meet_length = np.mean(np.diff(x1)).days
            x2 = list(x1[np.array([ x1[i] < ql_to_datetime(today) for i in np.arange(len(x1)) ])])
            x3 = [bbg_date_str( datetime_to_ql(x2[i])) for i in np.arange(len(x2))]

            y = pd.Series([ pd.datetime(int(x[i][0:4]),int(x[i][5:7]),int(x[i][8:10])) for i in range(len(x)) ])
            y = pd.DataFrame(y[y > (datetime.datetime.combine(d[i], datetime.datetime.min.time())+pd.DateOffset(days=-1))  ], columns = ['Meets'])    ##### future meetings
            if len(y) == len(t_list):
                meet_index = pd.Series([y.iloc[i,][0].strftime('%b') + '-' + y.iloc[i,][0].strftime('%y') for i in range(len((y)))])
            else:
                y1 = y['Meets'].append( pd.Series([ y[-1:]['Meets'].values[0]+np.timedelta64(45*i,'D') for i in range(1, len(t_list)-len(y)+1 )] ) )   ##### generate own future fomc dates
                y2 = pd.DataFrame(y1)
                meet_index = pd.Series( [y2.iloc[i,][0].strftime('%b') +'-'+ y2.iloc[i,][0].strftime('%y') for i in range(len((y2))) ] )
            try:
                x4 = con.ref_hist(base_ticker, 'PX_LAST', dates=x3)['value']
                x5[j] = [(meet_index[i], x4[i]) for i in np.arange(len(x4))]
            except:
                x5[j] = []

            df1['meet_date'] = meet_index
#            print('preparing dict:', df1)
            ois_fix = con.bdh(c.fixing, 'PX_LAST', bbg_date_str(c.cal.advance(d1, ql.Period('-2D'))), bbg_date_str(c.cal.advance(d1, ql.Period('-2D'))), longdata=True)['value'][0]
            base_fix = con.bdh(base_ticker, 'PX_LAST', bbg_date_str(c.cal.advance(d1, ql.Period('-2D'))), bbg_date_str(c.cal.advance(d1, ql.Period('-2D'))), longdata=True)['value'][0]
            x5[j].append(('base',base_fix))
            basis = base_fix - ois_fix
            df1['cb'] = np.round(df1['value']+basis,2)
            df1['step'] = 100 * np.array([df1['cb'][0] - base_fix] + df1['cb'].diff()[1:].tolist())
            df1['cum'] = df1['step'].cumsum()
            df_l[j].append(df1.loc[:,['meet_date','cb','step','cum']])
#            print(df_l)

    return [df_l, x5]

#dt = get_wirp( [['SOFR_DC','SONIA_DC'], [datetime.date(2024, 2, 7), datetime.date(2023, 10, 18)]] )
#dt = get_wirp( [['SOFR_DC','SONIA_DC'], [datetime.date(2024, 2, 7)]] )
#dt = get_wirp( [['SOFR_DC'], [datetime.date(2024, 2, 7),datetime.date(2024, 1, 5),datetime.date(2023, 10, 18)]] )

def get_wirp_hist(a):
#    a = 'SOFR_DC'

    today = ql.Date(datetime.datetime.now().day, datetime.datetime.now().month, datetime.datetime.now().year)
    c = ccy(a,today)
    ticker = c.bbgplot_tickers[2]
    contrib = c.contrib[0]
    n_meets = c.contrib[1]
    base_ticker = c.base_ticker
    d_start = c.cal.advance(today, ql.Period('-2Y'))

    if c.curncy == ql.USDCurrency():
        t_list = [ticker + str(i) + ' ' + contrib + ' Curncy' for i in range(1, n_meets)]
    elif c.curncy == ql.EURCurrency() or c.curncy == ql.GBPCurrency():
        t_list = [ticker + str(i) + 'A ' + contrib + ' Curncy' for i in range(1, n_meets)]

    df1 = con.bdh(t_list, 'PX_LAST', bbg_date_str(d_start), bbg_date_str(today), longdata=True)

    if c.curncy == ql.USDCurrency():
        df1['meet_num'] = [int(df1['ticker'][i].split()[0][len(ticker):]) for i in np.arange(len(df1))]
    elif c.curncy == ql.EURCurrency() or c.curncy == ql.GBPCurrency():
        df1['meet_num'] = [int(df1['ticker'][i].split()[0][len(ticker):-1]) for i in np.arange(len(df1))]

    x = con.bulkref(base_ticker, 'ECO_FUTURE_RELEASE_DATE_LIST', ovrds=[("START_DT", bbg_date_str(d_start)), ("END_DT", bbg_date_str(c.cal.advance(d_start, ql.Period('4Y'))))])['value']
    y = pd.Series([pd.datetime(int(x[i][0:4]), int(x[i][5:7]), int(x[i][8:10])) for i in range(len(x))])
    z = pd.Series([y[i].date() for i in np.arange(len(y)) ])
    intra_meet_length = np.mean(np.diff(z)).days
    fut_gen_n = len(t_list) - np.sum(z > ql_to_datetime(today)) + 1
    y1 = pd.Series(y.tolist()+pd.Series([y[-1:].values[0] + np.timedelta64(45 * i, 'D') for i in range(1,fut_gen_n)]).tolist())
    meet_index = pd.Series([y1[i].strftime('%b') + '-' + y1[i].strftime('%y') for i in range(len((y1)))])

    df2 = df1.sort_values(['date', 'meet_num'])
    df3 = df2.reset_index(drop=True)
    d_unique = df3['date'].unique()
    d_index = []
    d_index3 = []
    d_cum = []
    for i in np.arange(len(d_unique)):
        y_filter = np.sum(d_unique[i] > y1)
        cut_off = len(df3[df3['date'] == d_unique[i]])
        m =max(df3[df3['date'] == d_unique[i]]['meet_num'])
        if 0.5*m*(m+1) != np.sum(df3[df3['date'] == d_unique[i]]['meet_num']):
            print("you have an issue with ordering:", i, d_unique[i])
        d_index.append( meet_index[y_filter:y_filter+cut_off])
    d_index2 = flat_lst(d_index)
    df3['meet'] = d_index2
    df3['step2'] = np.round(100*(df3['value'].diff()),1)
    for i in np.arange(len(df3)):
        if df3['meet_num'][i] == 1:
            d_index3.append(0.0)
        else:
            d_index3.append(df3['step2'][i])
    df3['step'] = d_index3
    for i in np.arange(len(d_unique)):
        d_cum.append( df3[df3['date']==d_unique[i]]['step'].cumsum().tolist() )
    d_cum2 = flat_lst(d_cum)
    df3['cum'] = np.round(d_cum2,0)

    return df3

#df1 = get_wirp_hist('SOFR_DC')

#c = ccy('SOFR_DC', today)
#c.ois_meet_hist
