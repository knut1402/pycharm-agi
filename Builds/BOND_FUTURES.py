###### Bond futures options
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
##### getting bond future price and implied yield


### find CTD
con.ref('USU1 Comdty', ['FUT_CTD_ISIN'])['value'][0]

### find last del date
con.ref('USU1 Comdty', ['FUT_DLV_DT_LAST'])['value'][0]

#### find conversion ratio
con.ref('USU1 Comdty', ['FUT_CNVS_FACTOR'])['value'][0]

#### CTD Yield ### use CF and fwd settle date ovrd

fwd_px = con.ref('USU1 Comdty', ['PX_LAST'])['value'][0]*con.ref('USU1 Comdty', ['FUT_CNVS_FACTOR'])['value'][0]

con.ref('US912810PU60 Govt', ['YAS_BOND_YLD','YLD_YTM_BID'], ovrds =[('PX_BID','140'),(('SETTLE_DT','20210930'))])

con.ref('US912810PU60 Govt', ['YLD_YTM_BID'], ovrds =[('PX_BID',fwd_px),
                    (('SETTLE_DT',bbg_date_str(con.ref('USU1 Comdty', ['FUT_DLV_DT_LAST'])['value'][0], ql_date=0)))])


##### function bond future yield
bond_fut_yield('USU1',[167.5, 169.5, 171.5])
######################################################## OPTIONS PRICER FROM VOL SURF BUILD

ticker = 'USU1'
option_type = ['C','C','C']  
strikes = [165,168,171]
weights = [1,-2,1]
t2 = [ticker+option_type[i]+' '+str(float(strikes[i]))+' Comdty' for i in np.arange(len(strikes))]

v1 = build_vol_surf([ticker+option_type[0]+' '+str(strikes[0])], chain_len=12)
v1.spot_px
df3 = v1.tab[v1.tab['ticker'].isin(t2)]
df3.reset_index(drop=True, inplace=True)
df3['weights'] = weights

opt_strat = pd.DataFrame() 
opt_strat['px']= np.array([px_opt_ticks(np.dot(df3['px'],df3['weights']))])
opt_strat['delta'] = np.array([np.dot(df3['delta'],df3['weights'])])
opt_strat['gamma'] = np.array([np.dot(df3['gamma'],df3['weights'])])
opt_strat['theta'] = np.array([np.dot(df3['theta'],df3['weights'])])



################ building shifts (delta)
spot_sim = np.arange(np.min(strikes)-8,np.max(strikes)+8, step =0.5)
spot_yld_sim = bond_fut_yield(v1.fut[:4], spot_sim)

df4 = v1.tab[['ATM_K','iv']]
df6 = pd.DataFrame()

for i in np.arange(len(spot_yld_sim)):
    shift1 = 100*(bond_fut_yield(v1.fut[:4], strikes)['K_Yield'] - spot_yld_sim.loc[i]['K_Yield'])
    
    iv_new = []
    for j in np.arange(len(shift1)):
        df5 = df4.iloc[(df4['ATM_K']-shift1[j]).abs().argsort()[:2]]
        iv_new.append(np.interp(shift1[j], df5['ATM_K'], df5['iv']))
    
    t1 = get_bsm_px_from_vol(ticker, option_type, strikes, weights, iv_new, spot_sim[i])
    df6 = df6.append(t1, ignore_index = True)

df6



############################# OPTION BY CHAIN / EXPIRY DATE
chain_ticker = ['3CN1C 160']
chain_ticker = chain_ticker[0]+' Comdty'
fut = con.ref(chain_ticker, ['OPT_UNDL_TICKER'])['value'][0]+' Comdty'
spot =  con.ref(fut, ['PX_LAST'])['value'][0]
centre_strike = np.round(spot*2)/2

df_chain = con.bulkref(fut, ['OPT_CHAIN'])

df_chain['des'] = [df_chain['value'][i][:4] for i in np.arange(len(df_chain))]
df_chain['opt_type'] = [df_chain['value'][i][4:5] for i in np.arange(len(df_chain))]
df_chain['strike'] = [float(df_chain['value'][i][5:-6].strip()) for i in np.arange(len(df_chain))]

