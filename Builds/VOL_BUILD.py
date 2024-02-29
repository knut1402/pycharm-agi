######## VOL CURVE BUILDS

#### Bond Futures

import os
import pandas as pd
import numpy as np
import math
import datetime
#import tia
#from tia.bbg import LocalTerminal as LT
import pdblp
import runpy
import QuantLib as ql
import matplotlib as mpl
import matplotlib.pyplot as plt
from tabulate import tabulate
import pickle

pd.set_option('display.max_columns', 10000)
pd.set_option('display.width', 10000)

con = pdblp.BCon(debug=False, port=8194, timeout=50000)
con.start()

from Utilities import *
from Conventions import FUT_CT,FUT_CT_Q, ccy

########################################### BUILD SURFACE !! 
def build_vol_surf(chain_ticker, chain_len=[12,12], b=0):
    
#    chain_ticker = ['RXH4P 133.0']
#    chain_len = [12,12]
#    b = 0

    chain_ticker = chain_ticker[0]+' Comdty'
    chain_filter = chain_ticker[:4]

    fut = con.ref(chain_ticker, ['OPT_UNDL_TICKER'])['value'][0]+' Comdty'
    ccy1 = con.ref(chain_ticker, ['CRNCY'])['value'][0]
    
    today = ql.Date(datetime.datetime.now().day,datetime.datetime.now().month,datetime.datetime.now().year)
    if ccy1 == 'USD':
        c = ccy('SOFR_DC',today)
    elif ccy1 == 'EUR':
        c = ccy('ESTER_DC',today)
    elif ccy1 == 'GBP':
        c = ccy('SONIA_DC',today)

    #### date handling for hist 
    #b=0
    if isinstance(b,int) == True:       
        if ((c.cal.isWeekend(today.weekday()) == False and b == 0) and c.cal.isHoliday(today) == True):
            ref_date = today
        else:
            ref_date = c.cal.advance(today,b,ql.Days)
    else:
        ref_date = ql.Date(int(b.split('-')[0]),int(b.split('-')[1]),int(b.split('-')[2]))
    
    ref_date_1 = c.cal.advance(ref_date,-1,ql.Days)
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
    bbg_t_1 = str(ref_date_1.year())+m1+d1

    #### get closes after 10pm!
    now = datetime.datetime.now()
    today7am = now.replace(hour=7, minute=0, second=0, microsecond=0)
    today10pm = now.replace(hour=22, minute=0, second=0, microsecond=0)
    time_check = ((now > today7am) and (now < today10pm))

    if ((ref_date == today) and (now < today7am)):
        spot = con.bdh(fut, ['PX_LAST'],bbg_t_1, bbg_t_1, longdata=True)['value'][0]
    else:
        spot = con.bdh(fut, ['PX_LAST'],bbg_t, bbg_t, longdata=True)['value'][0]
    centre_strike = np.round(spot*2)/2
    

    df_chain = con.bulkref(fut, ['OPT_CHAIN'])
    df_chain['des'] = [df_chain['value'][i][:4] for i in np.arange(len(df_chain))]
    df_chain['opt_type'] = [df_chain['value'][i][4:5] for i in np.arange(len(df_chain))]
    df_chain['strike'] = [float(df_chain['value'][i][5:-6].strip()) for i in np.arange(len(df_chain))]
    df_chain = df_chain[df_chain['des'] == chain_filter]
    
    if len(df_chain[df_chain['strike'] == centre_strike]) == 0 :
        centre_strike = np.round(spot)
        idx1 = df_chain[df_chain['strike'] == centre_strike].index
    else:
        idx1 = df_chain[df_chain['strike'] == centre_strike].index
    
    df_chain2 = df_chain.loc[(idx1[0] - chain_len[0]):idx1[0] + 5]   #### hardcoding for max 10 ITM options
    df_chain2.reset_index(drop=True, inplace=True)
    df_chain2 = df_chain2.append(df_chain.loc[idx1[1] - 5:(idx1[1] + chain_len[1] + 1)], ignore_index=True)

    ticker = df_chain2['des'][0]
    option_type = df_chain2['opt_type']
    strikes = df_chain2['strike']
    opt_type = df_chain2['opt_type']

    t2 = [ticker+option_type[i]+' '+str(strikes[i])+' Comdty' for i in np.arange(len(strikes))]
    expiry_dt = con.ref(t2[0], ['LAST_TRADEABLE_DT'])['value'][0]
    expiry_dt = ql.Date(expiry_dt.day,expiry_dt.month,expiry_dt.year)
#    fut = con.ref(t2[0], ['OPT_UNDL_TICKER'])['value'][0]+' Comdty'
#    spot =  con.ref(fut, ['PX_LAST'])['value'][0]

    option_type_ql = []
    for i in np.arange(len(option_type)):
        if option_type[i] == 'C':
            option_type_ql.append(ql.Option.Call)
        else:
            option_type_ql.append(ql.Option.Put)

