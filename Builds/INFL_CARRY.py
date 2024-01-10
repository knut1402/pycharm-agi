##### inflation carry calculation 


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

from INF_ZC_BUILD import infl_zc_swap_build, Infl_ZC_Pricer
from Utilities import *


def linker_carry_calc(isin, inf_index, repo_rate, fixing_curve = 'BARX', fwd_date=''):

#    isin = ['CA135087VS05 Govt']
#    isin = euro_linker_db['linker_isin'].tolist()
#    inf_index = 'CACPI'
#    fixing_curve = 'Seasonals'
#    repo_rate = 0.18
#    fwd_date = '' 
#    fwd_date = ['31-01-2022']
   
    if fixing_curve == 'BARX':
        forcast_index = 2
    elif fixing_curve == 'Market':
        forcast_index = 1
    elif fixing_curve == 'Seasonals':
        forcast_index = 0

    fix_c = infl_zc_swap_build(inf_index,b=-1)
    
    if fwd_date == '':
        fwd_date = [ ql.Date.endOfMonth(fix_c.ref_date)+ql.Period(str(i)+'M') for i in np.arange(3) ]
    else:
        fwd_date = [ql.Date(int(fwd_date[i].split('-')[0]),int(fwd_date[i].split('-')[1]),int(fwd_date[i].split('-')[2])) for i in np.arange(len(fwd_date)) ]
        # fwd date format:
        # fwd_date = ['30-01-2022', '15-03-2022' ]
            

    df_static = dict([(key, []) for key in isin ])
    df_carry = dict([(key, []) for key in isin ])
    [df_static[i].append(con.ref(i, ['MATURITY','CPN','CPN_FREQ','DAYS_ACC','DAYS_TO_NEXT_COUPON','PX_LAST', 'PX_CLOSE_1D','SETTLE_DT','PX_CLOSE_DT','DAYS_TO_SETTLE','BASE_CPI'])) for i in isin];

    for j in isin:
        j = isin[0]
        d1 = df_static[j][0][df_static[j][0]['field'] == 'SETTLE_DT']['value'].tolist()[0]
        spot_settle_date = ql.Date(d1.day,d1.month,d1.year)
        spot_clean_px = df_static[j][0][df_static[j][0]['field'] == 'PX_LAST']['value'].tolist()[0]
    
        d2 = df_static[j][0][df_static[j][0]['field'] == 'PX_CLOSE_DT']['value'].tolist()[0]
        close_date =  ql.Date(d2.day,d2.month,d2.year)
        close_sette_date =  fix_c.cal.advance(close_date,  df_static[j][0][df_static[j][0]['field'] == 'DAYS_TO_SETTLE']['value'].tolist()[0]  ,ql.Days)
        close_clean_px = df_static[j][0][df_static[j][0]['field'] == 'PX_CLOSE_1D']['value'].tolist()[0]

        ref_index_close = get_infl_index(fix_c.curve[2], close_sette_date)
        idx_ratio_close = np.round(ref_index_close / df_static[j][0][df_static[j][0]['field'] == 'BASE_CPI']['value'].tolist()[0],5)
        coupon_acc_close = (df_static[j][0][df_static[j][0]['field'] == 'CPN']['value'].tolist()[0] * (1 / df_static[j][0][df_static[j][0]['field'] == 'CPN_FREQ']['value'].tolist()[0]) * (df_static[j][0][df_static[j][0]['field'] == 'DAYS_ACC']['value'].tolist()[0] - int(spot_settle_date - close_sette_date )) / 
                            (df_static[j][0][df_static[j][0]['field'] == 'DAYS_ACC']['value'].tolist()[0] + df_static[j][0][df_static[j][0]['field'] == 'DAYS_TO_NEXT_COUPON']['value'].tolist()[0] ))

        dp_cls = (close_clean_px + coupon_acc_close)*idx_ratio_close
    
        ref_index = get_infl_index(fix_c.curve[2], spot_settle_date)
        idx_ratio = np.round(ref_index / df_static[j][0][df_static[j][0]['field'] == 'BASE_CPI']['value'].tolist()[0],5)
        coupon_acc = (df_static[j][0][df_static[j][0]['field'] == 'CPN']['value'].tolist()[0] * (1 / df_static[j][0][df_static[j][0]['field'] == 'CPN_FREQ']['value'].tolist()[0]) * (df_static[j][0][df_static[j][0]['field'] == 'DAYS_ACC']['value'].tolist()[0] ) / 
                      (df_static[j][0][df_static[j][0]['field'] == 'DAYS_ACC']['value'].tolist()[0] + df_static[j][0][df_static[j][0]['field'] == 'DAYS_TO_NEXT_COUPON']['value'].tolist()[0] ))

        dp = (spot_clean_px + coupon_acc)*idx_ratio 
    
        repo_close = (dp_cls*repo_rate)*int( spot_settle_date - close_sette_date) / 36000 
        spot_clean_px_from_close = ((dp_cls + repo_close) / idx_ratio ) - coupon_acc
    
        fwd_index_ratio = [ np.round(get_infl_index(fix_c.curve[2], fwd_date[i]) / df_static[j][0][df_static[j][0]['field'] == 'BASE_CPI']['value'].tolist()[0],5) for i in np.arange(len(fwd_date)) ] 
        fwd_cpn_acc = [ (df_static[j][0][df_static[j][0]['field'] == 'CPN']['value'].tolist()[0] * (1 / df_static[j][0][df_static[j][0]['field'] == 'CPN_FREQ']['value'].tolist()[0]) * (df_static[j][0][df_static[j][0]['field'] == 'DAYS_ACC']['value'].tolist()[0]  + int(fwd_date[i] - spot_settle_date )) /
                         (df_static[j][0][df_static[j][0]['field'] == 'DAYS_ACC']['value'].tolist()[0] + df_static[j][0][df_static[j][0]['field'] == 'DAYS_TO_NEXT_COUPON']['value'].tolist()[0] )) for i in np.arange(len(fwd_date)) ]

        repo = [ (dp*repo_rate)*int(fwd_date[i] - spot_settle_date) / 36000 for i in np.arange(len(fwd_date)) ]
        fwd_clean_px = [ ((dp + repo[i]) / fwd_index_ratio[i] ) - fwd_cpn_acc[i] for i in np.arange(len(fwd_date)) ]
    
        close_yield = con.ref(j, ['YLD_YTM_BID'], ovrds =[('PX_BID',close_clean_px),(('SETTLE_DT',  bbg_date_str(  close_sette_date , ql_date=1)  ))])['value'][0]
        spot_yield_from_close = con.ref(j, ['YLD_YTM_BID'], ovrds =[('PX_BID',spot_clean_px_from_close),(('SETTLE_DT',  bbg_date_str(  spot_settle_date , ql_date=1)  ))])['value'][0]
        spot_yield = con.ref(j, ['YLD_YTM_BID'], ovrds =[('PX_BID',spot_clean_px ),(('SETTLE_DT',  bbg_date_str(  spot_settle_date , ql_date=1)  ))])['value'][0]
        fwd_yield = [ con.ref(j, ['YLD_YTM_BID'], ovrds =[ ('PX_BID',fwd_clean_px[i] ),(('SETTLE_DT',  bbg_date_str(fwd_date[i], ql_date=1) ))])['value'][0] for i in np.arange(len(fwd_date)) ]
    
        df_carry[j] = [100*(spot_yield_from_close - close_yield)] + [100*(fwd_yield[0] - spot_yield)] + [ 100*(fwd_yield[i] - fwd_yield[i-1])  for i in np.arange(1,len(fwd_date))]
        
    return df_carry, fwd_date



#linker_carry_calc( ['CA135087VS05 Govt'], 'CACPI', repo_rate=0.0, fixing_curve = 'Seasonals', fwd_date='')