idx1 = df_chain[df_chain['strike'] == centre_strike].index
df_chain2 = df_chain[(idx1[0]-20):idx1[0]+1]
df_chain2.reset_index(drop = True, inplace = True)
df_chain2 = df_chain2.append(df_chain[idx1[1]:(idx1[1]+20+1)], ignore_index = True)



ticker = df_chain2['des'][0]
option_type = df_chain2['opt_type']
strikes = df_chain2['strike']
weights = np.repeat(1,len(df_chain2))



########################################### BUILD SURFACE !! 
def build_vol_surf(chain_ticker, chain_len=[12,12]):
    
    chain_ticker = ['1MV1P 131.5']
    chain_len = [16,4]
    chain_ticker = chain_ticker[0]+' Comdty'
    chain_filter = chain_ticker[:4]
    
    fut = con.ref(chain_ticker, ['OPT_UNDL_TICKER'])['value'][0]+' Comdty'
    spot =  con.ref(fut, ['PX_LAST'])['value'][0]
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
    
    df_chain2 = df_chain.loc[(idx1[0]-chain_len[0]):idx1[0]+chain_len[1]+1]
    df_chain2.reset_index(drop = True, inplace = True)
    df_chain2 = df_chain2.append(df_chain.loc[idx1[1]-chain_len[0]:(idx1[1]+chain_len[1]+1)], ignore_index = True)

    ticker = df_chain2['des'][0]
    option_type = df_chain2['opt_type']
    strikes = df_chain2['strike']
    opt_type = df_chain2['opt_type']

    t2 = [ticker+option_type[i]+' '+str(strikes[i])+' Comdty' for i in np.arange(len(strikes))]
    expiry_dt = con.ref(t2[0], ['LAST_TRADEABLE_DT'])['value'][0]
    expiry_dt = ql.Date(expiry_dt.day,expiry_dt.month,expiry_dt.year)
    fut = con.ref(t2[0], ['OPT_UNDL_TICKER'])['value'][0]+' Comdty'
    spot =  con.ref(fut, ['PX_LAST'])['value'][0]

    option_type_ql = []
    for i in np.arange(len(option_type)):
        if option_type[i] == 'C':
            option_type_ql.append(ql.Option.Call)
        else:
            option_type_ql.append(ql.Option.Put)

#### option modelling
    div_rate = 0.0
    r = con.ref('FEDL01 Index', ['PX_LAST'])['value'][0]/100
    day_count = ql.Actual365Fixed()
    calendar = ql.UnitedStates()

    calculation_date = ql.Date(datetime.datetime.now().day,datetime.datetime.now().month,datetime.datetime.now().year)
    ql.Settings.instance().evaluationDate = calculation_date

    volatility = 0.05
    spot_handle = ql.QuoteHandle(ql.SimpleQuote(spot))
    flat_ts = ql.YieldTermStructureHandle(ql.FlatForward(calculation_date, r, day_count))
    div_ts = ql.YieldTermStructureHandle(ql.FlatForward(calculation_date, div_rate, day_count))
    flat_vol_ts = ql.BlackVolTermStructureHandle(ql.BlackConstantVol(calculation_date, calendar, volatility, day_count))
    bsm_process = ql.BlackScholesMertonProcess(spot_handle, div_ts, flat_ts, flat_vol_ts)

    df1 = con.bdh(t2, ['PX_BID','PX_ASK'], bbg_date_str(calculation_date), bbg_date_str(calculation_date),longdata=True)
    opt_px = df1.groupby('ticker').value.mean()
    opt_px[opt_px < 1/64] = 0.5/64   ######## remove 0 prices for cab 
    
    
    df2 = pd.DataFrame()
    df2['ticker'] = t2
    df2['strikes'] = strikes
    df2['opt_type'] = opt_type    
    df2['px'] = [opt_px[opt_px.index == t2[i]].values[0] for i in np.arange(len(opt_px))]
    df2['px_64'] = [px_opt_ticks(df2['px'][i]) for i in np.arange(len(opt_px))]
    #df2['px_bid'] = [px_opt_ticks(df1[(df1['ticker'] == t2[i]) & (df1['field'] == 'PX_BID') ]['value']) for i in np.arange(len(t2))]
    #df2['px_ask'] = [px_opt_ticks(df1[(df1['ticker'] == t2[i]) & (df1['field'] == 'PX_ASK') ]['value']) for i in np.arange(len(t2))]
    #df2['px_bid'] = [px_opt_ticks(df1[df1['field'] == 'PX_BID']['value'].tolist()[i]) for i in np.arange(len(opt_px))]
    #df2['px_ask'] = [px_opt_ticks(df1[df1['field'] == 'PX_ASK']['value'].tolist()[i]) for i in np.arange(len(opt_px))]

    df3 = bond_fut_yield(fut[:4],strikes)
    df2['Yld'] = df3['K_Yield']
    df2['ATM_K'] = df3['K_Dist']


    ### Vanilla + European+ Analytic
    opt_iv = []
    opt_delta = []
    opt_gamma = []
    opt_theta = []
    opt_vega = []
    opt_bs_px = []

    for i in np.arange(len(opt_px)):
