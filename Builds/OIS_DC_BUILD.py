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
from Conventions import FUT_CT,FUT_CT_Q, ccy
    
con = pdblp.BCon(debug=False, port=8194, timeout=50000)
con.start()


def ois_dc_build(a,b=0):
    
    today = ql.Date(datetime.datetime.now().day,datetime.datetime.now().month,datetime.datetime.now().year)

#    a = 'SOFR_DC'
#    b=0
#    b = '20-08-2021'
    
    c = ccy(a,today)
    
    #### date handling for hist 
    #b=0
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


    
    
    
##### outputs 
    x4 = con.bdh(x1['TenorTicker'].tolist(),'PX_LAST',bbg_t_1,bbg_t_1, longdata = True)
    
    x4 = x4.drop(['date', 'field'], axis=1)
    x1 = x1.set_index('TenorTicker').join(x4.set_index('ticker'))    
    #x1= x1.dropna()
    x1.rename(columns={'value': 'Rate_1D', }, inplace=True)
    x1 = x1.reset_index()    
    x1.rename(columns={'value': 'TenorTicker', }, inplace=True)

    #x1
    
    #x1['Rate_1D'] = pd.Series([con.bdh(x1['value'][i].split()[0]+str(' BGN ')+x1['value'][i].split()[1],'PX_LAST',bbg_t_1,bbg_t_1).iloc[0][0]
    #                             for i in range(len(x1))  ])  
       
    x1['Chg_1d'] = 100*(x1['Rate']-x1['Rate_1D'])
    
    rates_tab_2y_index = x1[x1['Tenor'] == '2Y'].index[0]
    rates_tab = x1[['Tenor','Rate']][rates_tab_2y_index:]
    rates_tab = rates_tab.reset_index(drop=True)
    rates_tab.columns = ['Tenor','SwapRate']

    print("*** !!! ois_curve built !!! ***")

    class ois_build_output(): 
           
            def __init__(self):
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


####################### sundry
####################### testing and plotting 

#EONIA = ois_dc_build('EONIA_DC')



#d2 = EONIA.ref_date
#d3 = d2 + ql.Period(40,ql.Years)
    
#dates_in = [ ql.Date(serial) for serial in range(d2.serialNumber(),d3.serialNumber()+1) ]
    
#rates_c = [100*EONIA.curve.forwardRate(d, ql.TARGET().advance(d,1,ql.Days), ql.Actual360(), ql.Simple).rate()
#                for d in dates_in ]
#yr_axis = [(dates_in[i]-dates_in[0])/365.25 for i in range(len(dates_in)) ] 
#dates = [ql_to_datetime(dates_in[i]) for i in range(len(dates_in))] 


#def ql_to_datetime(d):
#    return pd.datetime(d.year(), d.month(), d.dayOfMonth())

#from matplotlib.pyplot import figure
#figure(num=None, figsize=(10, 7), dpi=80, facecolor='w', edgecolor='k')

#plt.figure(figsize=(10, 7), dpi=80)
#plt.plot( yr_axis , rates_c , color = "blue")

#mpl.rcParams['axes.facecolor'] = 'white'
#plt.rcParams['axes.labelpad'] = 400.00
#plt.figure(figsize=(10, 7), dpi=80)
#plt.grid(True, 'major', 'both', linestyle = '-.')
#plt.plot( yr_axis , rates_c , color = "blue")












