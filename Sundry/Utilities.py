######## ALL UTILITIES
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
import concurrent.futures
import time


def bond_fut_yield2(fut_ticker,fut_px):
    con = pdblp.BCon(debug=False, port=8194, timeout=50000)
    con.start()

#    fut_ticker = '5MM2'
#    fut_px = np.array(strikes)[mask1].tolist()

    bond_fut_dets = con.ref(fut_ticker+' Comdty', ['FUT_CTD_ISIN','FUT_DLV_DT_LAST','FUT_CNVS_FACTOR','CRNCY'])['value']
    fut_last = con.ref(fut_ticker+' Comdty', ['PX_LAST'])['value'][0]
    fwd_px = fut_last*bond_fut_dets[2]
    strike_px = np.array(fut_px)*bond_fut_dets[2]
    
    fwd_yield = con.ref(bond_fut_dets[0]+' Govt', ['YLD_YTM_BID'], ovrds =[('PX_BID',fwd_px),(('SETTLE_DT',bbg_date_str(bond_fut_dets[1], ql_date=0)))])['value'][0]

    strike_yield = [con.ref(bond_fut_dets[0]+' Govt', ['YLD_YTM_BID'], ovrds =[('PX_BID',strike_px[i]), (('SETTLE_DT',bbg_date_str(bond_fut_dets[1], ql_date=0)))])['value'][0] for i in np.arange(len(fut_px))]
   
    bond_fut_yield_tab = pd.DataFrame()
    bond_fut_yield_tab['Fut'] = np.repeat(fut_ticker,len(fut_px))
    if bond_fut_dets[3] == 'USD':
        bond_fut_yield_tab['Fut_Px'] = np.repeat(px_dec_to_frac(fut_last),len(fut_px))
    else:
        bond_fut_yield_tab['Fut_Px'] = np.repeat(fut_last,len(fut_px))
    bond_fut_yield_tab['Fut_Yield'] = np.repeat(fwd_yield,len(fut_px))
    bond_fut_yield_tab['K_Yield'] = np.array(strike_yield)
    bond_fut_yield_tab['K_'] = np.array(fut_px)
    bond_fut_yield_tab['K_Dist'] = 100*np.array(strike_yield-fwd_yield)
    
    return bond_fut_yield_tab

#bond_fut_yield2(fut[:4],np.array(strikes)[mask1].tolist())
#bond_fut_yield(fut[:4],np.array(strikes)[mask1].tolist())
#bond_fut_yield('TYM2', [118, 119, 120, 118.5] )

def bond_fut_yield(fut_ticker, fut_px):
    con = pdblp.BCon(debug=False, port=8194, timeout=50000)
    con.start()
#    fut_ticker = fut[:4]
#    fut_px = df2['strikes'].tolist()

    #bond future
    bond_fut_dets = con.ref(fut_ticker + ' Comdty', ['FUT_CTD_ISIN','FUT_DLV_DT_LAST','FUT_CNVS_FACTOR','CRNCY','PX_LAST'])['value']
    fut_last = bond_fut_dets.pop(bond_fut_dets.index[-1])
    fwd_px = fut_last * bond_fut_dets[2]
    strike_px = np.array(fut_px) * bond_fut_dets[2]
    
    #ctd
    fwd_yield = con.ref(bond_fut_dets[0]+' Govt', ['YLD_YTM_BID'], ovrds =[('PX_BID',fwd_px),(('SETTLE_DT',bbg_date_str(bond_fut_dets[1], ql_date=0)))])['value'][0]
            
    #yield retriever for strikes
    def get_strike_yield(strike):
        bond_yield = con.ref(bond_fut_dets[0]+ ' Govt', ['YLD_YTM_BID'], ovrds = [('PX_BID', strike), ('SETTLE_DT', bbg_date_str(bond_fut_dets[1], ql_date=0) )])['value'][0]
        return bond_yield

    #concurrent api calls
    with concurrent.futures.ThreadPoolExecutor(8) as executor:
        yields = executor.map(get_strike_yield, strike_px)
    strike_yield = list(yields)
    
    #dataframe builder
    bond_fut_yield_tab = pd.DataFrame()
    bond_fut_yield_tab['Fut'] = np.repeat(fut_ticker, len(fut_px))
    bond_fut_yield_tab['Fut'] = np.repeat(fut_ticker,len(fut_px))
    if bond_fut_dets[3] == 'USD':
        bond_fut_yield_tab['Fut_Px'] = np.repeat(px_dec_to_frac(fut_last),len(fut_px))
    else:
        bond_fut_yield_tab['Fut_Px'] = np.repeat(fut_last,len(fut_px))
        
    bond_fut_yield_tab['Fut_Yield'] = np.repeat(fwd_yield, len(fut_px))
    bond_fut_yield_tab['K_Yield'] = np.array(sorted( (strike_yield), reverse=True)) 
    bond_fut_yield_tab['K_'] = np.array(sorted(fut_px, reverse=False))
    bond_fut_yield_tab['K_Dist'] = 100*np.array(sorted(strike_yield, reverse=True)-fwd_yield)
    
    return bond_fut_yield_tab