#        print(df2['ticker'][i])
        payoff = ql.PlainVanillaPayoff(option_type_ql[i], strikes[i])
        exercise = ql.EuropeanExercise(expiry_dt)
        option = ql.VanillaOption(payoff, exercise)
    
        option.setPricingEngine(ql.AnalyticEuropeanEngine(bsm_process))

        opt_iv.append(100*option.impliedVolatility(df2['px'][i], bsm_process, maxVol = 100))
        opt_vol_ts = ql.BlackVolTermStructureHandle(ql.BlackConstantVol(calculation_date, calendar, opt_iv[i]/100, day_count))
        bsm_process = ql.BlackScholesMertonProcess(spot_handle, div_ts, flat_ts, opt_vol_ts)
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
    
    class vol_surf_output():
        def __init__(self):
            self.tab = df2
            self.tab_call = df2[df2['opt_type'] == 'C']
            self.tab_put = df2[df2['opt_type'] == 'P']
            self.ticker = chain_ticker
            self.center = centre_strike
            self.expiry_dt = expiry_dt
            self.fut = fut
            self.spot_px = spot
            self.spot_px_fmt = px_dec_to_frac(spot)
    
    return vol_surf_output()

v1 = build_vol_surf(['1MV1P 131.5'], chain_len=[12,6])

v1.tab_call
v1.expiry_dt
v1.fut
v1.spot_px


#################### build vol spline 
def build_vol_spline(fut, sim_spot, a):
#    fut = 'TYZ1'
#    sim_spot = 130
#    a = v1
   
    df3 = pd.DataFrame(index = a.tab_call['strikes'])
    df3['ATM_K'] = np.array(a.tab_call['ATM_K'] - a.tab_call[a.tab_call['strikes'] == sim_spot]['ATM_K'].tolist())   
    df3['iv_c'] = np.interp(df3['ATM_K'], a.tab_call['ATM_K'][::-1], a.tab_call['iv'][::-1])
    df3['iv_p'] = np.interp(df3['ATM_K'], a.tab_call['ATM_K'][::-1], a.tab_put['iv'][::-1])
    
    return df3



def bond_fut_opt_strat(t,opt_t,opt_s,opt_w, s_range = [-3,3], increm = 0.5, s_name = 'strategy', chain_len = [12,12]):
#    t = ['1MV1']
#    opt_t = ['P','P','P']
#    opt_s = [131.5,130.5,130]
#    opt_w = [1,-2,1]
#    increm = 0.5
#    s_range = [0,2]
#    s_name = 'TYU1 PS'
#   chain_len= [10,6]
    
    v1 = build_vol_surf([t[0]+opt_t[0]+' '+str(opt_s[0])], chain_len)
    #v1.tab
    
    df4 = pd.DataFrame()
    for i in np.arange(len(opt_t)):
        df4 = df4.append(v1.tab[(v1.tab['opt_type'] == opt_t[i]) & (v1.tab['strikes'] == opt_s[i])], ignore_index = True)
        
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
    
    sim_range = np.arange(min(opt_s)+s_range[0],max(opt_s)+s_range[1],increm)
    
    sim_dict = {}
    for i in sim_range:
