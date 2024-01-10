##### swaps building testing 

import pandas as pd
import numpy as np
import datetime
#import tia
#from tia.bbg import LocalTerminal as LT
import pdblp
import runpy
import QuantLib as ql
import matplotlib as mpl
import matplotlib.pyplot as plt

con = pdblp.BCon(debug=False, port=8194, timeout=50000)
con.start()

from Conventions import FUT_CT,FUT_CT_Q, ccy
from OIS_DC_BUILD import ois_dc_build
from Utilities import swap_class


def swap_build(a,b=0):

#    a = 'AUD_3M'
#    a = 'EUR_6M'
#    b = 0
    
    pd.set_option('display.max_columns', 10000)
    pd.set_option('display.width', 10000)
    
    ###### getting conventions 
    
    today = ql.Date(datetime.datetime.now().day,datetime.datetime.now().month,datetime.datetime.now().year)
    c = ccy(a,today)
    still_no_ois_disc_crvs = ['NOK_3M','NOK_6M','PLN_3M','PLN_6M','CZK_3M','CZK_6M','HUF_3M','HUF_6M','ZAR_3M','ILS_3M']
    
    if isinstance(b,int) == True:
        ref_date = c.cal.advance(today,b,ql.Days)
    else:
        #    c.cal.isBusinessDay(ref_date)
        ref_date = ql.Date(int(b.split('-')[0]),int(b.split('-')[1]),int(b.split('-')[2]))
    ref_date_1 = c.cal.advance(ref_date,-1,ql.Days)
    
    #### refine conventions c
    c = ccy(a,ref_date)

    ql.Settings.instance().evaluationDate = today
       
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
        
    ##### build relevant discoutn curve
    
    if a not in still_no_ois_disc_crvs:   ############ list of non-ois dc curves
        dc = ois_dc_build(c.dc_index, b).curve
        discount_curve = ql.RelinkableYieldTermStructureHandle(dc)
    
    ##### fiixing / depo rates
    try:
        depo = con.bdh(c.fixing, 'PX_LAST',bbg_t_1,bbg_t_1).iloc[0][0]
    except:
        depo = con.ref(c.fixing, 'PX_LAST')['value'][0]
    quotes1 = [ ql.SimpleQuote(depo/100) ]
    helpers = [ ql.DepositRateHelper(ql.QuoteHandle(quotes1[0]),c.fixing_tenor, c.sett_d,c.cal, ql.Following, False, c.floating[1] )]
    
    ################################ BBG Swap Rates
    
    obj = 'CURVE_TENOR_RATES'
    ticker = c.bbg_curve
    curve_ccy  =con.ref(ticker,'CRNCY')['value'][0]

    inst = con.bulkref(ticker, obj)