#### option modelling
    r = con.ref(c.fixing, ['PX_LAST'])['value'][0]/100
    day_count = ql.Actual365Fixed()
    calendar = c.cal

#    calculation_date = ql.Date(datetime.datetime.now().day,datetime.datetime.now().month,datetime.datetime.now().year)
#    ql.Settings.instance().evaluationDate = calculation_date
    calculation_date = ref_date
    ql.Settings.instance().evaluationDate = today

    volatility = 0.05
    spot_handle = ql.QuoteHandle(ql.SimpleQuote(spot))
    flat_ts = ql.YieldTermStructureHandle(ql.FlatForward(calculation_date, r, day_count))
    flat_vol_ts = ql.BlackVolTermStructureHandle(ql.BlackConstantVol(calculation_date, calendar, volatility, day_count))
    bsm_process = ql.BlackProcess(spot_handle, flat_ts, flat_vol_ts)

    if ((ref_date == today) and time_check):
        df1 = con.bdh(t2, ['PX_BID', 'PX_ASK'], bbg_date_str(calculation_date), bbg_date_str(calculation_date),
                      longdata=True)
    elif ((ref_date == today) and (now > today10pm)):
        df1 = con.bdh(t2, ['PX_LAST'], bbg_date_str(calculation_date), bbg_date_str(calculation_date), longdata=True)
    elif ((ref_date == today) and (now < today7am)):
        df1 = con.bdh(t2, ['PX_LAST'], bbg_date_str(ref_date_1), bbg_date_str(ref_date_1), longdata=True)
    else:
        df1 = con.bdh(t2, ['PX_LAST'], bbg_date_str(calculation_date), bbg_date_str(calculation_date), longdata=True)

    opt_px = df1.groupby('ticker').value.mean()
    opt_px[opt_px < 1/64] = 0.5/64   ######## remove 0 prices for cab 
    
    t3 = np.unique(df1['ticker']).tolist()
    mask1 = [t2[i] in t3 for i in np.arange(len(t2))]
    t4 = np.array(t2)[mask1].tolist()
    
    df2 = pd.DataFrame()
    df2['ticker'] = t4
    df2['strikes'] = np.array(strikes)[mask1].tolist()
    df2['opt_type'] = np.array(option_type_ql)[mask1].tolist()
    df2['px'] = [opt_px[opt_px.index == t4[i]].values[0] for i in np.arange(len(opt_px))]
    df2['px_64'] = [px_opt_ticks(df2['px'][i]) for i in np.arange(len(opt_px))]

    df3 = bond_fut_yield(fut[:4], np.unique(df2['strikes']).tolist() )
    df2['Yld'] = [df3[df3['K_'] == df2['strikes'][i]]['K_Yield'].tolist()[0] for i in np.arange(len(df2))]
    df2['ATM_K'] = [df3[df3['K_'] == df2['strikes'][i]]['K_Dist'].tolist()[0] for i in np.arange(len(df2))]


    ### Vanilla + European+ Analytic
    opt_iv = []
    opt_delta = []
    opt_gamma = []
    opt_theta = []
    opt_vega = []
    opt_bs_px = []

    for i in np.arange(len(opt_px)):
#        i = 16
        print(i,df2['ticker'][i])
        payoff = ql.PlainVanillaPayoff( int(df2['opt_type'][i]), df2['strikes'][i])
        exercise = ql.EuropeanExercise(expiry_dt)
        option = ql.VanillaOption(payoff, exercise)

        option.setPricingEngine(ql.AnalyticEuropeanEngine(bsm_process))

        opt_iv.append(100*option.impliedVolatility(df2['px'][i], bsm_process, maxVol = 1000, maxEvaluations=1000000))
        opt_vol_ts = ql.BlackVolTermStructureHandle(ql.BlackConstantVol(calculation_date, calendar, opt_iv[i]/100, day_count))
        bsm_process = ql.BlackProcess(spot_handle, flat_ts, opt_vol_ts)
        option.setPricingEngine(ql.AnalyticEuropeanEngine(bsm_process))
    
        opt_bs_px.append(option.NPV())
        opt_delta.append(100*option.delta())
        opt_gamma.append(option.gamma())
        opt_theta.append(option.theta())
        opt_vega.append(option.vega())

    df2['bs_px'] = opt_bs_px
    df2['iv'] = opt_iv
    df2['delta'] = opt_delta
    df2['gamma'] = opt_gamma
    df2['theta'] = opt_theta
    df2['vega'] = opt_vega

    if ccy1 == 'USD':
        st_type = 'USD'
    else:
        st_type = 'Non-USD'

    class vol_surf_output():
        def __init__(self):
            self.tab = df2
            self.tab_call = df2[df2['opt_type'] == 1]
            self.tab_put = df2[df2['opt_type'] == -1]
            self.ticker = chain_ticker
            self.center = centre_strike
            self.expiry_dt = expiry_dt
            self.fut = fut
            self.spot_px = spot
            self.spot_px_fmt = px_dec_to_frac(spot)
            self.ref_date = ref_date
            self.currency = ccy1
            self.type = st_type

    print("*** !!! listed_vol surf built !!! ***")
    return vol_surf_output()