#        print(i)
#        i = 130.0
        df_all = build_vol_spline(v1.fut[:4], i, v1)
        sim_dict[i] = df_all.loc[opt_s]
        s1 = get_sim_option_px(i, opt_t, opt_s, [sim_dict[i].loc[opt_s[j],'iv_'+opt_t[j].lower()] for j in np.arange(len(opt_t))], v1.expiry_dt)
        sim_dict[i]['px'] = s1.px
        sim_dict[i]['delta'] = s1.delta
        df_opt_strat.loc[-1] =  [i,  v1.tab_call[v1.tab_call['strikes'] == i]['ATM_K'].tolist()[0] ,np.dot(s1.px,df4['weight']),  np.dot(s1.delta,df4['weight']),  np.dot(s1.gamma,df4['weight']) , np.dot(s1.theta,df4['weight']), np.dot(s1.vega,df4['weight'])] 
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
    
    return bf_opt_strat_output()


ty1 = bond_fut_opt_strat(['1MV1'],['P','P','P'],[131.5,131,130.5],[1,-2,1], s_range = [0,3], increm = 0.5,  chain_len = [12,6])

us_cs.strat
us_cs.expiry_dt
us_cs.vol
us_cs.opt_dets



    
plt.plot(df_opt_strat['fut_px'],df_opt_strat['strat_px'])
plt.plot(df_opt_strat['fut_px'],df_opt_strat['strat_delta'])




#### get simulated option price! 
def get_sim_option_px(sim_px, sim_opt_type, sim_strikes, sim_iv, sim_expiry ):
#    sim_px = 166
#    sim_opt_type = ['C','C']
#    sim_strikes = [168,170]
#    sim_iv = [9.84,10]
#    sim_expiry = v1.expiry_dt
    
    div_rate = 0.0
    r = con.ref('FEDL01 Index', ['PX_LAST'])['value'][0]/100
    day_count = ql.Actual365Fixed()
    calendar = ql.UnitedStates()
    calculation_date = ql.Date(datetime.datetime.now().day,datetime.datetime.now().month,datetime.datetime.now().year)
    ql.Settings.instance().evaluationDate = calculation_date
    
    sim_option_type_ql = []
    for i in np.arange(len(sim_opt_type)):
        if sim_opt_type[i] == 'C':
            sim_option_type_ql.append(ql.Option.Call)
        else:
            sim_option_type_ql.append(ql.Option.Put)

    spot_handle = ql.QuoteHandle(ql.SimpleQuote(sim_px))
    flat_ts = ql.YieldTermStructureHandle(ql.FlatForward(calculation_date, r, day_count))
    div_ts = ql.YieldTermStructureHandle(ql.FlatForward(calculation_date, div_rate, day_count))
    
    sim_opt_delta = []
    sim_opt_gamma = []
    sim_opt_theta = []
    sim_opt_vega = []
    sim_opt_bs_px = []

    for i in np.arange(len(sim_opt_type)):
        opt_vol_ts = ql.BlackVolTermStructureHandle(ql.BlackConstantVol(calculation_date, calendar, sim_iv[i]/100, day_count))
        bsm_process = ql.BlackScholesMertonProcess(spot_handle, div_ts, flat_ts, opt_vol_ts)
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

            








#################### plottign vol 

import matplotlib.pyplot as plt
#from mpldatacursor import datacursor
#import mplcursors

### parsing vol spline
vol_s = v1.tab_call
vol_s.reset_index(drop=True, inplace=True)

vol_s2 = v1.tab_put
vol_s2.reset_index(drop=True, inplace=True)


fig = plt.figure(figsize=[16,12])
#fig.subplots_adjust(top=0.8)
ax1 = fig.add_subplot(211)
ax1.set_ylabel('imp. vol.')
#ax1.set_title('opt vol')

x1 = -vol_s['ATM_K']
y1 = vol_s['iv']
#ax1.scatter(x1, y, lw=2)

sc1 = ax1.scatter(x1, y1, marker = 'x', s = 9)
#sc1 = ax1.plot(x1, y, marker = 'x', markersize = 5)

