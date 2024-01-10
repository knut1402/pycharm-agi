#### inflation swap build

import os
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
from tabulate import tabulate

con = pdblp.BCon(debug=False, port=8194, timeout=50000)
con.start()

pd.set_option('display.max_columns', 10000)
pd.set_option('display.width', 10000)

from Conventions import FUT_CT, ccy, ccy_infl
from OIS_DC_BUILD import ois_dc_build
from Utilities import *


def infl_zc_swap_build(a,b=0, base_month_offset=0):

#    a = 'UKRPI'
#    a = 'HICPxT'
#    b=-1
#    base_month_offset=0
    
    today = ql.Date(datetime.datetime.now().day,datetime.datetime.now().month,datetime.datetime.now().year)
    c = ccy_infl(a,today)
    
    dc_curve = ois_dc_build(c.dc_curve, b).curve
    
    #### date handling for hist 
    if isinstance(b,int) == True:
        ref_date = c.cal.advance(today,b,ql.Days)
    else:
        ref_date = ql.Date(int(b.split('-')[0]),int(b.split('-')[1]),int(b.split('-')[2]))
    
    ### handle dates
    settle_date = c.cal.advance(ref_date,2,ql.Days)
    ref_date_1 = c.cal.advance(ref_date,-1,ql.Days)
    ql.Settings.instance().evaluationDate = ref_date
    c = ccy_infl(a,ref_date)
    
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
    inf_index_hist = c.fixing_hist
    ### get seasonality
    inf_seas = c.seas
    

    ### get inflation swap data
    inf_tab = pd.DataFrame(columns=['ticker','maturity','px','index_eod','index','mom'])
    inf_tab['ticker'] = c.ticker
    for i in np.arange(len(c.ticker)):
        inf_tab['maturity'][i] = con.ref(c.ticker[i], 'SECURITY_TENOR_TWO_RT')['value'].tolist()[0]
        inf_tab['px'][i] = con.bdh(c.ticker[i], 'PX_LAST',bbg_t,bbg_t, longdata=True)['value'][0]



    ### set base index + sort seasonality vector to start by base month+1
    base_month = c.base_month + ql.Period(str(base_month_offset)+'M')
    inf_tab['index_eod'] = [base_month + ql.Period(inf_tab['maturity'][i]) for i in np.arange(len(inf_tab))]
    if c.interp == 0:
        base_index = inf_index_hist[inf_index_hist['months'] == base_month]['index'].tolist()[0]
    else: 
        base_index = get_infl_index(inf_index_hist, ref_date)

    jig_seas = pd.DataFrame(columns=('months','seas'))
    jig_seas['months'] = inf_seas[base_month.month():]['months'].tolist()+inf_seas[:base_month.month()]['months'].tolist()
    jig_seas['seas'] = inf_seas[base_month.month():]['seas'].tolist()+inf_seas[:base_month.month()]['seas'].tolist()


    ### output inflation index projection
    inf_tab['index'] = [base_index*(1+(0.01*inf_tab['px'][i]))**(int(inf_tab['maturity'][i][:-1])) for i in np.arange(len(inf_tab))]
    
    ###### Dealing with fixings already published ====== ZC 1y point
    st_date = c.last_fix_month
    st_index = c.fixing_hist[c.fixing_hist['months'] == st_date]['index'].tolist()[0]
    y1_trend = np.floor((inf_tab['index_eod'][0] - c.last_fix_month)/30)
    inf_tab['mom'][0] = 100*((inf_tab['index'][0] / st_index)**(1/ y1_trend )-1)
    
    st_date = inf_tab['index_eod'][0]
    st_index = inf_tab['index'][0]
    
    for i in np.arange(len(inf_tab))[1:]:
        inf_tab['mom'][i] = 100*((inf_tab['index'][i] / st_index)**(1/(np.floor((inf_tab['index_eod'][i] - st_date)/365)*12))-1)
        st_index = inf_tab['index'][i]
        st_date = inf_tab['index_eod'][i]

    inf_index_proj = pd.DataFrame(columns=['months','index_trend','index'])
    schedule_2 = ql.MakeSchedule(base_month + ql.Period('1M'), inf_tab['index_eod'].tolist()[-1], ql.Period('1M'))
    inf_index_proj['months'] = [schedule_2[i] for i in range(len(schedule_2))]
    
    fixed_fixings = 12 - int(y1_trend)
    
    if fixed_fixings > 0:    ###### what if base month is last fixings !!!
        for j in np.arange(fixed_fixings):
            inf_index_proj['index_trend'][j] = c.fixing_hist[c.fixing_hist['months']  == inf_index_proj['months'][j]]['index'].tolist()[0]
            inf_index_proj['index'][j] = c.fixing_hist[c.fixing_hist['months']  == inf_index_proj['months'][j]]['index'].tolist()[0]
    
        for j in np.arange(fixed_fixings ,11):
            inf_index_proj['index_trend'][j] = inf_index_proj['index_trend'][j-fixed_fixings]*(1+(inf_tab['mom'][0]/100))
            inf_index_proj['index'][j] = inf_index_proj['index_trend'][j]*(1+ (np.sum(jig_seas['seas'][fixed_fixings:(j%12 + 1)])/100))
            
            inf_index_proj['index_trend'][11] = inf_tab['index'][0]
            inf_index_proj['index'][11] = inf_tab['index'][0]

    else:
        st_index = base_index
        for j in np.arange(12):
            inf_index_proj['index_trend'][j] = st_index*(1+(inf_tab['mom'][0]/100))
            inf_index_proj['index'][j] = inf_index_proj['index_trend'][j]*(1+ (np.sum(jig_seas['seas'][:(j%12 + 1)])/100))
            st_index = inf_index_proj['index_trend'][j]
            
    
    ####### Dealding with  > 1y ZC fixings
    i = 0
    st_index = inf_tab['index'][0]
    for j in np.arange(12,len(inf_index_proj)):
        if (inf_index_proj['months'][j] <= inf_tab['index_eod'][i]):
            i = i
        else:
            i = i+1
        inf_index_proj['index_trend'][j] = st_index*(1+(inf_tab['mom'][i]/100))
        inf_index_proj['index'][j] = inf_index_proj['index_trend'][j]*(1+ (np.sum(jig_seas['seas'][:(j%12 + 1)])/100))
        st_index = inf_index_proj['index_trend'][j]
    
    ###### defining different curves
    ### 1. simple - seasonally defined
    cutoff = np.where(inf_index_proj['months'] == inf_index_hist['months'].iloc[-1])[0][0]
    prj_inf_fixings = inf_index_hist[:-cutoff - 1]
    inf_fixings1 = prj_inf_fixings.append(inf_index_proj, ignore_index=True)
    ### using bank forecast
    prj_inf_fixings = inf_index_proj[cutoff + 1:]
    inf_fixings2 = inf_index_hist.append(prj_inf_fixings, ignore_index=True)
    ### using BGC market fixings
    if c.fix_ticker[0] != 'none':
        inf_fixings3 = inf_index_proj
        for i in np.arange(fixed_fixings, 11):
            m2 = inf_fixings3.iloc[i]['months'].month()
            ticker1 = c.fix_ticker[0] + str(m2) + c.fix_ticker[1]
            y1 = con.bdh(ticker1, 'PX_LAST', bbg_t, bbg_t, longdata=True)['value'][0] / 100
            b1 = list(inf_index_hist[inf_index_hist['months'] == (inf_fixings3.iloc[i]['months'] - ql.Period('1Y'))]['index'])[0]
            inf_fixings3.at[i, "index"] = b1 * (1 + (y1 / 100))
