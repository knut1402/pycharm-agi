#### Swaption

import pandas as pd
import numpy as np
import datetime
#import tia
#from tia.bbg import LocalTerminal as LT
import pdblp
import eikon as ek
import runpy
import QuantLib as ql
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns


con = pdblp.BCon(debug=False, port=8194, timeout=50000)
con.start()

eikon_app_key= '6ccde6df4ee247cea42850581c08b61c4126f047'
ek.set_app_key(eikon_app_key)

from Utilities import *
from Conventions import FUT_CT,FUT_CT_Q, ccy
from OIS_DC_BUILD import ois_dc_build
from SWAP_BUILD import swap_build
from SWAP_PRICER import Swap_Pricer



def Swaption_Pricer(a,option_type,notional, t, roll, strat_tag = 1):
#    a = 'SOFR_DC'
#    option_type = ['P', 'P']
#    notional = [100, -100]
#    t = [[1.0,10,1.50], [1.0,10,1.75]]
#    roll = ["-1m","-2m","-3m"]
#    strat_tag = 1
    
    today = ql.Date(datetime.datetime.now().day,datetime.datetime.now().month,datetime.datetime.now().year)
    ql.Settings.instance().evaluationDate = today
    c = ccy(a,today)
    cal = c.cal
    
    if a == 'SONIA_DC':
        swp_crv = ois_dc_build(a, b=0)
        curve = ql.RelinkableYieldTermStructureHandle(swp_crv.curve)
        dc_curve = ql.RelinkableYieldTermStructureHandle(swp_crv.curve)
        index = ql.IborIndex(c.fixing, c.fixing_tenor, c.sett_d, c.curncy, c.cal, ql.ModifiedFollowing, True, c.floating[1], curve)
        volc = gbp_volc(curve, dc_curve, skew=1)
    elif a == 'SOFR_DC':
        swp_crv = ois_dc_build(a, b=0)
        curve = ql.RelinkableYieldTermStructureHandle(swp_crv.curve)
        dc_curve = ql.RelinkableYieldTermStructureHandle(swp_crv.curve)
        index = ql.IborIndex(c.fixing, c.fixing_tenor, c.sett_d, c.curncy, c.cal, ql.ModifiedFollowing, True, c.floating[1], curve)
        volc = usd_volc_sofr(curve, dc_curve, skew=1)
    elif a == 'USD_3M':
        swp_crv = swap_build(a, b=0)
        curve = ql.RelinkableYieldTermStructureHandle(swp_crv.curve[0])
        dc_curve = ql.RelinkableYieldTermStructureHandle(swp_crv.curve[1])
        index = c.index(c.fixing_tenor,curve)
        volc = usd_volc(curve, dc_curbe, skew=1)

    roll_dict = dict()
    strat_dict = dict([(key, []) for key in ['terms','premium','px_bps','opt_delta']])
    roll = [0] + roll
    
    for j in roll:
        output_dict = dict([(key, []) for key in ['type','terms','notional','par_01','atmf','K','premium','px_bps','opt_delta','imp_vol_norm','expiry', 'start', 'maturity']])
        for i in np.arange(len(option_type)):        
            if isinstance(t[i][0],str) == True:
                try:
                    effective = ql.Date(int(t[i][0].split('-')[0]),int(t[i][0].split('-')[1]),int(t[i][0].split('-')[2]))
                except:
                    if t[i][0][-1] in ('D','d'):
                        unit = ql.Days
                    elif t[i][0][-1] in ('W','w'):
                        unit = ql.Weeks
                    elif t[i][0][-1] in ('M','m'):
                        unit = ql.Months
                    effective = cal.advance(today,int(t[i][0][0:-1]),unit)

            else:
                effective = cal.advance(today, t[i][0], ql.Years)
                
            if isinstance(j, str) == True:
                if j[-1] in ('D','d'):
                    unit = ql.Days
                elif j[-1] in ('W','w'):
                    unit = ql.Weeks
                elif j[-1] in ('M','m'):
                    unit = ql.Months
                effective = cal.advance(effective,int(j[0:-1]),unit)
            else:
                effective = cal.advance(effective,j,ql.Years)
                

            start = cal.advance(effective, c.sett_d, ql.Days)
            maturity = cal.advance(start, int(t[i][1]), ql.Years)

            fixed_schedule = ql.Schedule(start, maturity, c.fixed[0], cal, ql.ModifiedFollowing, ql.ModifiedFollowing, ql.DateGeneration.Forward, False)
            float_schedule = ql.Schedule (start, maturity, c.floating[0], cal, ql.ModifiedFollowing, ql.ModifiedFollowing, ql.DateGeneration.Forward, False)
  
            if option_type[i] == 'P':
                swap_type = 1
            else:
                swap_type = -1
    
            swap = ql.VanillaSwap(swap_type , notional[i]*1000000, fixed_schedule, t[i][2]/100, c.fixed[1], float_schedule, index, 0.0, c.floating[1])
            underlying = Swap_Pricer([[swp_crv,t[i][0], int(t[i][1]),notional[i]*1000000]])
            atm_fwd = underlying.rate
            under_risk = underlying.risk[0]
 
            swaption_normal_model = ql.Swaption(swap, ql.EuropeanExercise(effective))
            swaption_normal_model.setPricingEngine(ql.BachelierSwaptionEngine(dc_curve, volc))
            prem = swaption_normal_model.NPV()*np.sign(notional[i])
            imp_vol_norm = 10000*swaption_normal_model.impliedVolatility(np.abs(prem), dc_curve,  0.003, 0.0000001, 500, 0.00001, 4.0 ,ql.Normal)
            delta = swaption_normal_model.delta()*np.sign(notional[i])/10000
            
            strat_risk = under_risk*( (strat_tag*notional[0]) + ((1-strat_tag)*notional[i]) ) / notional[i]

            output_dict['type'].append(option_type[i])
            output_dict['terms'].append(t[i])
            output_dict['notional'].append(notional[i])
            output_dict['expiry'].append(effective)
            output_dict['start'].append(start)
            output_dict['maturity'].append(maturity)
            output_dict['par_01'].append(int(np.round(under_risk,0)))
            output_dict['atmf'].append(np.round(atm_fwd[0],3))
            output_dict['K'].append(t[i][2])
            output_dict['premium'].append(int(np.round(prem,0)))
            output_dict['px_bps'].append(np.round(prem/strat_risk,1))
            output_dict['opt_delta'].append(int(np.round(delta,0)))
            output_dict['imp_vol_norm'].append(np.round(imp_vol_norm,1))
        
        output_dict['type'].append('')
        output_dict['terms'].append(j)
        output_dict['notional'].append('')
        output_dict['expiry'].append('')
        output_dict['start'].append('')
        output_dict['maturity'].append('')
        output_dict['par_01'].append(np.sum(output_dict['par_01']))
        output_dict['atmf'].append('')
        output_dict['K'].append('')
        output_dict['premium'].append(np.sum(output_dict['premium']))
        output_dict['px_bps'].append(np.sum(output_dict['px_bps']))
        output_dict['opt_delta'].append(np.sum(output_dict['opt_delta']))
        output_dict['imp_vol_norm'].append('')
        roll_dict[j] = output_dict

        for k in strat_dict.keys():
            strat_dict[k].append(output_dict[k][-1])
 