def get_next_imm(d,n):
    d = ql.UnitedKingdom().advance(d,ql.Period('-3m'))
    imms = [d]
    for i in np.arange(n):
        imms.append(ql.IMM.nextDate( imms[-1] ))
    return imms[1:]




############### for bond futures options pricing
def px_opt_ticks(a, tick = 1/64):
#    a = opt_px.values[0]
    a1 = math.modf(a)
    if int(a1[0]/tick) < 10:
        a2 = str(int(a1[1]))+"'0"+str(int(a1[0]/tick))
    else:
        a2 = str(int(a1[1]))+"'"+str(int(a1[0]/tick))
    return a2


def fut_payoff(x, fut_tick ,fut_dets):
#    x = st.strat['fut_px']
#    fut_tick = ['USU1 Comdty']    
#    fut_dets = [-1,166.0]
    fut_tick_size = con.ref(fut_tick[0], ['FUT_TICK_SIZE'])['value'][0]
    fut_tick_val = con.ref(fut_tick[0], ['FUT_TICK_VAL'])['value'][0]
    fut_point_val = np.float(con.ref(fut_tick[0], ['FUT_VAL_PT'])['value'][0])
    
    y = ((fut_tick_val/fut_tick_size)/fut_point_val)*fut_dets[0]*( x - fut_dets[1] )
    return y

def opt_payoff(x, opt_dets, opt_px):
#    x = x1
#   opt_px = 0.2
#   opt_dets =     
    opt_type = opt_dets[1]
    k = opt_dets[2]
    opt_w = opt_dets[3]
    
    y = np.repeat(-opt_px,len(x))
    for i in np.arange(len(opt_type)):
        if opt_type[i] == 'C':
            pv = x - k[i]
            pv[pv < 0] = 0
            y = y + opt_w[i]*pv
        else:
            pv = k[i] - x
            pv[pv < 0] = 0
            y = y + opt_w[i]*pv
    
    return y


def round_nearest(x, a):
    return round(x / a) * a


### swap_class feeds swap_pricer
def swap_class( index, st, mt, n, x ):
     
    class swpc: 
        def __init__(self):
            self.index = index
            self.st = st
            self.mt = mt
            self.n = n
            self.rate_x = x

    return swpc()

### inflation indexratio helper
def  get_infl_index(index_hist, ref_date):
    ### interp was a flag used for historial fixings vs forecasted fixings for interpolated curves
#    index_hist = inf_index_hist
#    ref_date = ql.Date(2,1,2021)
   
    dd = ref_date.dayOfMonth()
    diM = ql.Date.endOfMonth(ref_date).dayOfMonth()
    
    index_date = ref_date - ql.Period("3M")
    

    index_sm = index_hist[index_hist['months'] == (index_date - index_date.dayOfMonth() + 1)]['index'].tolist()[0]
    index_em = index_hist[index_hist['months'] == ql.Date.endOfMonth(index_date) + 1]['index'].tolist()[0]
    
    index = index_sm + ((dd-1)*(index_em - index_sm)/diM)
    
    return index



#### Bloomberg utilities to be moved separately !!
def bbg_date_str(a, ql_date = 1):    
#    a = con.ref('USU1 Comdty', ['FUT_DLV_DT_LAST'])['value'][0]
    if ql_date != 1:
        a = ql.Date(a.day,a.month,a.year)
    
    if a.dayOfMonth() < 10:
        d0 = str(0)+str(a.dayOfMonth())
    else:
        d0 = str(a.dayOfMonth())
    
    if a.month() < 10:
        m0 = str(0)+str(a.month())
    else:
        m0 = str(a.month())
    
    bbg_t = str(a.year())+m0+d0
    return bbg_t


def ql_date_str(a, ql_date=1):
    #    a = con.ref('USU1 Comdty', ['FUT_DLV_DT_LAST'])['value'][0]
    if ql_date != 1:
        a = ql.Date(a.day, a.month, a.year)

    if a.dayOfMonth() < 10:
        d0 = str(0) + str(a.dayOfMonth())
    else:
        d0 = str(a.dayOfMonth())

    if a.month() < 10:
        m0 = str(0) + str(a.month())
    else:
        m0 = str(a.month())

    bbg_t = d0+'-'+m0+'-'+str(a.year())
    return bbg_t

def px_dec_to_frac(a, ft = 32):
    a1 = int(math.modf(a)[1])
    a2 = math.modf(math.modf(a)[0]*ft)
    if int((a2)[1]) == 0:
        a3 = ''
    elif int((a2)[1]) < 10:
        a3 = '-0'+str(int((a2)[1]))
    else:
        a3 = '-'+str(int((a2)[1]))
    
    
    a4 = (a2[0])*8
    
    if a4 == 4.0:
        a4 = '+'
    elif a4 == 0.0:
        a4 = ''
    else:
        a4 = int(a4)
    return str(a1)+str(a3)+str(a4)