#    inst_dated = con.bulkref(ticker, obj, [('CURVE_DATE', '20211013')])

    x1 = inst['value'][inst['name']=='Tenor Ticker']
    x2 = inst['value'][inst['name']=='Tenor']
    
    x1 = x1.reset_index()
    x1.drop(columns= ['index'], inplace = True)
    x2 = x2.reset_index()
    x2.drop(columns= ['index'], inplace = True)
    x1['Tenor'] = x2

    x3 = x1[ x1['Tenor'] == c.start_swap].index.values
    x4 = x1[int(x3):].reset_index()
    
    
    if a == 'AUD_3M':
        for i in np.arange(2,     list(np.where(x4['Tenor'] == '10Y'))[0][0]  ):
                           x4['value'][i] = x4['value'][i].split()[0]+'Q '+'CBBT Curncy'
        for i in np.arange(  list(np.where(x4['Tenor'] == '10Y'))[0][0] ,len(x4)):
                           x4['value'][i] = x4['value'][i].split()[0][:4]+x4['Tenor'][i][:2]+'Q '+'CMPN Curncy'
                           
    if a == 'AUD_6M':
        for i in np.arange(2):
            x4['value'][i] = x4['value'][i].split()[0][:-1]+' BGN'+' Curncy'
        for i in np.arange(2, len(x4)):
            x4['value'][i] = x4['value'][i].split()[0]+' CBBT'+' Curncy'
                           
    if a == 'NOK_3M':
        for i in np.arange(len(x4)):
            x4['value'][i] = x4['value'][i].split()[0]+'V3 BGN Curncy'
            
    if a in ['CZK_3M','HUF_3M']:
        for i in np.arange(len(x4)):
            x4['value'][i] = x4['value'][i].split()[0]+'V3 BLC3 Curncy'
    
    x7 = con.bdh(x4['value'].tolist(),'PX_LAST',bbg_t,bbg_t, longdata = True)
    
    x4 = x4.set_index('value').join(x7.set_index('ticker'))    
    x4= x4.dropna()
    x4.rename(columns={'value': 'SwapRate', }, inplace=True)
    x4 = x4.reset_index()    
    x4.rename(columns={'value': 'TenorTicker', }, inplace=True)
    
    
    if a == 'MXN_TIIE':
        mxn_28d_convert = []
        for i in np.arange(len(x4)):
            if x4['Tenor'][i][-1] == 'M':
                mxn_28d_convert.append( 28*int(x4['Tenor'][i][:-1]) )
            elif x4['Tenor'][i][-1] == 'Y':
                mxn_28d_convert.append( 28*13*int(x4['Tenor'][i][:-1]) )
        
        x4['SwapTenor'] = mxn_28d_convert
        x5 = [(x4['SwapRate'][i], int(x4['SwapTenor'][i]), 'D') for i in range(len(x4))]
    else:
        x4['SwapTenor'] = [ int(x4['Tenor'][i][:-1]) for i in range(len(x4)) ]
        x5 = [(x4['SwapRate'][i], int(x4['SwapTenor'][i]), x4['Tenor'][i][-1]) for i in range(len(x4))]
    
    
    #x4
    ################################ BBG FRA Rates // Fut Prices + CC
    if c.add_inst == 'FRA':
        x6 = c.add_tenors['FRA']
        x7 = con.bdh(x6.tolist(), 'PX_LAST',bbg_t,bbg_t, longdata = True)
        
        x8 = pd.DataFrame()
        x8['TenorTicker'] = x6
        x8 = x8.set_index('TenorTicker').join(x7.set_index('ticker'))
        
        x9 = con.ref_hist(x6.tolist(),'SECURITY_TENOR_TWO_RT', dates = [bbg_t])
        x9['StartStub'] = [int(x9['value'][i].split('M')[0]) for i in range(len(x9)) ]
        x9.drop(columns= ['date','field','value'], inplace = True)
        x8 = x8.join(x9.set_index('ticker'))        
       
        x10 = [(x8['value'][i],int(x8['StartStub'][i])) for i in range(len(x8))]

       
        #x26 = [ (con.bdh(c.add_tenors['FRA'][i], 'PX_LAST',bbg_t,bbg_t).iloc[0][0], 
        #    int(con.ref_hist(c.add_tenors['FRA'][i], 'SECURITY_TENOR_TWO',dates = [bbg_t])['value'][0].split('M')[0])) 
        #    for i in range(len(c.add_tenors['FRA']))  ]
        
        for rate, months_to_start in x10:
            quotes1.append(ql.SimpleQuote(rate/100))
            helpers.append(ql.FraRateHelper(ql.QuoteHandle(quotes1[-1]),months_to_start, c.index_a ))
    
    elif c.add_inst == 'FUT':
        x6 = c.add_tenors['FRA']
             
        #x26 = [(con.bdh(c.add_tenors['FRA'][i], 'PX_LAST',bbg_t,bbg_t).iloc[0][0]+c.add_conv_corr['CC'][i],
        #       ql.Date(con.ref_hist(c.add_tenors['FRA'][i],'LAST_TRADEABLE_DT', dates = [bbg_t])['value'][0].day+c.sett_d,
        #               con.ref_hist(c.add_tenors['FRA'][i],'LAST_TRADEABLE_DT', dates = [bbg_t])['value'][0].month,
        #               con.ref_hist(c.add_tenors['FRA'][i],'LAST_TRADEABLE_DT', dates = [bbg_t])['value'][0].year)) 
        #           for i in range(2+int(c.start_swap[0])*4)]