#v1 = build_vol_surf(['TYH4P 111'], chain_len=[15,15], b=0)
#v2 = build_vol_surf(['TYH4P 111'], chain_len=[12,12], b=-1)
#v1 = build_stir_vol_surf(['0EH2P 98.5'], chain_len=[8,8], b=0)
#df = v2.tab
#v1.tab

#################### build vol spline 
def build_vol_spline(fut, sim_spot, a):
#    fut = '0QU4'
#    sim_spot = 96.0625
#    a = v1

#    df3 = pd.DataFrame(index = a.tab_call['strikes'])
#    df3['ATM_K'] = np.array(a.tab_call['ATM_K'] - a.tab_call[a.tab_call['strikes'] == sim_spot]['ATM_K'].tolist())
#    df3['iv_c'] = np.interp(df3['ATM_K'], a.tab_call['ATM_K'][::-1], a.tab_call['iv'][::-1])
#    df3['iv_p'] = np.interp(df3['ATM_K'], a.tab_put['ATM_K'][::-1], a.tab_put['iv'][::-1])

    ### *****  code for if we use diff strikes for puts and calls
    if np.sum(a.tab_call['strikes'] == sim_spot):    #### in list doesnt seem to always work !
        df3 = pd.DataFrame(index=a.tab_call['strikes'])
        df3['ATM_K'] = np.array(a.tab_call['ATM_K'] - a.tab_call[a.tab_call['strikes'] == sim_spot]['ATM_K'].tolist())
        df4 = pd.DataFrame(index=list(set(a.tab_put['strikes'].tolist()) - set(a.tab_call['strikes'].tolist())))
        df4['ATM_K'] = [ (a.tab_put['ATM_K'][i] - a.tab_call[a.tab_call['strikes'] == sim_spot]['ATM_K']).tolist()[0]  for i in np.arange(len(a.tab_put)) if a.tab_put['strikes'][i] in df4.index.tolist()]

    else:
        df3 = pd.DataFrame(index=a.tab_put['strikes'])
        df3['ATM_K'] = np.array(a.tab_put['ATM_K'] - a.tab_put[a.tab_put['strikes'] == sim_spot]['ATM_K'].tolist())
        df4 = pd.DataFrame(index=list(set(a.tab_call['strikes'].tolist()) - set(a.tab_put['strikes'].tolist())))
        df4['ATM_K'] = [ (a.tab_call['ATM_K'][i] - a.tab_put[a.tab_put['strikes'] == sim_spot]['ATM_K']).tolist()[0]  for i in np.arange(len(a.tab_put),len(a.tab)) if a.tab_call['strikes'][i] in df4.index.tolist()]


    df5 = pd.concat([df3, df4]).drop_duplicates().sort_index()
    df5['iv_c'] = np.interp(df5['ATM_K'], a.tab_call['ATM_K'][::-1], a.tab_call['iv'][::-1])
    df5['iv_p'] = np.interp(df5['ATM_K'], a.tab_put['ATM_K'][::-1], a.tab_put['iv'][::-1])

    return df5


def bond_fut_opt_strat(t, opt_t, opt_s, opt_w, s_range = [-1,2], increm = 0.5, s_name = 'strategy', built_surf = 0, chain_len = [12,12]):
#    t = ['TYH4']
#    opt_t = ['P','P']
#    opt_s = [110,108.5]
#    opt_w = [1,-1]
#    increm = 0.5
#    s_range = [0,1]
#    s_name = 'TYH4 PS'
#    chain_len= [12,12]
    if built_surf == 0:
        v1 = build_vol_surf([t[0]+opt_t[0]+' '+str(opt_s[0])], chain_len, b = 0)  ##### MAKE SURE NO DATES  ie no b !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    else:
        v1 = built_surf