#            print(m2)
#            print( b1 * (1 + (y1 / 100)))
#            print(inf_fixings3.iloc[i]['index'])

        prj_inf_fixings = inf_index_hist[:-cutoff - 1]
        inf_fixings3 = prj_inf_fixings.append(inf_fixings3, ignore_index=True)
    else:
        inf_fixings3 = inf_fixings1

    class infl_zc_build_output():
        def __init__(self):
             self.curve = (inf_fixings1, inf_fixings3, inf_fixings2)
             self.index = c.index
             self.fixing_hist = inf_index_hist
             self.seas = inf_seas
             self.ref_date = ref_date
             self.settle_date = settle_date
             self.base_month = base_month
             self.base_index = base_index
             self.interp = c.interp
             self.cal = c.cal
             self.rates = inf_tab[['maturity','px']]
             self.ccy = c.ccy
             self.last_pm =  c.last_fix_month
             self.dc = dc_curve

    return infl_zc_build_output()


#rpi = infl_zc_swap_build('UKRPI',b=0)
#rpi.rates
#rpi.curve[0][250:270]
#rpi.ref_date
#rpi.base_month
#rpi.interp

#inf_fixings1[260:270]
#inf_fixings2[260:270]
#inf_fixings3[260:270]

#inf_fixings1[295:301]
#inf_fixings2[295:301]
#inf_fixings3[295:301]