ax1.tick_params(axis='both', which='major', labelsize=9)
new_labels = [str(vol_s['strikes'][i])+'\n\n'+str(np.round(vol_s['ATM_K'][i],1))+'\n\n'+str(np.round(vol_s['delta'][i],1)) for i in np.arange(len(vol_s))][0:-1:2]
ax1.set_xticks(x1.tolist()[0:-1:2])
ax1.set_xticklabels(new_labels)
#mplcursors.cursor(sc1)
#datacursor(sc1)
ax2 = fig.add_subplot(212)
ax2.set_ylabel('imp. vol.')
#ax1.set_title('opt vol')

x2 = -vol_s2['ATM_K']
y2 = vol_s2['iv']
#ax1.scatter(x1, y, lw=2)

sc2 = ax2.scatter(x2, y2, marker = 'x', s = 9, color = 'r')
#sc1 = ax1.plot(x1, y, marker = 'x', markersize = 5)

ax2.tick_params(axis='both', which='major', labelsize=9)
new_labels2 = [str(vol_s2['strikes'][i])+'\n\n'+str(np.round(vol_s2['ATM_K'][i],1))+'\n\n'+str(np.round(vol_s2['delta'][i],1)) for i in np.arange(len(vol_s2))][0:-1:2]
ax2.set_xticks(x2.tolist()[0:-1:2])
ax2.set_xticklabels(new_labels2)


plt.show()






###### Utilities  !!!



################################################################################################ options via Quanlib

# option data
maturity_date = ql.Date(27, 8, 2021)
spot_price = 160+(30/32)
strike_price = 163
volatility = 0.0817 # the historical vols for a year
dividend_rate =  0.0
option_type = ql.Option.Call

risk_free_rate = 0.001
day_count = ql.Actual365Fixed()
calendar = ql.UnitedStates()

calculation_date = ql.Date(6, 7, 2021)
ql.Settings.instance().evaluationDate = calculation_date

### Vanilla + European+ Analytic
payoff = ql.PlainVanillaPayoff(option_type, strike_price)
exercise = ql.EuropeanExercise(maturity_date)
option = ql.VanillaOption(payoff, exercise)

spot_handle = ql.QuoteHandle(ql.SimpleQuote(spot_price))
flat_ts = ql.YieldTermStructureHandle(ql.FlatForward(calculation_date, risk_free_rate, day_count))
dividend_yield = ql.YieldTermStructureHandle(ql.FlatForward(calculation_date, dividend_rate, day_count))
flat_vol_ts = ql.BlackVolTermStructureHandle(ql.BlackConstantVol(calculation_date, calendar, volatility, day_count))
bsm_process = ql.BlackScholesMertonProcess(spot_handle, dividend_yield, flat_ts, flat_vol_ts)

option.setPricingEngine(ql.AnalyticEuropeanEngine(bsm_process))
bs_price = option.NPV()
bs_price*64

option.impliedVolatility(74/64, bsm_process)

option.delta()
option.gamma()
option.theta()
option.vega()

##### Vanilla + European + MC
steps = 2
rng = "pseudorandom"
numPaths = 100000

option.setPricingEngine(ql.MCEuropeanEngine(bsm_process,rng,steps, requiredSamples=numPaths))
bs_price = option.NPV()
bs_price*64

option.impliedVolatility(38/64, bsm_process)

#### doesn't WORK ! 
option.delta()
option.gamma()
option.theta()
option.vega()

##### Vanilla + European + FdBlackScholes
tGrid, xGrid = 2000, 200
option.setPricingEngine(ql.FdBlackScholesVanillaEngine(bsm_process,tGrid,xGrid))
bs_price = option.NPV()
bs_price*64

option.impliedVolatility(38/64, bsm_process)


option.delta()
option.gamma()
option.theta()
option.vega() #### doesnot work


##### Vanilla + European + AnalyticHeston
v0 = 0.005
kappa = 0.8
theta = 0.008
rho = 0.2
sigma = 0.08
heston_process = ql.HestonProcess(flat_ts, dividend_yield, spot_handle, v0, kappa, theta, sigma, rho)
heston_model = ql.HestonModel(heston_process)
option.setPricingEngine(ql.AnalyticHestonEngine(heston_model))
bs_price = option.NPV()
bs_price*64

