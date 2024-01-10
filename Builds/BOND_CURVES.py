##### bond database
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

con = pdblp.BCon(debug=False, port=8194, timeout=500000)
con.start()

from Conventions import FUT_CT,FUT_CT_Q, ccy
from SWAP_BUILD import swap_build
from OIS_DC_BUILD import ois_dc_build
from SWAP_PRICER import Swap_Pricer
from Utilities import *


def bond_curve_build(db_srch, d1, fwd_d, repo_rate, fwd_repo_rate):

#    db_srch = ['ITALY_NOM']
#    db_srch = ['SWEDEN_NOM']
#    d1 = [0, '04-01-2022']
#    repo_rate = 0
#    fwd_repo_rate = 0
#    fwd_d = ['1m', '3m']

    cal = ql.UnitedStates(ql.UnitedStates.FederalReserve)
    repo_rate = [repo_rate]*(len(d1)-1)
    fwd_repo_rate = [fwd_repo_rate]*len(fwd_d)
    
    df_out = dict([(key, []) for key in db_srch ])
    g_out = []
    
    for k in np.arange(len(db_srch)):
        k=0
        ###################### output set up
        bbid = con.bsrch("FI:"+db_srch[k])[0]
        df_static = dict([(key, []) for key in bbid ])
        [df_static[i].append(con.ref(i, ['ID_ISIN','CRNCY','PX_DIRTY_CLEAN','MATURITY','CPN','CPN_FREQ','DAYS_ACC','DAYS_TO_NEXT_COUPON', 'SETTLE_DT','PX_CLOSE_DT','DAYS_TO_SETTLE','BASE_CPI','ISSUE_DT'])) for i in bbid];
        df_output = dict([(key, []) for key in ['ISIN', 'MATURITY', 'COUPON', 'PX', 'YLD'] + flat_lst( [ ['PX_T'+str(i), 'YLD_T'+str(i), 'CARRY_T'+str(i)]  for i in np.arange(1,len(d1))]) +[str(fwd_d[i])+'_CARRY' for i in np.arange(len(fwd_d))] ])

        ##### handling dates
        today = ql.Date(datetime.datetime.now().day,datetime.datetime.now().month,datetime.datetime.now().year)
        d1_a = []
        for j in np.arange(len(d1)):
            if isinstance(d1[j],int) == True:
                d1_a.append(cal.advance(today,d1[j],ql.Days))
            elif isinstance(d1[j],str) == True:
                try:
                    d1_a.append( ql.Date(int(d1[j].split('-')[0]),int(d1[j].split('-')[1]),int(d1[j].split('-')[2])) )
                except:
                    if d1[j][-1] in ('D','d'):
                        unit = ql.Days
                    elif d1[j][-1] in ('W','w'):
                        unit = ql.Weeks
                    elif d1[j][-1] in ('M','m'):
                        unit = ql.Months
                    if j > 0:
                        d1_a.append(cal.advance( d1_a[0] , int(d1[j][0:-1]), unit) )
                    else:
                        d1_a.append(cal.advance( today , int(d1[j][0:-1]), unit) )

        d1_b = [bbg_date_str(d1_a[i] , ql_date=1) for i in np.arange(len(d1)) ]  
        settle_dt = [cal.advance(d1_a[i],  df_static[bbid[0]][0][df_static[bbid[0]][0]['field'] == 'DAYS_TO_SETTLE']['value'].tolist()[0], ql.Days) for i in np.arange(len(d1)) ]

        settle_fwd_dt = []
        for j in np.arange(len(fwd_d)):
            if isinstance(fwd_d[j],int) == True:
                settle_fwd_dt.append(cal.advance(d1_a[0],fwd_d[j],ql.Days))
            elif isinstance(fwd_d[j],str) == True:
                try:
                    settle_fwd_dt.append( ql.Date(int(fwd_d[j].split('-')[0]),int(fwd_d[j].split('-')[1]),int(fwd_d[j].split('-')[2])) )
                except:
                    if fwd_d[j][-1] in ('D','d'):
                        unit = ql.Days
                    elif fwd_d[j][-1] in ('W','w'):
                        unit = ql.Weeks
                    elif fwd_d[j][-1] in ('M','m'):
                        unit = ql.Months
                    settle_fwd_dt.append(cal.advance( d1_a[0] , int(fwd_d[j][0:-1]), unit) )

        for j in np.arange(len(bbid)):