#    v1.tab
    
    opt_t2 = []
    for i in opt_t:
        if i == 'C':
            opt_t2.append(1)
        else:
            opt_t2.append(-1)
    
    df4 = pd.DataFrame()
    for i in np.arange(len(opt_t)):
        df4 = df4.append(v1.tab[(v1.tab['opt_type'] == opt_t2[i]) & (v1.tab['strikes'] == opt_s[i])], ignore_index = True)
        
    df4['weight'] = opt_w
    st_px = np.dot(df4['bs_px'],df4['weight'])
    
    df_opt_strat = pd.DataFrame()
    df_opt_strat['fut_px'] = [v1.spot_px]
    df_opt_strat['ATM_K'] = np.array([0.0])
    df_opt_strat['strat_px'] = st_px
    df_opt_strat['strat_delta'] = np.dot(df4['delta'],df4['weight'])
    df_opt_strat['strat_gamma'] = np.dot(df4['gamma'],df4['weight'])
    df_opt_strat['strat_theta'] = np.dot(df4['theta'],df4['weight'])
    df_opt_strat['strat_vega'] = np.dot(df4['vega'],df4['weight'])
    
    fut_spot_sim  = [round(v1.spot_px*(1/increm))/(1/increm)]
    
    sim_range = np.arange(min(opt_s+fut_spot_sim)+s_range[0],max(opt_s+fut_spot_sim)+s_range[1]+increm,increm)
    
    sim_dict = {}
    for i in sim_range:
#        print(i)
        df_all = build_vol_spline(v1.fut[:4], i, v1)
        sim_dict[i] = df_all.loc[opt_s]
        s1 = get_sim_option_px(v1.currency, v1.ref_date, i, opt_t, opt_s, [sim_dict[i].loc[opt_s[j],'iv_'+opt_t[j].lower()] for j in np.arange(len(opt_t))], v1.expiry_dt)
        sim_dict[i]['px'] = s1.px
        sim_dict[i]['delta'] = s1.delta
        try:
            df_opt_strat.loc[-1] =  [i,  v1.tab_call[v1.tab_call['strikes'] == i]['ATM_K'].tolist()[0] ,np.dot(s1.px,df4['weight']),  np.dot(s1.delta,df4['weight']),  np.dot(s1.gamma,df4['weight']) , np.dot(s1.theta,df4['weight']), np.dot(s1.vega,df4['weight'])]
        except:
            df_opt_strat.loc[-1] = [i, v1.tab_put[v1.tab_put['strikes'] == i]['ATM_K'].tolist()[0], np.dot(s1.px, df4['weight']), np.dot(s1.delta, df4['weight']), np.dot(s1.gamma, df4['weight']), np.dot(s1.theta, df4['weight']), np.dot(s1.vega, df4['weight'])]
        df_opt_strat.index = df_opt_strat.index+1
        
    df_opt_strat.sort_values(by=['fut_px'], inplace=True)
    df_opt_strat.reset_index(drop=True, inplace= True)
    df_opt_strat['strat_px_fmt'] = [px_dec_to_opt_frac(df_opt_strat['strat_px'][i],64) for i in np.arange(len(df_opt_strat))]
    
    class bf_opt_strat_output():
        def __init__(self):
            self.vol = v1.tab
            self.vol_call = v1.tab_call
            self.vol_put = v1.tab_call
            self.ticker = t
            self.fut = v1.fut
            self.center = v1.center
            self.expiry_dt = v1.expiry_dt
            self.spot_px = v1.spot_px
            self.spot_px_fmt = v1.spot_px_fmt
            self.strat = df_opt_strat
            self.strat_name = s_name
            self.strat_px = st_px
            self.opt_dets = [t,opt_t,opt_s,opt_w]
            self.currency = v1.currency
            self.type = v1.type
    
    return bf_opt_strat_output()


#### get simulated option price for BF opt! 
def get_sim_option_px(ccy1, ref_date, sim_px, sim_opt_type, sim_strikes, sim_iv, sim_expiry ):
#    sim_px = 166
#    sim_opt_type = ['C','C']
#    sim_strikes = [168,170]
#    sim_iv = [9.84,10]
#    sim_expiry = v1.expiry_dt

    today = ql.Date(datetime.datetime.now().day,datetime.datetime.now().month,datetime.datetime.now().year)
    if ccy1 == 'USD':
        c = ccy('SOFR_DC',today)
    elif ccy1 == 'EUR':
        c = ccy('ESTER_DC',today)
    elif ccy1 == 'GBP':
        c = ccy('SONIA_DC',today)
    
#    div_rate = 0.0
    r = con.ref(c.fixing, ['PX_LAST'])['value'][0]/100
    day_count = ql.Actual365Fixed()
    calendar = c.cal
    
    calculation_date = ref_date
    ql.Settings.instance().evaluationDate = calculation_date
    
    sim_option_type_ql = []
    for i in np.arange(len(sim_opt_type)):
        if sim_opt_type[i] == 'C':
            sim_option_type_ql.append(ql.Option.Call)
        else:
            sim_option_type_ql.append(ql.Option.Put)

    spot_handle = ql.QuoteHandle(ql.SimpleQuote(sim_px))
    flat_ts = ql.YieldTermStructureHandle(ql.FlatForward(calculation_date, r, day_count))