#    df_out1 = pd.DataFrame(roll_dict[0])
#    df_out2 = pd.DataFrame(strat_dict)
    
    class swaption_output():
        def __init__(self):
             self.ref_curve = swp_crv
             self.table = pd.DataFrame(roll_dict[0])
             self.roll = pd.DataFrame(strat_dict)
             
    return swaption_output()



#Swaption_Curve('SOFR_DC', [5, 30])

def Swaption_Curve(a, tails, expiries = ['1m','3m','6m','9m',1,'15m','18m','21m',2]):
#    a = 'SONIA_DC'
#    expiries = ['1m','3m','6m','9m',1,'15m','18m','21m',2]
#    tails = [5,30]
     
    spreads = [-50,-40,-30,-20,-10,0,10,20,30,40,50]
    notional = 100
    
    today = ql.Date(datetime.datetime.now().day,datetime.datetime.now().month,datetime.datetime.now().year)
    ql.Settings.instance().evaluationDate = today
    c = ccy(a,today)
    cal = c.cal
    
    if a == 'SONIA_DC':
        swp_crv = ois_dc_build(a, b=0)
        curve = ql.RelinkableYieldTermStructureHandle(swp_crv.curve)
        dc_curve = ql.RelinkableYieldTermStructureHandle(swp_crv.curve)
        index = ql.IborIndex(c.fixing, c.fixing_tenor, c.sett_d, c.curncy, c.cal, ql.ModifiedFollowing, True, c.floating[1], curve)
        volc = gbp_volc(curve, dc_curve, skew=1)
    elif a == 'SOFR_DC':
        swp_crv = ois_dc_build(a, b=0)
        curve = ql.RelinkableYieldTermStructureHandle(swp_crv.curve)
        dc_curve = ql.RelinkableYieldTermStructureHandle(swp_crv.curve)
        index = ql.IborIndex(c.fixing, c.fixing_tenor, c.sett_d, c.curncy, c.cal, ql.ModifiedFollowing, True, c.floating[1], curve)
        volc = usd_volc_sofr(curve, dc_curve, skew=1)
    elif a == 'USD_3M':
        swp_crv = swap_build(a, b=0)
        curve = ql.RelinkableYieldTermStructureHandle(swp_crv.curve[0])
        dc_curve = ql.RelinkableYieldTermStructureHandle(swp_crv.curve[1])
        index = c.index(c.fixing_tenor,curve)
        volc = usd_volc(curve, dc_curbe, skew=1)
    