def Infl_ZC_Pricer(inf_curve, st_date, tenor, lag = 3, not1 = 10, use_forecast = 0, use_mkt_fixing = 0):

#    inf_curve = ukrpi1
#    st_date = ql.Date(1,12,2020)
#    st_date = '6M'
#    st_date = 0
#    tenor = 1
#    lag = 0
#    use_forecast = 0
#    use_mkt_fixing = 1
#    not1 = 10

    if use_forecast == 1:
        inf_fixings = inf_curve.curve[2]
        last_fixing_month = inf_curve.fixing_hist['months'][-1:].tolist()[0]
    elif use_mkt_fixing == 1:
        inf_fixings = inf_curve.curve[1]
        last_fixing_month = inf_curve.last_pm
    else:
        inf_fixings = inf_curve.curve[0]
        last_fixing_month = inf_curve.last_pm
        
    if isinstance(st_date,ql.Date) == True:
        start = st_date
    elif isinstance(st_date,str) == True:
        try:
            start = ql.Date(int(st_date.split('-')[0]),int(st_date.split('-')[1]),int(st_date.split('-')[2]))
        except:
            if st_date[-1] in ('D','d'):
                unit = ql.Days
            elif st_date[-1] in ('W','w'):
                unit = ql.Weeks
            elif st_date[-1] in ('M','m'):
                unit = ql.Months
            start = inf_curve.settle_date + ql.Period(st_date)

    else:
        start = inf_curve.settle_date + ql.Period(str(st_date)+"Y")
    
    ### lagged start
    if inf_curve.interp == 0:
        start_month = inf_curve.cal.advance(start,-lag,ql.Months)
        start_month = start_month - start_month.dayOfMonth() + 1
        end_month = inf_curve.cal.advance(start_month,tenor,ql.Years)
        end_month = end_month - end_month.dayOfMonth() + 1
        
        base_month = inf_fixings[inf_fixings['months'] == start_month]['months'].tolist()[0]
        index_ratio = (inf_fixings[inf_fixings['months'] == end_month]['index'].tolist()[0] / inf_fixings[inf_fixings['months'] == start_month]['index'].tolist()[0])
        zc_rate =  100*((index_ratio ** (1/tenor)) - 1)
    else: 
        start_month = start - ql.Period("3M")
        end_month = start_month + ql.Period(str(tenor)+"Y")
        
        base_month = inf_fixings[inf_fixings['months'] == start_month]['months'].tolist()[0]
        index_ratio = (inf_fixings[inf_fixings['months'] == end_month]['index'].tolist()[0] / inf_fixings[inf_fixings['months'] == start_month]['index'].tolist()[0])
        zc_rate =  100*((index_ratio ** (1/tenor)) - 1)

    base_month_fix = inf_fixings[inf_fixings['months'] == start_month]['index'].tolist()[0]
    
    ### calc inf01
    try:
        df1 = inf_curve.dc.discount(end_month)
    except:
        df1 = 1
    inf01 = tenor*((1+ (zc_rate / 100 ))**(tenor-1))* df1
    risk01 = inf01*not1*100
    
    
    class infl_zc_pricer_output():
        def __init__(self):
             self.base = base_month
             self.base_fixing = base_month_fix
             self.index = inf_curve.index
             self.zc_rate = np.round(zc_rate,3)
             self.interp = inf_curve.interp
             self.last_fm = last_fixing_month
             self.inf01 = np.round(inf01,1)
             self.risk = np.round(risk01,1)

    return infl_zc_pricer_output()