#    div_ts = ql.YieldTermStructureHandle(ql.FlatForward(calculation_date, div_rate, day_count))
    
    sim_opt_delta = []
    sim_opt_gamma = []
    sim_opt_theta = []
    sim_opt_vega = []
    sim_opt_bs_px = []

    for i in np.arange(len(sim_opt_type)):
        opt_vol_ts = ql.BlackVolTermStructureHandle(ql.BlackConstantVol(calculation_date, calendar, sim_iv[i]/100, day_count))
        bsm_process = ql.BlackProcess(spot_handle, flat_ts, opt_vol_ts)
        payoff = ql.PlainVanillaPayoff(sim_option_type_ql[i], sim_strikes[i])
        exercise = ql.EuropeanExercise(sim_expiry)
        sim_option = ql.VanillaOption(payoff, exercise)
        sim_option.setPricingEngine(ql.AnalyticEuropeanEngine(bsm_process))
        
        sim_opt_bs_px.append(sim_option.NPV())
        sim_opt_delta.append(100*sim_option.delta())
        sim_opt_gamma.append(sim_option.gamma())
        sim_opt_theta.append(sim_option.theta())
        sim_opt_vega.append(sim_option.vega())
        
    class sim_option_px_output():
        def __init__(self):
            self.px = sim_opt_bs_px
            self.delta = sim_opt_delta
            self.gamma = sim_opt_gamma
            self.theta = sim_opt_theta
            self.vega = sim_opt_vega
    
    return sim_option_px_output()



###################### And now for STIR Vol Build ###############################################################################################################################################################################################################################################################################

def build_stir_vol_surf(chain_ticker, chain_len=[12,12], b=0):
    
#    chain_ticker = ['SFRM4P 96']
#    chain_len = [20,20]
#    b = 0

    chain_ticker = chain_ticker[0]+' Comdty'

    ccy1 = con.ref(chain_ticker, ['CRNCY'])['value'][0]
    if ccy1 == 'USD':
        if chain_ticker[:3] == 'SFR':
            fut = 'SFR'+con.ref(chain_ticker, ['OPT_UNDL_TICKER'])['value'][0][3:]+' Comdty'
            chain_filter = chain_ticker[:5]
        else:
            fut = 'SFR' + con.ref(chain_ticker, ['OPT_UNDL_TICKER'])['value'][0][2:] + ' Comdty'
            chain_filter = chain_ticker[:4]
    elif ccy1 == 'EUR':
        fut = 'ER'+con.ref(chain_ticker, ['OPT_UNDL_TICKER'])['value'][0][2:]+' Comdty'
        chain_filter = chain_ticker[:4]
    elif ccy1 == 'GBP':
        if chain_ticker[:3] == 'SFIR':
            fut = 'SFI'+con.ref(chain_ticker, ['OPT_UNDL_TICKER'])['value'][0][3:]+' Comdty'
            chain_filter = chain_ticker[:5]
        else:
            fut = 'SFI' + con.ref(chain_ticker, ['OPT_UNDL_TICKER'])['value'][0][2:] + ' Comdty'
            chain_filter = chain_ticker[:4]

    fut_1 = con.ref(chain_ticker, ['OPT_UNDL_TICKER'])['value'][0]+' Comdty'
    
    today = ql.Date(datetime.datetime.now().day,datetime.datetime.now().month,datetime.datetime.now().year)
    if ccy1 == 'USD':
        c = ccy('SOFR_DC',today)
    elif ccy1 == 'EUR':
        c = ccy('ESTER_DC',today)
    elif ccy1 == 'GBP':
        c = ccy('SONIA_DC',today)

    #### date handling for hist 
    #b=0
    if isinstance(b,int) == True:
        ref_date = c.cal.advance(today,b,ql.Days)
    else:
        ref_date = ql.Date(int(b.split('-')[0]),int(b.split('-')[1]),int(b.split('-')[2]))
    
    ref_date_1 = c.cal.advance(ref_date,-1,ql.Days)
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

    spot = con.bdh(fut, ['PX_LAST'],bbg_t, bbg_t, longdata=True)['value'][0]
    centre_strike = np.round(spot*16)/16
    

    df_chain = con.bulkref(fut_1, ['OPT_CHAIN'])

    if ((chain_ticker[:3] == 'SFR') or (chain_ticker[:3] == 'SFI')):
        df_chain['des'] = [df_chain['value'][i][:5] for i in np.arange(len(df_chain))]
        df_chain['opt_type'] = [df_chain['value'][i][5:6] for i in np.arange(len(df_chain))]
        df_chain['strike'] = [float(df_chain['value'][i][6:-6].strip()) for i in np.arange(len(df_chain))]
    else:
        df_chain['des'] = [df_chain['value'][i][:4] for i in np.arange(len(df_chain))]
        df_chain['opt_type'] = [df_chain['value'][i][4:5] for i in np.arange(len(df_chain))]
        df_chain['strike'] = [float(df_chain['value'][i][5:-6].strip()) for i in np.arange(len(df_chain))]
    df_chain = df_chain[df_chain['des'] == chain_filter]
    
    if len(df_chain[df_chain['strike'] == centre_strike]) == 0 :
        centre_strike = np.round(spot)
        idx1 = df_chain[df_chain['strike'] == centre_strike].index
    else:
        idx1 = df_chain[df_chain['strike'] == centre_strike].index

    ##### figuring out range of calls / puts strikes   /// different to bond fut opt vol build
    ### puts
    df_chain2 = df_chain.loc[(idx1[0]-chain_len[0]):idx1[0]+10]   ##### 10 == hardwriting the # ITM puts
    df_chain2.reset_index(drop = True, inplace = True)
    ### calls
    df_chain2 = df_chain2.append(df_chain.loc[idx1[1]-10:(idx1[1]+chain_len[1]+1)], ignore_index = True)  ##### 10 == hardwriting the # ITM puts

    ticker = df_chain2['des'][0]
    option_type = df_chain2['opt_type']
    strikes = df_chain2['strike']
    opt_type = df_chain2['opt_type']

    t2 = [ticker+option_type[i]+' '+str(strikes[i])+' Comdty' for i in np.arange(len(strikes))]
    expiry_dt = con.ref(t2[0], ['LAST_TRADEABLE_DT'])['value'][0]
    expiry_dt = ql.Date(expiry_dt.day,expiry_dt.month,expiry_dt.year)

    option_type_ql = []
    for i in np.arange(len(option_type)):
        if option_type[i] == 'C':
            option_type_ql.append(ql.Option.Put)
        else:
            option_type_ql.append(ql.Option.Call)