option.impliedVolatility(38/64, bsm_process)

#### does not Work! 
option.delta()
option.gamma()
option.theta()
option.vega() 


##### Vanilla + American + FdBlackScholes

exercise = ql.AmericanExercise(calculation_date,maturity_date)
option = ql.VanillaOption(payoff, exercise)

tGrid, xGrid = 2000, 200
option.setPricingEngine(ql.FdBlackScholesVanillaEngine(bsm_process,tGrid,xGrid))
bs_price = option.NPV()
bs_price*64

option.impliedVolatility(38/64, bsm_process)


option.delta()
option.gamma()
option.theta()
option.vega() #### doesnot work


##### Vanilla + American + MCAmericanEngine
exercise = ql.AmericanExercise(calculation_date,maturity_date)
option = ql.VanillaOption(payoff, exercise)

steps = 200
rng = "pseudorandom"
numPaths = 100000
option.setPricingEngine(ql.MCAmericanEngine(bsm_process,rng,steps, requiredSamples=numPaths))

bs_price = option.NPV()
bs_price*64

option.impliedVolatility(38/64, bsm_process)

### doesnot work! 
option.delta()
option.gamma()
option.theta()
option.vega()

############################################################ OPTIONS PRICER get price from vol

def get_bsm_px_from_vol(ticker, option_type, strikes, weights, vol, spot = 0):
    
#    ticker = 'USU1'
#    option_type = ['C','C','C']  
#    strikes = [165,168,171]
#    weights = [1,-2,1]
#    vol = iv_new
#    spot =  spot_sim[i]

    t2 = [ticker+option_type[i]+' '+str(strikes[i])+' Comdty' for i in np.arange(len(strikes))]
    expiry_dt = con.ref(t2[0], ['LAST_TRADEABLE_DT'])['value'][0]
    expiry_dt = ql.Date(expiry_dt.day,expiry_dt.month,expiry_dt.year)
    fut = con.ref(t2[0], ['OPT_UNDL_TICKER'])['value'][0]+' Comdty'
    
    option_type_ql = []
    for i in np.arange(len(option_type)):
        if option_type[i] == 'C':
            option_type_ql.append(ql.Option.Call)
        else:
            option_type_ql.append(ql.Option.Put)
    

#### option modelling
    div_rate = 0.0
    r = con.ref('FEDL01 Index', ['PX_LAST'])['value'][0]/100
    day_count = ql.Actual365Fixed()
    calendar = ql.UnitedStates()

    calculation_date = ql.Date(datetime.datetime.now().day,datetime.datetime.now().month,datetime.datetime.now().year)
    ql.Settings.instance().evaluationDate = calculation_date

    volatility = 0.05
    spot_handle = ql.QuoteHandle(ql.SimpleQuote(spot))
    flat_ts = ql.YieldTermStructureHandle(ql.FlatForward(calculation_date, r, day_count))
    div_ts = ql.YieldTermStructureHandle(ql.FlatForward(calculation_date, div_rate, day_count))
    flat_vol_ts = ql.BlackVolTermStructureHandle(ql.BlackConstantVol(calculation_date, calendar, volatility, day_count))
    bsm_process = ql.BlackScholesMertonProcess(spot_handle, div_ts, flat_ts, flat_vol_ts)

    opt_iv = []
    opt_delta = []
    opt_gamma = []
    opt_theta = []
    opt_vega = []
    opt_bs_px = []

    for i in np.arange(len(strikes)):
        payoff = ql.PlainVanillaPayoff(option_type_ql[i], strikes[i])
        exercise = ql.EuropeanExercise(expiry_dt)
        option = ql.VanillaOption(payoff, exercise)
    
        option.setPricingEngine(ql.AnalyticEuropeanEngine(bsm_process))
        opt_vol_ts = ql.BlackVolTermStructureHandle(ql.BlackConstantVol(calculation_date, calendar, vol[i]/100, day_count))
        bsm_process = ql.BlackScholesMertonProcess(spot_handle, div_ts, flat_ts, opt_vol_ts)
        option.setPricingEngine(ql.AnalyticEuropeanEngine(bsm_process))
    
        opt_bs_px.append(option.NPV())
        opt_delta.append(100*option.delta())
        opt_gamma.append(option.gamma())
        opt_theta.append(option.theta())
        opt_vega.append(option.vega())

    df2 = pd.DataFrame()
    df2['bs_px'] = opt_bs_px
    df2['delta'] = opt_delta
    df2['gamma'] = opt_gamma
    df2['theta'] = opt_theta
    df2['vega'] = opt_vega
    df2['weights'] = weights


    opt_strat = pd.DataFrame() 
    opt_strat['px']= np.array([px_opt_ticks(np.dot(df2['bs_px'],df2['weights']))])
    opt_strat['delta'] = np.array([np.dot(df2['delta'],df2['weights'])])
    opt_strat['gamma'] = np.array([np.dot(df2['gamma'],df2['weights'])])
    opt_strat['theta'] = np.array([np.dot(df2['theta'],df2['weights'])])
    
    return opt_strat