def px_dec_to_opt_frac(a, ft = 64):
    
#    a = df_opt_strat['strat_px'][3]
#    ft=64
    
    if np.sign(a) > 0:
        a_sign = ''
    else:
        a_sign = '-'
    a1 = abs(int(math.modf(a)[1]))
    a2 = math.modf(a)[0]*ft
    
    if abs(np.round(abs(a2),1)) < 10:
        a3 = '0'
    else:
        a3 = ''
    
    if abs(a1) < 1:
        a3 = a_sign+str(np.round(abs(a2),1))
    else:
        a3 = a_sign+str(a1)+'-'+a3+str(np.round(abs(a2),1))
    return(a3)


def px_frac_to_opt_dec(a, ft=64):
#    a = '1-16.8'
#    ft=64
    if a[0] == '-':
        a_sign = -1
        a = a[1:]
    else:
        a_sign = +1

    a2 = a.split('-')
    if len(a2) > 1:
        a3 = a_sign*(int(a2[0]) + (float(a2[1])/ft))
    else:
        a3 = a_sign * float(a2[0]) / ft
    return a3

def convert_to_64(a):
### converting 1-02 to 66 / no dedimals involved this is fractional -> fractional; required for plotting opt payoff
#    a = '1-16.8'

    if a[0] == '-':
        a_sign = -1
        a = a[1:]
    else:
        a_sign = +1

    a2 = a.split('-')
    if len(a2) > 1:
        a3 = a_sign*( (64*int(a2[0])) + float(a2[1]))
    else:
        a3 = a_sign * float(a2[0])
    return a3



def flat_lst(t):
    flat_list = [item for sublist in t for item in sublist]
    return flat_list

##### Quantlib utilities

def ql_to_datetime(d):
    return datetime.date(d.year(), d.month(), d.dayOfMonth())


def datetime_to_ql(d):
    return ql.Date(d.day,d.month, d.year)

#### converting datetime string
def convert_date_format(date_str):
    try:
        date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d')
    except:
        date_obj = datetime.datetime.strptime(date_str, '%Y/%m/%d %H:%M:%S')
    return date_obj.strftime('%d-%m-%Y')

#### df style map for -ve numbers in red
    def style_negative(v, props=''):
        return props if v < 0 else None


### removing certain plots from bokeh charts
def remove_glyphs(figure, glyph_name_list):
    renderers = figure.select(dict(type=GlyphRenderer))
    for r in renderers:
        if r.name in glyph_name_list:
            col = r.glyph.y
            r.data_source.data[col] = [np.nan] * len(r.data_source.data[col])

### inflation 1y1y fwd for fixings
def get_1y1y_fwd(a):
    return 100*((((1 + (0.01 * a[1])) ** 2) / ((1 + (0.01 * a[0])) ** 1)) - 1)


def get_linker_metrics(df, sort_feed, m='fly'):
    df_out = pd.DataFrame()
    df_out['date'] = df.index

    if m == 'fly':
        df_out[m] = list(100 * (2 * df[sort_feed[1]] - df[sort_feed[0]] - df[sort_feed[2]])['YLD_YTM_MID'])
        df_out[m+'z_sprd'] = list(1 * (2 * df[sort_feed[1]] - df[sort_feed[0]] - df[sort_feed[2]])['Z_SPRD_MID'])
    elif m == 'spread':
        df_out[m] = list(100 * (df[sort_feed[1]] - df[sort_feed[0]])['YLD_YTM_MID'])
        df_out[m+'z_sprd'] = list(1 * (df[sort_feed[1]] - df[sort_feed[0]])['Z_SPRD_MID'])
    elif m == 'ry':
        df_out[m] = list(1 * (df[sort_feed[0]])['YLD_YTM_MID'])
        df_out[m+'z_sprd'] = list(1 * (df[sort_feed[0]])['Z_SPRD_MID'])

    df_out['z_score_1m'] = roll_zscore(df_out[m], 20)
    df_out['z_score_3m'] = roll_zscore(df_out[m], 60)
    df_out['z_score_6m'] = roll_zscore(df_out[m], 180)

    df_out['z_sprd_z_score_1m'] = roll_zscore(df_out[m+'z_sprd'],20)
    df_out['z_sprd_z_score_3m'] = roll_zscore(df_out[m+'z_sprd'],60)
    df_out['z_sprd_z_score_6m'] = roll_zscore(df_out[m+'z_sprd'],180)
    return df_out



def roll_zscore(x, window):
    r = x.rolling(window=window, min_periods=1)
    m = r.mean().shift(1)
    s = r.std(ddof=0).shift(1)
    z = (x-m)/s
    return z