#### option modelling
#    div_rate = 0.0
    r = con.ref(c.fixing, ['PX_LAST'])['value'][0]/100
    day_count = ql.Actual365Fixed()
    calendar = c.cal

    calculation_date = ref_date
    ql.Settings.instance().evaluationDate = calculation_date

    volatility = 1.0
    spot_handle = ql.QuoteHandle(ql.SimpleQuote(100-spot))
    flat_ts = ql.YieldTermStructureHandle(ql.FlatForward(calculation_date, r, day_count))
#    div_ts = ql.YieldTermStructureHandle(ql.FlatForward(calculation_date, div_rate, day_count))
    flat_vol_ts = ql.BlackVolTermStructureHandle(ql.BlackConstantVol(calculation_date, calendar, volatility, day_count))
    bsm_process = ql.BlackProcess(spot_handle, flat_ts, flat_vol_ts)

    #### get closes after 10pm!
    now = datetime.datetime.now()
    today7am = now.replace(hour=7, minute=0, second=0, microsecond=0)
    today10pm = now.replace(hour=22, minute=0, second=0, microsecond=0)
    time_check = ((now > today7am) and (now < today10pm))

    if ((ref_date == today) and time_check):
        df1 = con.bdh(t2, ['PX_BID','PX_ASK'], bbg_date_str(calculation_date), bbg_date_str(calculation_date),longdata=True)
    elif ((ref_date == today) and (now > today10pm)):
        df1 = con.bdh(t2, ['PX_LAST'], bbg_date_str(calculation_date), bbg_date_str(calculation_date), longdata=True)
    elif ((ref_date == today) and (now < today7am)):
        df1 = con.bdh(t2, ['PX_LAST'], bbg_date_str(ref_date_1), bbg_date_str(ref_date_1), longdata=True)
    else:
        df1 = con.bdh(t2, ['PX_LAST'], bbg_date_str(calculation_date), bbg_date_str(calculation_date),longdata=True)

    opt_px = df1.groupby('ticker').value.mean()
    opt_px[opt_px < 1/64] = 0.5/64   ######## remove 0 prices for cab 
    
   
    df2 = pd.DataFrame()
    df2['ticker'] = t2
    df2['strikes'] = strikes
    df2['opt_type'] = option_type_ql

    df2['px'] = [opt_px[opt_px.index == t2[i]].values[0] for i in np.arange(len(opt_px))]
    df2['px_64'] = [px_opt_ticks(df2['px'][i]) for i in np.arange(len(opt_px))]
    df2['Yld'] = 100-df2['strikes']
    df2['ATM_K'] = 100*(spot-df2['strikes'])


    ### Vanilla + European+ Analytic
    opt_iv = []
    opt_delta = []
    opt_gamma = []
    opt_theta = []
    opt_vega = []
    opt_bs_px = []

    for i in np.arange(len(opt_px)):
        print(df2['ticker'][i])
        payoff = ql.PlainVanillaPayoff(option_type_ql[i], 100-strikes[i])
        exercise = ql.EuropeanExercise(expiry_dt)
        option = ql.VanillaOption(payoff, exercise)
    
        option.setPricingEngine(ql.AnalyticEuropeanEngine(bsm_process))

        opt_iv.append(100*option.impliedVolatility(df2['px'][i], bsm_process,  maxEvaluations= 100000, minVol = 0.0000000000001, maxVol = 1000.0 ))
        opt_vol_ts = ql.BlackVolTermStructureHandle(ql.BlackConstantVol(calculation_date, calendar, opt_iv[i]/100, day_count))
        bsm_process = ql.BlackProcess(spot_handle, flat_ts, opt_vol_ts)
        option.setPricingEngine(ql.AnalyticEuropeanEngine(bsm_process))
    
        opt_bs_px.append(option.NPV())
        opt_delta.append(-100*option.delta())
        opt_gamma.append(option.gamma())
        opt_theta.append(option.theta())
        opt_vega.append(option.vega())
        
    df2['bs_px'] = opt_bs_px
    df2['iv'] = opt_iv
    df2['delta'] = opt_delta
    df2['gamma'] = opt_gamma
    df2['theta'] = opt_theta
    df2['vega'] = opt_vega
    
    class stir_vol_surf_output():
        def __init__(self):
            self.tab = df2
            self.tab_call = df2[df2['opt_type'] == -1]
            self.tab_put = df2[df2['opt_type'] == 1]
            self.ticker = chain_ticker
            self.center = centre_strike
            self.expiry_dt = expiry_dt
            self.fut = fut
            self.spot_px = spot
            self.spot_px_fmt = px_dec_to_frac(spot)
            self.ref_date = ref_date
            self.currency = ccy1
    
    return stir_vol_surf_output()