############################################################ OPTIONS PRICER  w/o building surface first

ticker = 'USU1'
option_type = ['C','C','C']  
strikes = [165,168,171]
weights = [1,-2,1]

t2 = [ticker+option_type[i]+' '+str(strikes[i])+' Comdty' for i in np.arange(len(strikes))]
expiry_dt = con.ref(t2[0], ['LAST_TRADEABLE_DT'])['value'][0]
expiry_dt = ql.Date(expiry_dt.day,expiry_dt.month,expiry_dt.year)
fut = con.ref(t2[0], ['OPT_UNDL_TICKER'])['value'][0]+' Comdty'
spot =  con.ref(fut, ['PX_LAST'])['value'][0]

option_type_ql = []
for i in np.arange(len(option_type)):
    if option_type[i] == 'C':
        option_type_ql.append(ql.Option.Call)
    else:
        option_type_ql.append(ql.Option.Put)
    


#### option modelling
div_rate = 0.0
r = con.ref('FEDL01 Index', ['PX_LAST'])['value'][0]/100
day_count = ql.Actual365Fixed()
calendar = ql.UnitedStates()

calculation_date = ql.Date(datetime.datetime.now().day,datetime.datetime.now().month,datetime.datetime.now().year)
ql.Settings.instance().evaluationDate = calculation_date

volatility = 0.05
spot_handle = ql.QuoteHandle(ql.SimpleQuote(spot))
flat_ts = ql.YieldTermStructureHandle(ql.FlatForward(calculation_date, r, day_count))
div_ts = ql.YieldTermStructureHandle(ql.FlatForward(calculation_date, div_rate, day_count))
flat_vol_ts = ql.BlackVolTermStructureHandle(ql.BlackConstantVol(calculation_date, calendar, volatility, day_count))
bsm_process = ql.BlackScholesMertonProcess(spot_handle, div_ts, flat_ts, flat_vol_ts)

df1 = con.bdh(t2, ['PX_BID','PX_ASK'], '20210706', '20210706',longdata=True)
opt_px = df1.groupby('ticker').value.mean()

df2 = pd.DataFrame()
df2['ticker'] = t2
df2['px'] = [opt_px[opt_px.index == t2[i]].values[0] for i in np.arange(len(opt_px))]
df2['px_64'] = [px_opt_ticks(df2['px'][i]) for i in np.arange(len(opt_px))]
df2['px_bid'] = [px_opt_ticks(df1[(df1['ticker'] == t2[i]) & (df1['field'] == 'PX_BID') ]['value']) for i in np.arange(len(t2))]
df2['px_ask'] = [px_opt_ticks(df1[(df1['ticker'] == t2[i]) & (df1['field'] == 'PX_ASK') ]['value']) for i in np.arange(len(t2))]
#df2['px_bid'] = [px_opt_ticks(df1[df1['field'] == 'PX_BID']['value'].tolist()[i]) for i in np.arange(len(opt_px))]
#df2['px_ask'] = [px_opt_ticks(df1[df1['field'] == 'PX_ASK']['value'].tolist()[i]) for i in np.arange(len(opt_px))]
df2['weights'] = weights