###############################################################################
    fwds_dict = dict()
            
    for k in tails:
        for j in expiries:
            output_dict = dict([(key, []) for key in ['type','terms','notional','par_01','atmf','K','premium','px_bps','opt_delta','imp_vol_norm','expiry', 'start', 'maturity']])
            if isinstance(j, str) == True:
                if j[-1] in ('D','d'):
                    unit = ql.Days
                elif j[-1] in ('W','w'):
                    unit = ql.Weeks
                elif j[-1] in ('M','m'):
                    unit = ql.Months
                effective = cal.advance(today,int(j[0:-1]),unit)
            else:
                effective = cal.advance(today,j,ql.Years)
        
            for i in spreads:
                if i < 0.1:
                    swap_type = -1
                else:
                    swap_type = 1
            
            
                start = cal.advance(effective, c.sett_d, ql.Days)
                maturity = cal.advance(start, k, ql.Years)
                fixed_schedule = ql.Schedule(start, maturity, c.fixed[0], cal, ql.ModifiedFollowing, ql.ModifiedFollowing, ql.DateGeneration.Forward, False)
                float_schedule = ql.Schedule (start, maturity, c.floating[0], cal, ql.ModifiedFollowing, ql.ModifiedFollowing, ql.DateGeneration.Forward, False)
    
                underlying = Swap_Pricer([[swp_crv,j,k,notional*1000000]])
                atm_fwd = underlying.rate[0]
                under_risk = underlying.risk[0]

                swap = ql.VanillaSwap(swap_type , notional*1000000, fixed_schedule, (atm_fwd+(0.01*i))/100, c.fixed[1], float_schedule, index, 0.0, c.floating[1])
                swaption_normal_model = ql.Swaption(swap, ql.EuropeanExercise(effective))
                swaption_normal_model.setPricingEngine(ql.BachelierSwaptionEngine(dc_curve, volc))
                prem = swaption_normal_model.NPV()*np.sign(notional)
                imp_vol_norm = 10000*swaption_normal_model.impliedVolatility(np.abs(prem), dc_curve,  0.003, 0.0000001, 500, 0.00001, 4.0 ,ql.Normal)
                delta = swaption_normal_model.delta()*np.sign(notional)/10000
            
                strat_risk = under_risk

                output_dict['type'].append(i)
                output_dict['terms'].append(str(j)+' x '+str(k))
                output_dict['notional'].append(notional)
                output_dict['expiry'].append(effective)
                output_dict['start'].append(start)
                output_dict['maturity'].append(maturity)
                output_dict['par_01'].append(under_risk)
                output_dict['atmf'].append(atm_fwd)
                output_dict['K'].append(atm_fwd+(0.01*i))
                output_dict['premium'].append(prem)
                output_dict['px_bps'].append(prem/strat_risk)
                output_dict['opt_delta'].append(delta)
                output_dict['imp_vol_norm'].append(np.round(imp_vol_norm,1))
                
            fwds_dict[str(j)+' '+str(k)] = output_dict
    
    curve_fwd_dict = dict([(key, []) for key in expiries])
    for j in expiries:
        output2_dict = dict([(key, []) for key in ['type','terms','par_01','atmf_1','atmf_2','K1','K2','crv_atmf','sprd','adj_crv_fwd']])
        df1 = pd.DataFrame(fwds_dict[str(j)+' '+str(tails[0])])
        df2 = pd.DataFrame(fwds_dict[str(j)+' '+str(tails[1])])
    
        df2['premium'] = df2['px_bps']*df1['par_01']
        df2['opt_delta'] = (df2['opt_delta']*df1['par_01'])/df2['par_01']
        df2['par_01'] = df1['par_01']
    
        prem_tot = df1['premium']-df2['premium']
        disc = prem_tot / df1['opt_delta']   ###### to be applited to DF2 instrument leg !!!! 
        
        for i in np.arange(len(df1)):
            output2_dict['type'].append(df1['type'][i])
            output2_dict['terms'].append(df1['terms'][i]+' '+df2['terms'][i])
            output2_dict['par_01'].append(df1['par_01'][i])
            output2_dict['atmf_1'].append(df1['atmf'][i])
            output2_dict['atmf_2'].append(df2['atmf'][i])
            output2_dict['K1'].append(df1['K'][i])
            output2_dict['K2'].append(df2['K'][i])
            output2_dict['crv_atmf'].append(100*(output2_dict['atmf_2'][i]-output2_dict['atmf_1'][i]))
            if df1['type'][i] == 0:
                output2_dict['sprd'].append(0.0)
            else:
                output2_dict['sprd'].append(disc[i])
            output2_dict['adj_crv_fwd'].append(output2_dict['crv_atmf'][i]-output2_dict['sprd'][i])
    
        curve_fwd_dict[j] = pd.DataFrame(output2_dict)
        

    swaption_curve_hm = pd.DataFrame()
    swaption_curve_hm['type'] = curve_fwd_dict['3m']['type']
    for j in expiries:
        swaption_curve_hm[j] = curve_fwd_dict[j]['adj_crv_fwd'] 

    swaption_curve_hm.set_index('type',drop=True, inplace=True)


    fig, axs = plt.subplots(1, 1, figsize=(8, 6));
    ax1 = plt.subplot(1, 1, 1);
    ax1.set_title('Curve: '+str(a)+': '+str(tails[0])+' / '+str(tails[1])+' : 0 premium strikes');
    sns.heatmap(swaption_curve_hm[::-1], cmap='Blues', linewidths=1, annot=swaption_curve_hm[::-1], yticklabels=swaption_curve_hm[::-1].index, xticklabels=swaption_curve_hm[::-1].columns, fmt=".1f", cbar=False, ax=ax1);
    plt.xlabel('Expiries');
    plt.ylabel(str(tails[0])+'y ATMF + K');