#v1 = build_stir_vol_surf(['SFRM4P 96'], chain_len=[20,20], b=0)
#v1 = build_stir_vol_surf(['EDZ2P 98.75'], chain_len=[9,9], b =0)
#v1.tab


def stir_opt_strat(t, opt_t, opt_s, opt_w, s_range = [-0.25,0.25], increm = 0.125, s_name = 'strategy', built_surf = 0, chain_len = [10,10]):
#    t = ['0QU4']
#    opt_t = ['C','C']
#    opt_s = [97,97.5]
#    opt_w = [1,-2]
#    increm = 0.125
#    s_range = [-0.25,0.25]
#    s_name = '0EJ2'
#    chain_len= [8,8]
    opt_t2 = []
    for i in opt_t:   ##### weird reversal due to ql. futpx -> rate methodology !!
        if i == 'C':
            opt_t2.append(-1)
        else:
            opt_t2.append(1)

    if built_surf == 0:
        v1 = build_stir_vol_surf([t[0]+opt_t[0]+' '+str(opt_s[0])], chain_len, b = 0)  ##### MAKE SURE NO DATES  ie no b !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    else:
        v1 = built_surf
#    v1.tab
    
    df4 = pd.DataFrame()
    for i in np.arange(len(opt_t2)):
        df4 = df4.append(v1.tab[(v1.tab['opt_type'] == opt_t2[i]) & (v1.tab['strikes'] == opt_s[i])], ignore_index = True)
        
    df4['weight'] = opt_w
    st_px = np.dot(df4['bs_px'],df4['weight'])
    
    df_opt_strat = pd.DataFrame()
    df_opt_strat['fut_px'] = [v1.spot_px]
    df_opt_strat['ATM_K'] = np.array([0.0])
    df_opt_strat['strat_px'] = st_px
    df_opt_strat['strat_delta'] = np.dot(df4['delta'],df4['weight'])
    df_opt_strat['strat_gamma'] = np.dot(df4['gamma'],df4['weight'])
    df_opt_strat['strat_theta'] = np.dot(df4['theta'],df4['weight'])
    df_opt_strat['strat_vega'] = np.dot(df4['vega'],df4['weight'])
    
    sim_range = np.arange(min(opt_s+[v1.center])+s_range[0],max(opt_s+[v1.center])+s_range[1]+increm, increm)
    
    sim_dict = {}
    for i in sim_range:
        print(i)
 #       i = 98.25
        df_all = build_vol_spline(v1.ticker.split()[0][:-1], i, v1)
        sim_dict[i] = df_all.loc[opt_s]
        s1 = get_sim_stir_option_px(v1.currency, v1.ref_date, i, opt_t, opt_s, [sim_dict[i].loc[opt_s[j],'iv_'+opt_t[j].lower()] for j in np.arange(len(opt_t))], v1.expiry_dt)
        sim_dict[i]['px'] = s1.px
        sim_dict[i]['delta'] = s1.delta
        try:
            df_opt_strat.loc[-1] =  [i,  v1.tab_call[v1.tab_call['strikes'] == i]['ATM_K'].tolist()[0] ,np.dot(s1.px,df4['weight']), np.dot(s1.delta,df4['weight']),
                                     np.dot(s1.gamma,df4['weight']) , np.dot(s1.theta,df4['weight']), np.dot(s1.vega,df4['weight'])]
        except:
            df_opt_strat.loc[-1] = [i, v1.tab_put[v1.tab_put['strikes'] == i]['ATM_K'].tolist()[0], np.dot(s1.px, df4['weight']), np.dot(s1.delta, df4['weight']),
                                    np.dot(s1.gamma, df4['weight']), np.dot(s1.theta, df4['weight']), np.dot(s1.vega, df4['weight'])]
        df_opt_strat.index = df_opt_strat.index+1
        
    df_opt_strat.sort_values(by=['fut_px'], inplace=True)
    df_opt_strat.reset_index(drop=True, inplace= True)
    df_opt_strat['strat_px_fmt'] = 100*df_opt_strat['strat_px'].round(4)
    
    class stir_opt_strat_output():
        def __init__(self):
            self.vol = v1.tab
            self.vol_call = v1.tab_call
            self.vol_put = v1.tab_call
            self.ticker = t
            self.fut = v1.fut
            self.center = v1.center
            self.expiry_dt = v1.expiry_dt
            self.spot_px = v1.spot_px
            self.spot_px_fmt = v1.spot_px_fmt
            self.strat = df_opt_strat
            self.strat_name = s_name
            self.strat_px = st_px
            self.opt_dets = [t,opt_t,opt_s,opt_w]
            self.currency = v1.currency
            self.type = 'stir'
    
    return stir_opt_strat_output()