#            print(j)
#            print( df_static[bbid[j]][0][df_static[bbid[j]][0]['field'] == 'ID_ISIN']['value'].tolist()[0] )
            issue_dt = df_static[bbid[j]][0][df_static[bbid[j]][0]['field'] == 'ISSUE_DT']['value'].tolist()[0] 
            issue_dt = ql.Date(issue_dt.day,issue_dt.month,issue_dt.year)            
            mature_dt = df_static[bbid[j]][0][df_static[bbid[j]][0]['field'] == 'MATURITY']['value'].tolist()[0] 
            mature_dt = ql.Date(mature_dt.day,mature_dt.month,mature_dt.year)
            if any(x < issue_dt for x in d1_a) or any( mature_dt - y < 90  for y in d1_a):
                print(issue_dt, mature_dt)
            else:
                #### live and chg on day T
                px = [con.bdh( bbid[j],['PX_LAST'], d1_b[i], d1_b[i], longdata=True)['value'].tolist()[0] for i in np.arange(len(d1)) ]
                yields = [ con.ref( bbid[j] , ['YLD_YTM_BID'], ovrds =[('PX_BID', px[i] ),(('SETTLE_DT',  bbg_date_str(  settle_dt[i] , ql_date=1)  ))])['value'][0] for i in np.arange(len(d1)) ]


                ###### past carry 
                coupon_acc = [( df_static[bbid[j]][0][df_static[bbid[j]][0]['field'] == 'CPN']['value'].tolist()[0] * (1 / df_static[bbid[j]][0][df_static[bbid[j]][0]['field'] == 'CPN_FREQ']['value'].tolist()[0]) * ( df_static[bbid[j]][0][df_static[bbid[j]][0]['field'] == 'DAYS_ACC']['value'].tolist()[0]  - int(settle_dt[0] - settle_dt[i]) - 1) / 
                               (df_static[bbid[j]][0][df_static[bbid[j]][0]['field'] == 'DAYS_ACC']['value'].tolist()[0] + df_static[bbid[j]][0][df_static[bbid[j]][0]['field'] == 'DAYS_TO_NEXT_COUPON']['value'].tolist()[0] )) for i in np.arange(len(d1)) ]

                dp = [(px[i] + coupon_acc[i]) for i in np.arange(len(d1))]
                repo = [ (dp[i]*repo_rate[i-1])*int(settle_dt[0] - settle_dt[i] ) / 36000 for i in np.arange(1,len(d1))]
                implied_spot_clean_px =  [dp[i] + repo[i-1] - coupon_acc[0] for i in np.arange(1,len(d1)) ]
                implied_yields = [ con.ref( bbid[j] , ['YLD_YTM_BID'], ovrds =[('PX_BID', implied_spot_clean_px[i-1] ),(('SETTLE_DT',  bbg_date_str(  settle_dt[0] , ql_date=1)  ))])['value'][0] for i in np.arange(1,len(d1)) ]
                implied_carry = [ 100*(implied_yields[i-1]  - yields[i]) for i in np.arange(1,len(d1)) ]

                ###### fwd carry 
                fwd_coupon_acc = [( df_static[bbid[j]][0][df_static[bbid[j]][0]['field'] == 'CPN']['value'].tolist()[0] * (1 / df_static[bbid[j]][0][df_static[bbid[j]][0]['field'] == 'CPN_FREQ']['value'].tolist()[0]) * ( df_static[bbid[j]][0][df_static[bbid[j]][0]['field'] == 'DAYS_ACC']['value'].tolist()[0]  + int(settle_fwd_dt[i] - settle_dt[0]) - 1) / 
                                   (df_static[bbid[j]][0][df_static[bbid[j]][0]['field'] == 'DAYS_ACC']['value'].tolist()[0] + df_static[bbid[j]][0][df_static[bbid[j]][0]['field'] == 'DAYS_TO_NEXT_COUPON']['value'].tolist()[0] )) for i in np.arange(len(fwd_d)) ]

                fwd_repo = [ (dp[0]*fwd_repo_rate[i])*int(settle_fwd_dt[i] - settle_dt[0]) / 36000 for i in np.arange(len(fwd_d))]
                implied_fwd_clean_px =  [ dp[0] + fwd_repo[i] - fwd_coupon_acc[i] for i in np.arange(len(fwd_d)) ]

                fwd_implied_yields = [ con.ref( bbid[j] , ['YLD_YTM_BID'], ovrds =[('PX_BID', implied_fwd_clean_px[i] ),(('SETTLE_DT',  bbg_date_str(  settle_fwd_dt[i] , ql_date=1)  ))])['value'][0] for i in np.arange(len(fwd_d)) ]
                fwd_implied_carry = [ 100*(fwd_implied_yields[i]  - yields[0]) for i in np.arange(len(fwd_d)) ]

                ##### formatting output
                df_output['ISIN'].append( df_static[bbid[j]][0][df_static[bbid[j]][0]['field'] == 'ID_ISIN']['value'].tolist()[0] )
                df_output['MATURITY'].append( df_static[bbid[j]][0][df_static[bbid[j]][0]['field'] == 'MATURITY']['value'].tolist()[0] )
                df_output['COUPON'].append( df_static[bbid[j]][0][df_static[bbid[j]][0]['field'] == 'CPN']['value'].tolist()[0] )
                df_output['PX'].append(px[0] )
                df_output['YLD'].append(yields[0] )
                
                for i in np.arange(1,len(d1)):
                    df_output['PX_T'+str(i)].append(px[i] )
                    df_output['YLD_T'+str(i)].append(yields[i] )
                    df_output['CARRY_T'+str(i)].append(implied_carry[i-1] )

                for i in np.arange(len(fwd_d)):
                    df_output[str(fwd_d[i])+'_CARRY'].append(fwd_implied_carry[i])

        df2 = pd.DataFrame(df_output)
        for i in  np.arange(1,len(d1)):
            df2['YLD_CHG_'+str(i)] = 100*( df2['YLD'] - df2['YLD_T'+str(i)]) - df2['CARRY_T'+str(i)]

        df2 = df2.sort_values(['MATURITY']) 
        df2 = df2.reset_index(drop=True)

        x = df2['MATURITY'].tolist()
        y = df2['YLD'].tolist()
        z = [df2['YLD_CHG_'+str(i)].tolist() for i in np.arange(1,len(d1)) ]
        hover_labels = x

        ql.Settings.instance().evaluationDate = d1_a[0]
        bonds = pd.DataFrame({'maturity': x, 'coupon': df2['COUPON'].tolist(), 'price': df2['PX'].tolist() })
        bondSettlementDays = df_static[bbid[0]][0][df_static[bbid[0]][0]['field'] == 'DAYS_TO_SETTLE']['value'].tolist()[0]
        bondSettlementDate = cal.advance(d1_a[0], ql.Period(bondSettlementDays , ql.Days))
        frequency = df_static[bbid[j]][0][df_static[bbid[j]][0]['field'] == 'CPN_FREQ']['value'].tolist()[0]
        dc = ql.ActualActual(ql.ActualActual.ISMA)
        accrualConvention = ql.ModifiedFollowing
        convention = ql.ModifiedFollowing
        redemption = 100.0

        instruments = []
        for idx, row in bonds.iterrows():
            schedule = ql.Schedule(bondSettlementDate, ql.Date(row.maturity.day,row.maturity.month,row.maturity.year), ql.Period(frequency), cal, accrualConvention, accrualConvention, ql.DateGeneration.Backward, False)
            helper = ql.FixedRateBondHelper(ql.QuoteHandle(ql.SimpleQuote(row.price)), bondSettlementDays, 100.0, schedule, [row.coupon / 100], dc, convention, redemption)
            instruments.append(helper)    

        curve_ns = ql.FittedBondDiscountCurve(bondSettlementDays, cal, instruments, dc, ql.NelsonSiegelFitting(), 1.0e-5, 10000)

        t = np.arange(1, int(np.floor((ql.Date(x[-1].day,x[-1].month, x[-1].year)- d1_a[0])/365)+1))
        t_x1 = [d1_a[0] + ql.Period(str(i)+'Y') for i in t]
        t_x2 = [datetime.datetime(t_x1[i].year(), t_x1[i].month(), t_x1[i].dayOfMonth())  for i in np.arange(len(t_x1))  ]
        rates_fwd = [100*curve_ns.forwardRate( bondSettlementDate, bondSettlementDate+ql.Period(str(i)+'Y'), dc,convention, ql.Annual).rate() for i in t]
        
        mpl.rcParams.update(mpl.rcParamsDefault)
        fig, ax = plt.subplots(2,1,figsize=[6.5,4.5],  gridspec_kw={'height_ratios': [2,1], 'hspace':0.135})
        sc = ax[0].scatter(x,y, s = 12, marker = 'x')
        ax[0].plot( t_x2 , rates_fwd, linewidth= 1, color = 'red' )
        ax[1].plot( ( ql_to_datetime(d1_a[0]),x[-1]) , (0,0), linewidth= 0.5,  color='black' )
        for i in np.arange(len(z)):
            x1 = [x[j]+datetime.timedelta(int(i)*30) for j in np.arange(len(x))]
            ax[1].bar(tuple(x1) , tuple(z[i]), width = 50)

        ax[0].grid(visible=True, linewidth=0.35)
        ax[0].set_title('')
        ax[0].set_ylabel('yield')
        ax[1].set_ylabel('adj. chg (bps)')
        plt.show()

        df3 = df2[['ISIN', 'MATURITY', 'COUPON', 'PX', 'YLD']+ ['YLD_CHG_'+str(i) for i in np.arange(1,len(d1))]+[str(fwd_d[i])+'_CARRY' for i in np.arange(len(fwd_d))]]
        
        df3 = df3.round({'PX': 3, 'YLD': 3, 'YLD_CHG_1': 1, '1M_CARRY': 1, '3M_CARRY': 1})
        
        df_out[db_srch[k]].append(df3)
        g_out = g_out + [fig]
    
#    plt.tight_layout();
    return df_out, g_out


#df_out['COLOMBIA_NOM_LCL'][0]
#g_out[0]