#    class swaption_crv_output():
#        def __init__(self):
#             self.crv_tab = curve_fwd_dict
#             self.fwds_tab = fwds_dict
             
    return fig;














#### Build Vol Cube

#### FMD 3M Libor
def usd_volc(curve, dc_curve, skew = 1):
    
    ### ATM
    expiry = ['1M','2M','3M','6M','9M','1Y','18M','2Y','3Y']
    tail = ['1Y','2Y','3Y','4Y','5Y','6Y','7Y','8Y','9Y','10Y','12Y','15Y','20Y','25Y','30Y']
    r1 = [['USD'+i+j+'3LATM=FMD'  for j in tail ] for i in expiry]
    r1 = flat_lst(r1)
    
    atm_vols, strike = ek.get_data(r1,  fields=['GEN_VAL7','GEN_VAL1']) 
    normal_vols = [  list(atm_vols['GEN_VAL7'][i*len(tail):(i+1)*len(tail)]) for i in np.arange(len(expiry)) ]
    
    swapTenors = [ql.Period(tenor) for tenor in tail]
    optionTenors = [ql.Period(tenor) for tenor in expiry]
    normal_vols = [[vol / 10000 for vol in row] for row in normal_vols]
    
    calendar = ql.UnitedStates()
    bdc = ql.ModifiedFollowing
    dayCounter = ql.Thirty360(ql.Thirty360.BondBasis)
    swaptionVolMatrix = ql.SwaptionVolatilityMatrix(calendar, bdc, optionTenors, swapTenors, ql.Matrix(normal_vols), dayCounter, False, ql.Normal)
    
    ### Skews
    strikeSpreads = [ -0.015, -0.010,-0.0075,-0.0050, -0.0025, -0.00125, 0.00125, 0.0025, 0.0050, 0.0075, 0.010, 0.015]

    #'USD2M2Y3LN300=FMD'
    #'USD1Y1Y3L0125=FMD'

    r2 = [[['USD'+i+j+k+'=FMD' for k in ['3LN150','3LN100','3LN075','3LN050','3LN025','3LN0125', '3L0125','3L025','3L050','3L075','3L100','3L0150']] for j in tail] for i in expiry] 
    r2 = flat_lst(r2)
    r2 = flat_lst(r2)

    skews, strike = ek.get_data(r2,  fields=['GEN_VAL7','GEN_VAL1']) 

    volSpreads  = [list(0.0001*skews['GEN_VAL7'][i*len(strikeSpreads):(i+1)*len(strikeSpreads)]) for i in np.arange(len(expiry)*len(tail)) ]
    if skew == 0:
        volSpreads   = [[0.0]*len(strikeSpreads)]*len(expiry)*len(tail)   ###### set vol spreads to 0

    volSpreads = [[ql.QuoteHandle(ql.SimpleQuote(v)) for v in row] for row in volSpreads]

    swapIndexBase = ql.UsdLiborSwapIsdaFixAm(ql.Period(6, ql.Months), curve, dc_curve)
    shortSwapIndexBase = ql.UsdLiborSwapIsdaFixAm(ql.Period(6, ql.Months), curve, dc_curve)
    vegaWeightedSmileFit = False

    volCube = ql.SwaptionVolatilityStructureHandle(ql.SwaptionVolCube2(ql.SwaptionVolatilityStructureHandle(swaptionVolMatrix),
                                                                       optionTenors, swapTenors, strikeSpreads, volSpreads,
                                                                       swapIndexBase, shortSwapIndexBase, vegaWeightedSmileFit))
    volCube.enableExtrapolation()
    
    return volCube