#xt = infl_zc_swap_build('HICPxT',b=0)
#xt1 = infl_zc_swap_build('HICPxT',b=-1)

#Infl_ZC_Pricer(rpi, '01-12-2020', 1, lag = 0, use_forecast=0, use_mkt_fixing=1).zc_rate
#Infl_ZC_Pricer(rpi, '01-12-2020', 1, lag = 0, use_forecast=0, use_mkt_fixing=1).base




######## plottting yoy inflation rates for some past and future dates 
#ukrpi1 = infl_zc_swap_build('UKRPI', b=0)
#hicpxt1 = infl_zc_swap_build('HICPxT', b=0)
#ukrpi1.rates

#rpi2 = [Infl_ZC_Pricer(ukrpi1, '15-10-2020', 1, lag = int(2-i), use_forecast=0, use_mkt_fixing=1).zc_rate for i in np.arange(49)]
#hicp2 = [Infl_ZC_Pricer(hicpxt1, '15-10-2020', 1, lag = int(2-i), use_forecast=0, use_mkt_fixing=1).zc_rate for i in np.arange(49)]

#cal = ql.UnitedKingdom()
#dates2 = [cal.advance(ql.Date(15,8,2021), ql.Period(str(i)+'M')) for i in np.arange(49) ]
#dates3 = [ql_to_datetime(dates2[i]) for i in np.arange(len(dates2))]

#plt.figure(figsize=(10,8))
#plt.plot(dates3, rpi2, label = "RPI")
#plt.plot(dates3, hicp2, label = "HICPxT")
#plt.axvline(x=dates3[12], c = 'k')
#plt.xticks(rotation = 90)
#plt.xlabel("Fixings Date")
#plt.ylabel("Inflation YoY")
#plt.legend()



#ukrpi1 = infl_zc_swap_build('UKRPI', b=0)
#ukrpi2 = infl_zc_swap_build('UKRPI', b=-1)



def inf_swap_table(crvs, lag, outright_rates, fwd_rates, curve_rates, fly_rates,  shift = [0,'1M','2M','3M'], price_nodes = 1, use_forecast = 0, use_mkt_fixing = 0):
    