df3 = bond_fut_yield('USU1',strikes)

df2['Yld'] = df3['K_Yield']
df2['ATM_K'] = df3['K_Dist']



### Vanilla + European+ Analytic
opt_iv = []
opt_delta = []
opt_gamma = []
opt_theta = []
opt_vega = []
opt_bs_px = []

for i in np.arange(len(opt_px)):
    payoff = ql.PlainVanillaPayoff(option_type_ql[i], strikes[i])
    exercise = ql.EuropeanExercise(expiry_dt)
    option = ql.VanillaOption(payoff, exercise)
    
    option.setPricingEngine(ql.AnalyticEuropeanEngine(bsm_process))

    opt_iv.append(100*option.impliedVolatility(df2['px'][i], bsm_process))
    opt_vol_ts = ql.BlackVolTermStructureHandle(ql.BlackConstantVol(calculation_date, calendar, opt_iv[i]/100, day_count))
    bsm_process = ql.BlackScholesMertonProcess(spot_handle, div_ts, flat_ts, opt_vol_ts)
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

opt_strat = pd.DataFrame() 
opt_strat['px']= np.array([px_opt_ticks(np.dot(df2['px'],df2['weights']))])
opt_strat['delta'] = np.array([np.dot(df2['delta'],df2['weights'])])
opt_strat['gamma'] = np.array([np.dot(df2['gamma'],df2['weights'])])
opt_strat['theta'] = np.array([np.dot(df2['theta'],df2['weights'])])


#################################################################################################### PY _ VOLLIB

import py_vollib 
from py_vollib.black import black as black_model
from py_vollib.black_scholes  import black_scholes as bs
from py_vollib.black_scholes.implied_volatility import implied_volatility as iv
from py_vollib.black.implied_volatility import implied_volatility as black_iv

from py_vollib.black_scholes.greeks.analytical import delta 
from py_vollib.black_scholes.greeks.analytical import gamma
from py_vollib.black_scholes.greeks.analytical import rho
from py_vollib.black_scholes.greeks.analytical import theta
from py_vollib.black_scholes.greeks.analytical import vega

from py_vollib.black.greeks.analytical import delta 
from py_vollib.black.greeks.analytical import gamma

from py_vollib.black_scholes.greeks.numerical import delta 
from py_vollib.black_scholes.greeks.numerical import gamma


#py_vollib.black_scholes.implied_volatility(price, S, K, t, r, flag)

"""
price (float) – the Black-Scholes option price
S (float) – underlying asset price
sigma (float) – annualized standard deviation, or volatility
K (float) – strike price
t (float) – time to expiration in years
r (float) – risk-free interest rate
flag (str) – ‘c’ or ‘p’ for call or put.
"""
def greek_val(flag, S, K, t, r, sigma):
    price = bs(flag, S, K, t, r, sigma)
    imp_v = iv(price, S, K, t, r, flag)
    delta_calc = delta(flag, S, K, t, r, sigma)
    gamma_calc = gamma(flag, S, K, t, r, sigma)
    rho_calc = rho(flag, S, K, t, r, sigma)
    theta_calc = theta(flag, S, K, t, r, sigma)
    vega_calc = vega(flag, S, K, t, r, sigma)
    return np.array([ price, imp_v ,theta_calc, delta_calc ,rho_calc ,vega_calc ,gamma_calc])

S = 160+(27/32)
K = 165
#sigma = 16
r = 0.001
t = (ql.Date(27,8,2021)-ql.Date(5,7,2021))/365
px = (41.5/64)

bs('c', S, K, t, r, 0.0823)
iv(px, S, K, t, r, 'c')
black_iv(px, S, K, t, r, 'c')


delta('c', S, K, t, r, iv(px, S, K, t, r, 'c'))
gamma('c', S, K, t, r, iv(px, S, K, t, r, 'c'))
theta('c', S, K, t, r, iv(px, S, K, t, r, 'c'))
vega('c', S, K, t, r, iv(px, S, K, t, r, 'c'))


ql.Date(27,8,2021)-ql.Date(5,7,2021)