#### TRADS SOFR
def usd_volc_sofr(curve, dc_curve, skew = 1):
    ### ATM
    expiry = ['1M','2M','3M','6M','9M','1Y','18M','2Y','3Y']
    tail = ['1Y','2Y','3Y','4Y','5Y','6Y','7Y','8Y','9Y','10Y','12Y','15Y','20Y','25Y','30Y']
    r1 = [['USD'+i+j+'SRATM=TRDL'  for j in tail ] for i in expiry]
    r1 = flat_lst(r1)
    
    atm_vols, strike = ek.get_data(r1,  fields=['GEN_VAL7','GEN_VAL1']) 
    normal_vols = [  list(atm_vols['GEN_VAL7'][i*len(tail):(i+1)*len(tail)]) for i in np.arange(len(expiry)) ]
    
    swapTenors = [ql.Period(tenor) for tenor in tail]
    optionTenors = [ql.Period(tenor) for tenor in expiry]
    normal_vols = [[vol / 10000 for vol in row] for row in normal_vols]
    
    calendar = ql.UnitedStates()
    bdc = ql.ModifiedFollowing
    dayCounter = ql.Thirty360(ql.Thirty360.BondBasis)
    swaptionVolMatrix = ql.SwaptionVolatilityMatrix(calendar, bdc, optionTenors, swapTenors, ql.Matrix(normal_vols), dayCounter, False, ql.Normal)
    
    ### Skews
    strikeSpreads = [ -0.015, -0.010,-0.0075,-0.0050, -0.0025, -0.0010, -0.0005, 0.0005, 0.0010, 0.0025, 0.0050, 0.0075, 0.010, 0.015]

    #'USD2M2Y3LN300=FMD'
    #'USD1Y1Y3L0125=FMD'

    r2 = [[['USD'+i+j+k+'=TRDL' for k in ['SRN150','SRN100','SRN75','SRN50','SRN25','SRN10', 'SRN5', 'SRP5', 'SRP10','SRP25','SRP50','SRP75','SRP100','SRP150']] for j in tail] for i in expiry] 
    r2 = flat_lst(r2)
    r2 = flat_lst(r2)

    skews, strike = ek.get_data(r2,  fields=['GEN_VAL7','GEN_VAL1']) 

    volSpreads  = [list(0.0001*skews['GEN_VAL7'][i*len(strikeSpreads):(i+1)*len(strikeSpreads)]) for i in np.arange(len(expiry)*len(tail)) ]
    
    ######## converting Outright vols to vol spreads  ######
    n1 = np.array(flat_lst( np.array(normal_vols)))
    for i in np.arange(len(volSpreads)):
        v2 = np.array(volSpreads[i])
        n2 = np.array(n1[i])
        volSpreads[i] = list(v2 - n2)

    
    if skew == 0:
        volSpreads   = [[0.0]*len(strikeSpreads)]*len(expiry)*len(tail)   ###### set vol spreads to 0

    volSpreads = [[ql.QuoteHandle(ql.SimpleQuote(v)) for v in row] for row in volSpreads]
    
    swapIndexBase = ql.UsdLiborSwapIsdaFixAm(ql.Period(6, ql.Months), curve, dc_curve)
    shortSwapIndexBase = ql.UsdLiborSwapIsdaFixAm(ql.Period(6, ql.Months), curve, dc_curve)
    vegaWeightedSmileFit = False

    volCube = ql.SwaptionVolatilityStructureHandle(ql.SwaptionVolCube2(ql.SwaptionVolatilityStructureHandle(swaptionVolMatrix),
                                                                       optionTenors, swapTenors, strikeSpreads, volSpreads,
                                                                       swapIndexBase, shortSwapIndexBase, vegaWeightedSmileFit))
    volCube.enableExtrapolation()
    
    return volCube