#    crvs = [xt, xt1]
#    shift = [0,'1M','2M','3M']
#    outright_rates = [1,2,3,4,5,6,7,8,9,10,12,15,20,25,30]
#    fwd_rates = [(1,1), (2,1), (3,1), (4,1), (2,2), (3,2), (5,5), (10,5), (10,10), (15,15) ]
#    curve_rates = [(2,3), (2,5), (2,10), (5,10), (5,30), (10,30)]
#    fly_rates = [(2,3,5), (2,5,10), (3,5,7), (5,10,30)]
#    price_nodes = 1   
#    lag = [3,3]
#    use_forecast = 0
#    use_mkt_fixing = 0
 
    x1 = []
    for i in np.arange(len(outright_rates)):
        x1.append([ Infl_ZC_Pricer( crvs[j], 0, outright_rates[i], lag[j] , not1 = 10, use_forecast=use_forecast , use_mkt_fixing=use_mkt_fixing ).zc_rate   for j in np.arange(len(crvs))] )
    zc = flat_lst( [ (x1[i][0], [100*(x1[i][0]-x1[i][j]) for j in np.arange(1,len(crvs))]) for i in np.arange(len(x1))] )

    if price_nodes == 1:
        x_fixing = [crvs[0].last_pm + ql.Period(str(i)+"M") for i in np.arange(13)]
        x2_mkt = []
        x2_barx = []
        for i in x_fixing:
            x2_mkt.append( [  Infl_ZC_Pricer( crvs[j], i-ql.Period("1y"), 1, lag = 0, not1 = 10, use_forecast = 0, use_mkt_fixing = 1).zc_rate    for j in np.arange(len(crvs))]  )
            x2_barx.append( [  Infl_ZC_Pricer( crvs[j], i-ql.Period("1y"), 1, lag = 0, not1 = 10, use_forecast = 1, use_mkt_fixing = 0).zc_rate    for j in np.arange(len(crvs))]  )
        
        fix_mkt = flat_lst( [ (x2_mkt[i][0], [100*(x2_mkt[i][0]-x2_mkt[i][j]) for j in np.arange(1,len(crvs))], x2_barx[i][0],  100*(x2_mkt[i][0] - x2_barx[i][0])   ) for i in np.arange(len(x2_mkt))])
    else:
        fix_mkt = []

    x3 = []
    for i,j in fwd_rates:
        x3.append([  Infl_ZC_Pricer( crvs[k], i, j, lag[k] , not1 = 10, use_forecast=use_forecast , use_mkt_fixing=use_mkt_fixing ).zc_rate   for k in np.arange(len(crvs))] )
    
    x4 = []
    x5 = []  
    for s in shift:
        for i,j in curve_rates:
            x4.append( [ 100*(Infl_ZC_Pricer( crvs[l], s, i, lag[l] , not1 = 10, use_forecast=use_forecast , use_mkt_fixing=use_mkt_fixing ).zc_rate - Infl_ZC_Pricer( crvs[l], s, j, lag[l] , not1 = 10, use_forecast=use_forecast , use_mkt_fixing=use_mkt_fixing ).zc_rate)  for l in np.arange(len(crvs))] )            
        for i,j,k in fly_rates:
            x5.append([    100*(  (2*Infl_ZC_Pricer( crvs[l], s, j, lag[l] , not1 = 10, use_forecast=use_forecast , use_mkt_fixing=use_mkt_fixing ).zc_rate) - Infl_ZC_Pricer( crvs[l], s, i, lag[l] , not1 = 10, use_forecast=use_forecast , use_mkt_fixing=use_mkt_fixing ).zc_rate - Infl_ZC_Pricer( crvs[l], s, k, lag[l] , not1 = 10, use_forecast=use_forecast , use_mkt_fixing=use_mkt_fixing ).zc_rate )   for l in np.arange(len(crvs))] )
        
    fwds = flat_lst( [ (x3[i][0], [100*(x3[i][0]-x3[i][j]) for j in np.arange(1,len(crvs))]) for i in np.arange(len(x3))] )
    curve = flat_lst( [ (x4[i][0], [1*(x4[i][0]-x4[i][j])   for j in np.arange(1,len(crvs))], [x4[ i+(len(curve_rates)*k)  ][0] for k in np.arange(1,len(shift))]) for i in np.arange(len(curve_rates))] )
    fly = flat_lst( [ (x5[i][0], [1*(x5[i][0]-x5[i][j])   for j in np.arange(1,len(crvs))], [x5[ i+(len(fly_rates)*k)  ][0] for k in np.arange(1,len(shift))]) for i in np.arange(len(fly_rates))] )
    


    class inf_swap_table_output():
        def __init__(self):
            self.fixings = fix_mkt
            self.zc = zc
            self.fwds = fwds
            self.curve = curve
            self.fly = fly
    
    return inf_swap_table_output()