#        x7 = pd.DataFrame(columns=('date','ticker','field','value'))
#        for i in np.arange(len(x6)):
#            print(x6[i])
#            x7 = x7.append(con.bdh(x6.tolist()[i], 'PX_LAST',bbg_t_1,bbg_t, longdata = True).iloc[-1], ignore_index=True)
#        x7 = con.bdh(x6.tolist()[1], 'PX_LAST',bbg_t_1,bbg_t, longdata = True)   ### doesnt work for

        x7 = []
        for i in np.arange(len(x6)):
            dict1 ={}
            dict1.update(con.bdh(x6.tolist()[i], 'PX_LAST',bbg_t_1,bbg_t, longdata = True).iloc[-1])
            x7.append(dict1)
        x7 = pd.DataFrame(x7)

        x8 = pd.DataFrame(c.add_conv_corr['CC'])
        x8 = x8.set_index(c.add_tenors['FRA']).join(x7.set_index('ticker'))
        if (a == 'SEK_3M') or (a == 'NOK_3M'):
            x8['CCAdjPx'] = 100 - x8['value'] + x8['CC']
        else:
            x8['CCAdjPx'] = x8['value'] + x8['CC']
        
        
        if type(con.ref_hist(x6.tolist()[0],'LAST_TRADEABLE_DT', dates = [bbg_t])['value'][0]) is not datetime.date:
            x9 = con.ref_hist(x6.tolist(),'SW_EFF_DT', dates = [bbg_t])
            fra_sett_adj = 0
        else:
            x9 = con.ref_hist(x6.tolist(),'LAST_TRADEABLE_DT', dates = [bbg_t])
            fra_sett_adj = c.sett_d
        
        if a == 'CAD_3M':
            fra_sett_adj = 2
        if a == 'NZD_3M':
            fra_sett_adj = 0
            
#        x9 = con.ref_hist(x6.tolist(),'LAST_TRADEABLE_DT', dates = [bbg_t])
        x9['StartDate'] = [ql.Date(x9['value'][i].day+fra_sett_adj, x9['value'][i].month, x9['value'][i].year) 
                            for i in range(len(x9)) ]
        x9.drop(columns= ['date','field','value'], inplace = True)
        x8 = x8.join(x9.set_index('ticker'))        
       
        x10 = [(x8['CCAdjPx'][i],x8['StartDate'][i]) for i in range(np.min([(0+int(c.start_swap[0])*4), len(x8)]))]    

        for price, start_date in x10:
            quotes1.append(ql.SimpleQuote(price))
            helpers.append(ql.FuturesRateHelper(ql.QuoteHandle(quotes1[-1]),start_date, 3,c.cal ,ql.Following, True, c.floating[1], ql.QuoteHandle(ql.SimpleQuote(0.0)), c.fut_type ))
    
    #x6
    ############################### Helpers aggregate rate + maturities
    
    
    if a in still_no_ois_disc_crvs:
        for rate, tenor, tenor_unit in x5:
            quotes1.append(ql.SimpleQuote(rate/100))
            helpers.append(ql.SwapRateHelper(ql.QuoteHandle(quotes1[-1]),ql.Period(tenor, ql.Years),
                                                 c.cal,
                                                 c.fixed[2], c.fixed[4], c.fixed[3],
                                                 c.index_a ))
    else:
        for rate, tenor, tenor_unit in x5:
            quotes1.append(ql.SimpleQuote(rate/100))
            if tenor_unit == 'M':
                helpers.append(ql.SwapRateHelper(ql.QuoteHandle(quotes1[-1]),ql.Period(tenor, ql.Months),
                                                 c.cal,
                                                 c.fixed[2], c.fixed[4], c.fixed[3],
                                                 c.index_a,
                                                 ql.QuoteHandle(), ql.Period(0, ql.Days) , discount_curve ))
            elif tenor_unit == 'D':
                helpers.append(ql.SwapRateHelper(ql.QuoteHandle(quotes1[-1]),ql.Period(tenor, ql.Days),
                                                 c.cal,
                                                 c.fixed[2], c.fixed[4], c.fixed[3],
                                                 c.index_a,
                                                 ql.QuoteHandle(), ql.Period(0, ql.Days) , discount_curve ))
            else:
                helpers.append(ql.SwapRateHelper(ql.QuoteHandle(quotes1[-1]),ql.Period(tenor, ql.Years),
                                                 c.cal,
                                                 c.fixed[2], c.fixed[4], c.fixed[3],
                                                 c.index_a,
                                                 ql.QuoteHandle(), ql.Period(0, ql.Days) , discount_curve ))
    

    ############################## Curve Build
    
    curve = ql.PiecewiseLogCubicDiscount(c.sett_d, c.cal, helpers, ql.Actual365Fixed())
    if a in still_no_ois_disc_crvs:
        dc = curve
    
    #eur6m_curve = ql.PiecewiseLogCubicDiscount(c.sett_d, c.cal, helpers, c.floating[1])
    #curve_handle = ql.RelinkableYieldTermStructureHandle(eur6m_curve)
    
    ############################### Curve Plots  + nodes
    
    #d1 = curve.referenceDate()
    #d2 = today + ql.Period(2,ql.Years)
    #dates_in = [ ql.Date(serial) for serial in range(d1.serialNumber(),d2.serialNumber()+1) ]
    
    #rates_c = [ 100*curve.forwardRate(d, c.cal.advance(d,3,ql.Months), c.floating[1], ql.Simple).rate()
    #            for d in dates_in ]
    
    #yr_axis = [(dates_in[i]-dates_in[0])/365.25 for i in range(len(dates_in)) ] 
    
    #plt.plot( yr_axis , rates_c , color = "blue")
    #plt.plot( x4['SwapTenor'] , x4['SwapRate'] ,'.', color = "red")
    #plt.show
    
    