def gbp_volc(curve, dc_curve, skew = 1):
    
    ### ATM
    expiry = ['1M','2M','3M','6M','9M','1Y','18M','2Y','3Y']
    tail = ['1Y','2Y','3Y','4Y','5Y','6Y','7Y','8Y','9Y','10Y','12Y','15Y','20Y','25Y','30Y']
    r1 = [['GBP'+i+j+'SOATM=TRDL'  for j in tail ] for i in expiry]
    r1 = flat_lst(r1)
    
    atm_vols, strike = ek.get_data(r1,  fields=['GEN_VAL7','GEN_VAL1']) 
    normal_vols = [  list(atm_vols['GEN_VAL7'][i*len(tail):(i+1)*len(tail)]) for i in np.arange(len(expiry)) ]
    
    swapTenors = [ql.Period(tenor) for tenor in tail]
    optionTenors = [ql.Period(tenor) for tenor in expiry]
    normal_vols = [[vol / 10000 for vol in row] for row in normal_vols]
    
    calendar = ql.UnitedStates()
    bdc = ql.ModifiedFollowing
    dayCounter = ql.Thirty360(ql.Thirty360.BondBasis)
    swaptionVolMatrix = ql.SwaptionVolatilityMatrix(calendar, bdc, optionTenors, swapTenors, ql.Matrix(normal_vols), dayCounter, False, ql.Normal)
    
    ### Skews
    strikeSpreads = [ -0.015, -0.010,-0.0075,-0.0050, -0.0025, -0.00125, 0.00125, 0.0025, 0.0050, 0.0075, 0.010, 0.015]

    r2 = [[['GBP'+i+j+k+'=TRDL' for k in ['SON150','SON100','SON75','SON50','SON25','SON125', 'SOP125','SOP25','SOP50','SOP75','SOP00','SOP150']] for j in tail] for i in expiry] 
    r2 = flat_lst(r2)
    r2 = flat_lst(r2)

    skews, strike = ek.get_data(r2,  fields=['GEN_VAL7','GEN_VAL1']) 

    volSpreads  = [list(0.0001*skews['GEN_VAL7'][i*len(strikeSpreads):(i+1)*len(strikeSpreads)]) for i in np.arange(len(expiry)*len(tail)) ]
    if skew == 0:
        volSpreads   = [[0.0]*len(strikeSpreads)]*len(expiry)*len(tail)   ###### set vol spreads to 0

    volSpreads = [[ql.QuoteHandle(ql.SimpleQuote(v)) for v in row] for row in volSpreads]
    
    swapIndexBase = ql.UsdLiborSwapIsdaFixAm(ql.Period(1, ql.Years), curve, dc_curve)
    shortSwapIndexBase = ql.UsdLiborSwapIsdaFixAm(ql.Period(1, ql.Years), curve, dc_curve)
    vegaWeightedSmileFit = False

    volCube = ql.SwaptionVolatilityStructureHandle(ql.SwaptionVolCube2(ql.SwaptionVolatilityStructureHandle(swaptionVolMatrix),
                                                                       optionTenors, swapTenors, strikeSpreads, volSpreads,
                                                                       swapIndexBase, shortSwapIndexBase, vegaWeightedSmileFit))
    volCube.enableExtrapolation()
    
    return volCube