#st =  stir_opt_strat(['0EH2'],['P','P'], [98.375, 98], [1, -1], s_range = [0,0.25], increm = 0.125, s_name = '0EH2 PS', chain_len = [10,10])
#st.strat


def get_sim_stir_option_px(ccy1, ref_date, sim_px, sim_opt_type, sim_strikes, sim_iv, sim_expiry):
    #    sim_px = 166
    #    sim_opt_type = ['C','C']
    #    sim_strikes = [168,170]
    #    sim_iv = [9.84,10]
    #    sim_expiry = v1.expiry_dt

    today = ql.Date(datetime.datetime.now().day, datetime.datetime.now().month, datetime.datetime.now().year)
    if ccy1 == 'USD':
        c = ccy('SOFR_DC', today)
    elif ccy1 == 'EUR':
        c = ccy('ESTER_DC', today)
    elif ccy1 == 'GBP':
        c = ccy('SONIA_DC', today)

    #    div_rate = 0.0
    r = con.ref(c.fixing, ['PX_LAST'])['value'][0] / 100
    day_count = ql.Actual365Fixed()
    calendar = c.cal

    calculation_date = ref_date
    ql.Settings.instance().evaluationDate = calculation_date

    sim_option_type_ql = []
    for i in np.arange(len(sim_opt_type)):
        if sim_opt_type[i] == 'C':
            sim_option_type_ql.append(ql.Option.Put)
        else:
            sim_option_type_ql.append(ql.Option.Call)

    spot_handle = ql.QuoteHandle(ql.SimpleQuote(100 - sim_px))
    flat_ts = ql.YieldTermStructureHandle(ql.FlatForward(calculation_date, r, day_count))
    #    div_ts = ql.YieldTermStructureHandle(ql.FlatForward(calculation_date, div_rate, day_count))

    sim_opt_delta = []
    sim_opt_gamma = []
    sim_opt_theta = []
    sim_opt_vega = []
    sim_opt_bs_px = []

    for i in np.arange(len(sim_opt_type)):
        opt_vol_ts = ql.BlackVolTermStructureHandle(
            ql.BlackConstantVol(calculation_date, calendar, sim_iv[i] / 100, day_count))
        bsm_process = ql.BlackProcess(spot_handle, flat_ts, opt_vol_ts)
        payoff = ql.PlainVanillaPayoff(sim_option_type_ql[i], 100 - sim_strikes[i])
        exercise = ql.EuropeanExercise(sim_expiry)
        sim_option = ql.VanillaOption(payoff, exercise)
        sim_option.setPricingEngine(ql.AnalyticEuropeanEngine(bsm_process))

        sim_opt_bs_px.append(sim_option.NPV())
        sim_opt_delta.append(-100 * sim_option.delta())
        sim_opt_gamma.append(sim_option.gamma())
        sim_opt_theta.append(sim_option.theta())
        sim_opt_vega.append(sim_option.vega())

    class sim_stir_option_px_output():
        def __init__(self):
            self.px = sim_opt_bs_px
            self.delta = sim_opt_delta
            self.gamma = sim_opt_gamma
            self.theta = sim_opt_theta
            self.vega = sim_opt_vega

    return sim_stir_option_px_output()