#    curve.nodes()
#    x8
    
    ###### testing 3m curve fwds:
    
#    100*curve.forwardRate(ql.Date(22,6,2022), c.cal.advance(ql.Date(22,6,2022),3,ql.Months), c.floating[1], ql.Simple).rate()
#    100-100*curve.forwardRate(ql.Date(19,12,2018), c.cal.advance(ql.Date(19,12,2018),3,ql.Months), c.floating[1], ql.Simple).rate()
#    100-100*curve.forwardRate(ql.Date(18,3,2020), c.cal.advance(ql.Date(18,3,2020),3,ql.Months), c.floating[1], ql.Simple).rate()
#    100-100*curve.forwardRate(ql.Date(18,6,2020), c.cal.advance(ql.Date(18,6,2020),3,ql.Months), c.floating[1], ql.Simple).rate()
#    100-100*curve.forwardRate(ql.Date(16,9,2020), c.cal.advance(ql.Date(16,9,2020),3,ql.Months), c.floating[1], ql.Simple).rate()
#    100-100*curve.forwardRate(ql.Date(18,9,2021), c.cal.advance(ql.Date(18,9,2021),3,ql.Months), c.floating[1], ql.Simple).rate()
#    100-100*curve.forwardRate(ql.Date(18,9,2022), c.cal.advance(ql.Date(18,9,2022),3,ql.Months), c.floating[1], ql.Simple).rate()
    
    
     
    class swap_build_output():
        def __init__(self):
             self.curve = (curve,dc)
             self.ref_date = curve.referenceDate()
             self.ref_fix = depo
             self.trade_date = ref_date
             self.rates = x4[['Tenor','SwapRate']]
             self.stir_rates = x8
             self.nodes = curve.nodes()
             self.index = a
             self.index_custom = c.index_custom
             self.floating = c.floating
             self.cal = c.cal
             self.fixing = c.fixing
             self.ois_trigger = c.ois_trigger
             self.ccy = curve_ccy

    return swap_build_output()


#eur6m = swap_build('EUR_6M')
#eur3m = swap_build('EUR_3M')