#GBP1Y3YSOP5=TRDL
#GBP1Y2YSOATM=TRDL

#GBP1Y3YSOP50=TRDL
#GBP1Y2YSON50=TRDL


####################### sundry


#today = ql.Date(datetime.datetime.now().day,datetime.datetime.now().month,datetime.datetime.now().year)
#ql.Settings.instance().evaluationDate = today
# Underlying swap definition
#usd3m = swap_build('USD_3M', b=-2)

#curve = ql.YieldTermStructureHandle(ql.FlatForward(today, 0.03, ql.Actual365Fixed()))
#libor_3m = ql.USDLibor(ql.Period('3M'), curve)

#curve = ql.RelinkableYieldTermStructureHandle(usd3m.curve[0])
#dc_curve = ql.RelinkableYieldTermStructureHandle(usd3m.curve[1])
#libor_3m = ql.USDLibor(ql.Period('3M'), curve)

#calendar = ql.UnitedStates()
#effective = calendar.advance(today, 1, ql.Years)
#maturity = calendar.advance(effective+2, 10, ql.Years)
#fixed_schedule = ql.Schedule(effective+2, maturity, ql.Period('6M'), calendar,
#                             ql.ModifiedFollowing, ql.ModifiedFollowing,
#                             ql.DateGeneration.Forward, False)
#float_schedule = ql.Schedule (effective+2, maturity, ql.Period('3M'), calendar,
#                              ql.ModifiedFollowing, ql.ModifiedFollowing,
#                              ql.DateGeneration.Forward, False)

#usd_vol1 = usd_volc(skew=1)


#Swap_Pricer([[usd3m,1,10]]).rate
#Swap_Pricer([[usd3m,'07-10-2022',5]]).rate
#Swap_Pricer([[usd3m,'05-10-2022',5]]).rate
#Swap_Pricer([[usd3m,'07-10-2022',5]]).dates
#Swap_Pricer([[usd3m,1,5]]).dates

###### dc disc 
#rate = (1.685) / 100
#swap = ql.VanillaSwap(ql.VanillaSwap.Payer, 100000000,
#               fixed_schedule, rate, ql.Thirty360(ql.Thirty360.BondBasis),
#               float_schedule, libor_3m, 0.0, ql.Actual360())

#swap.setPricingEngine(ql.DiscountingSwapEngine(dc_curve))
#swap.fairRate()*100

#swaption_normal_model = ql.Swaption(swap, ql.EuropeanExercise(effective))
#swaption_normal_model.setPricingEngine(ql.BachelierSwaptionEngine(dc_curve, usd_vol1))
#swaption_normal_model.NPV()

#swaption_normal_model.impliedVolatility(swaption_normal_model.NPV(), dc_curve,  0.003, 0.0000001, 500, 0.00001, 4.0 ,ql.Normal)




####### single disc 
#rate = 1.65 / 100
#swap = ql.VanillaSwap(ql.VanillaSwap.Payer, 100000000,
#               fixed_schedule, rate, ql.Thirty360(ql.Thirty360.BondBasis),
#               float_schedule, libor_3m, 0.0, ql.Actual360())

#swaption_normal_model = ql.Swaption(swap, ql.EuropeanExercise(effective))

#normal_vol = ql.SimpleQuote(0.0073)
#swaption_normal_model.setPricingEngine(ql.BachelierSwaptionEngine(dc_curve, ql.QuoteHandle(normal_vol)))
#swaption_normal_model.NPV()

#######  cash settle
#rate = 1.6853 / 100
#swap = ql.VanillaSwap(ql.VanillaSwap.Payer, 100000000,
#               fixed_schedule, rate, ql.Thirty360(ql.Thirty360.BondBasis),
#               float_schedule, libor_3m, 0.0, ql.Actual360())

#swaption_normal_model = ql.Swaption(swap, ql.EuropeanExercise(effective),  ql.Settlement.Cash, ql.Settlement.ParYieldCurve)

#normal_vol = ql.SimpleQuote(0.00771)
#swaption_normal_model.setPricingEngine(ql.BachelierSwaptionEngine(dc_curve, ql.QuoteHandle(normal_vol)))
#swaption_normal_model.NPV()


#swaption_normal_model.delta()/10000
#swaption_normal_model.vega()/10000
#swaption_normal_model.theta()


