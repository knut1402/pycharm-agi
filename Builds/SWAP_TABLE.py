# fwds , spreads and flys table:
############################# Output Table Function
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
from SWAP_BUILD import swap_build
from OIS_DC_BUILD import ois_dc_build
from SWAP_PRICER import Swap_Pricer, quick_swap
from Utilities import *


def swap_table(a, offset = [-1], shift = [0,'1M','3M','6M',1]):
    
    """ Author = RS 
        a            : curve handle [= swap_build()]
        offset == -1 : changes in rates / fwds / sprds / flys; default :COD [-1]
        shift        : fwd curve sprds / flys default: [0,'1M','3M','6M',1]
        
        outputs      : curves used (curve, dc), curve date and fixing, 
                       rates, fwds, sprds, flys as separate tables,
                       rates, fwds, sprds, flys combined as output_table
                       rates, fwds, sprds, flys combined as list
                       fwd curve sprds / flys combines as  fwdcurve table      """
    
#    a = sofr
#    a = ester
#    offset = [-1, -5]
#    offset = ['20-12-2021', -10, '04-01-2021']
    
    today = ql.Date(datetime.datetime.now().day,datetime.datetime.now().month,datetime.datetime.now().year)
    if a.ois_trigger == 0:
        sw_tab_index = a.index
    else:
        sw_tab_index = a.ois_index
        
    c = ccy(sw_tab_index, today)
    t1 = pd.DataFrame()
    t1 = a.rates.copy()
    t = []

#    for i in np.arange(len(offset)):
#        if  isinstance(offset[i],int) == True:
#            x1 = c.cal.advance(a.trade_date,offset[i],ql.Days)
#            if a.ois_trigger == 0:
#                t = t + [swap_build(sw_tab_index, str(x1.dayOfMonth())+'-'+str(x1.month())+'-'+str(x1.year())  ) ]
#            else:
#                t = t + [ois_dc_build(sw_tab_index, str(x1.dayOfMonth())+'-'+str(x1.month())+'-'+str(x1.year())  ) ]
#        else:
#            if a.ois_trigger == 0:
#                t = t + [swap_build(sw_tab_index, offset[i])]
#            else:
#                t = t + [ois_dc_build(sw_tab_index, offset[i])]


    for i in np.arange(len(offset)):
        if a.ois_trigger == 0:
            t = t + [swap_build(sw_tab_index, offset[i])]
        else:
            t = t + [ois_dc_build(sw_tab_index, b=offset[i])]


            
#    x1 = [c.cal.advance(a.trade_date,offset[i],ql.Days) for i in range(len(offset)) ]
        
    ################################### make offsets === equal dates as well !!  --- how for heatmap and swap table ???
#    if a.ois_trigger == 0:
#        t = [swap_build(sw_tab_index,    str(x1[i].dayOfMonth())+'-'+str(x1[i].month())+'-'+str(x1[i].year())  ) for i in range(len(offset)) ]
#    else:
#        t = [ois_dc_build(sw_tab_index,    str(x1[i].dayOfMonth())+'-'+str(x1[i].month())+'-'+str(x1[i].year())  ) for i in range(len(offset)) ]
    chg = ['d:'+str(offset[i]) for i in range(len(offset))]
    
    ########### dates
    trade_dates = [a.trade_date] + [t[i].trade_date for i in np.arange(len(t))]
    
    
 ##################### Fwds Table
    output_table = pd.DataFrame()
    output_fwdcurve = pd.DataFrame()
    calc_fwds = pd.DataFrame()
    calc_sprds = pd.DataFrame()
    calc_flys = pd.DataFrame()
    
    a1 = pd.Series([Swap_Pricer([[a,1,1]]), Swap_Pricer([[a,2,1]]), Swap_Pricer([[a,3,1]]),
                    Swap_Pricer([[a,4,1]]), Swap_Pricer([[a,2,2]]), Swap_Pricer([[a,3,2]]),
                    Swap_Pricer([[a,5,5]]), Swap_Pricer([[a,10,5]]), Swap_Pricer([[a,10,10]]),
                    Swap_Pricer([[a,15,15]]) ])
        
    a11 = [pd.Series([Swap_Pricer([[t[i],1,1]]), Swap_Pricer([[t[i],2,1]]), Swap_Pricer([[t[i],3,1]]),
                    Swap_Pricer([[t[i],4,1]]), Swap_Pricer([[t[i],2,2]]), Swap_Pricer([[t[i],3,2]]),
                    Swap_Pricer([[t[i],5,5]]), Swap_Pricer([[t[i],10,5]]), Swap_Pricer([[t[i],10,10]]),
                    Swap_Pricer([[t[i],15,15]]) ]) for i in range(len(offset)) ]

    a2 = pd.Series([Swap_Pricer([[a,0,2],[a,0,3]]).spread, Swap_Pricer([[a,0,2],[a,0,5]]).spread,
                    Swap_Pricer([[a,0,2],[a,0,10]]).spread, Swap_Pricer([[a,0,5],[a,0,10]]).spread,
                    Swap_Pricer([[a,0,5],[a,0,30]]).spread, Swap_Pricer([[a,0,10],[a,0,30]]).spread ])
    
    a21 = [pd.Series([Swap_Pricer([[t[i],0,2],[t[i],0,3]]).spread, Swap_Pricer([[t[i],0,2],[t[i],0,5]]).spread,
                    Swap_Pricer([[t[i],0,2],[t[i],0,10]]).spread, Swap_Pricer([[t[i],0,5],[t[i],0,10]]).spread,
                    Swap_Pricer([[t[i],0,5],[t[i],0,30]]).spread, Swap_Pricer([[t[i],0,10],[t[i],0,30]]).spread ]) for i in range(len(offset))]

    a3 = pd.Series([Swap_Pricer([[a,0,2],[a,0,3],[a,0,5]]).fly,
                    Swap_Pricer([[a,0,2],[a,0,5],[a,0,10]]).fly,
                    Swap_Pricer([[a,0,3],[a,0,5],[a,0,7]]).fly,
                    Swap_Pricer([[a,0,5],[a,0,10],[a,0,30]]).fly  ])
        
    a31 = [pd.Series([Swap_Pricer([[t[i],0,2],[t[i],0,3],[t[i],0,5]]).fly,
                    Swap_Pricer([[t[i],0,2],[t[i],0,5],[t[i],0,10]]).fly,
                    Swap_Pricer([[t[i],0,3],[t[i],0,5],[t[i],0,7]]).fly,
                    Swap_Pricer([[t[i],0,5],[t[i],0,10],[t[i],0,30]]).fly  ]) for i in range(len(offset)) ]

    calc_fwds['Fwds'] = [a1[i].name[0] for i in range(len(a1))]
    calc_fwds['Rate'] =  [a1[i].rate[0] for i in range(len(a1))]
    for i in range(len(offset)):
        calc_fwds[chg[i]] =  np.round(100*(calc_fwds['Rate'] - [a11[i][j].rate[0] for j in range(len(a1))]  ),1)
       
    calc_sprds['Curve'] = ['2 - 3','2 - 5','2 - 10','5 - 10','5 - 30','10 - 30']
    calc_sprds['Rate'] =  a2[0:]
    for i in range(len(offset)):
        calc_sprds[chg[i]] =  calc_sprds['Rate'] - a21[i][0:] 
        
    calc_flys['Fly'] = ['2.3.5','2.5.10','3.5.7','5.10.30']
    calc_flys['Rate'] =  a3[0:]
    for i in range(len(offset)):
        calc_flys[chg[i]] =  calc_flys['Rate'] - a31[i][0:] 
    
    for i in range(len(offset)):
        t1[chg[i]] = np.round(100*(t1['SwapRate']- t[i].rates['SwapRate']),1)
    
    list1 = pd.concat([t1, calc_fwds, calc_sprds, calc_flys])
    output_table = pd.concat([t1, calc_fwds, calc_sprds, calc_flys], axis =1)

    
    n_offset = len(offset)
    
    output_table.loc[:,'SwapRate'] = output_table.loc[:,'SwapRate'].round(decimals = 3)
    for i in np.arange(len(offset)):
            output_table.iloc[:,2+i] = output_table.iloc[:,2+i].round(decimals = 1)                                   
            output_table.iloc[:,5+i+n_offset-1] = output_table.iloc[:,5+i+n_offset-1].round(decimals = 1)
            output_table.iloc[:,8+i+(2*(n_offset-1))] = output_table.iloc[:,8+i+(2*(n_offset-1))].round(decimals = 1) 
            output_table.iloc[:,11+i+(3*(n_offset-1))] = output_table.iloc[:,11+i+(3*(n_offset-1))].round(decimals = 1)
            
        
    output_table.iloc[:,4+n_offset-1] = output_table.iloc[:,4+n_offset-1].round(decimals = 3)                     #### fwd rate
    output_table.iloc[:,7+(2*(n_offset-1))] = output_table.iloc[:,7+(2*(n_offset-1))].round(decimals = 1)         #### curve rate 
    output_table.iloc[:,10+(3*(n_offset-1))] = output_table.iloc[:,10+(3*(n_offset-1))].round(decimals = 1)       #### fly rate

    output_table = output_table.fillna('')

    #output_table
     
####################  Fwd Roll Table
    
    c1 = (sw_tab_index).split('_')[0].lower()
    #shift = [0,'1M','3M','6M',1]
    
    if (a.nodes[-1][0]-a.ref_date)/365.25 < 16:
        a4 = [( (c1+' 2-3', [[a,shift[i],2],[a,shift[i],3]]),
            (c1+' 2-5', [[a,shift[i],2],[a,shift[i],5]]),
            (c1+' 2-10', [[a,shift[i],2],[a,shift[i],10]]),
            (c1+' 5-10', [[a,shift[i],5],[a,shift[i],10]]), ) for i in range(len(shift)) ]
    else:  
        a4 = [( (c1+' 2-3', [[a,shift[i],2],[a,shift[i],3]]),
               (c1+' 2-5', [[a,shift[i],2],[a,shift[i],5]]),
               (c1+' 2-10', [[a,shift[i],2],[a,shift[i],10]]),
               (c1+' 5-10', [[a,shift[i],5],[a,shift[i],10]]),
               (c1+' 5-30', [[a,shift[i],5],[a,shift[i],30]]),
               (c1+' 10-30', [[a,shift[i],10],[a,shift[i],30]]),  ) for i in range(len(shift)) ]
    
    n = len(a4[1])
    sprdfwd = pd.DataFrame()
    
    for i in range(len(shift)):
        sprdfwd[shift[i]] = [Swap_Pricer(a4[i][j][1]).spread for j in range(n)]
    
    sprdfwd.index = [a4[0][i][0] for i in range(n)]   
    
    if (a.nodes[-1][0]-a.ref_date)/365.25 < 16:
        a5 = [( (c1+' 2-3-5', [[a,shift[i],2],[a,shift[i],3],[a,shift[i],5]]),
               (c1+' 2-5-10', [[a,shift[i],2],[a,shift[i],5],[a,shift[i],10]]),
               (c1+' 3-5-7', [[a,shift[i],3],[a,shift[i],5],[a,shift[i],7]])    ) for i in range(len(shift)) ]
    else:
        a5 = [( (c1+' 2-3-5', [[a,shift[i],2],[a,shift[i],3],[a,shift[i],5]]),
               (c1+' 2-5-10', [[a,shift[i],2],[a,shift[i],5],[a,shift[i],10]]),
               (c1+' 3-5-7', [[a,shift[i],3],[a,shift[i],5],[a,shift[i],7]]),
               (c1+' 5-10-30', [[a,shift[i],5],[a,shift[i],10],[a,shift[i],30]])    ) for i in range(len(shift)) ]
    
    n2 = len(a5[1])
    flyfwd = pd.DataFrame()
    
    for i in range(len(shift)):
        flyfwd[shift[i]] = [Swap_Pricer(a5[i][j][1]).fly for j in range(n2)]
    
    flyfwd.index = [a5[0][i][0] for i in range(n2)]   
    
    output_fwdcurve = pd.concat([sprdfwd,flyfwd])
        
    
    #output_curve
 
    class swap_table_output():
        def __init__(self):
            self.curve = a.curve
            self.all_curves = [a]+t
            self.ref_date = a.ref_date
            self.trade_date = a.trade_date
            self.dates = trade_dates
            self.ref_fix = a.ref_fix
            self.rates = t1
            self.fwds = calc_fwds
            self.sprds = calc_sprds
            self.flys = calc_flys
            self.table = output_table
            self.fwdcurve = output_fwdcurve 
            self.aslist = list1
    
    return swap_table_output()


### testing
#sofr = ois_dc_build("SOFR_DC",b=0)
#tab1= swap_table(sofr)
#tab1.table

#tab1= swap_table2([sofr], outright_rates = [1,2,3,4,5,6,7,8,9,10,12,15,20,25,30,40,50],
#                  fwd_rates = [(1,1), (2,1), (3,1), (4,1), (2,2), (3,2), (5,5), (10,5), (10,10), (15,15) ],
#                  curve_rates = [(2,3), (2,5), (2,10), (5,10), (5,30), (10,30)],
#                  fly_rates = [(2,3,5), (2,5,10), (3,5,7), (5,10,30)])

#tab1.fly

####################### heatmap for rates, curves

def curve_hmap(a,b=-1, offset=[-1], ois_flag = 0):
#    a = g= ['EUR_6M','PLN_6M','HUF_6M','CZK_6M']
    curve_rates = {}
    curve_rates_chg = {}
    curve_fwds = {}
    curve_crvs = {}
    curve_flys = {}
    curve_rolls = {}
    for i in a:
        print(i)
        if ois_flag == 0:
            curve = swap_build(i, b)
        else:
            curve = ois_dc_build(i, b)
    
        tab = swap_table(curve, offset)
        tab.rates.set_index('Tenor', drop=True, inplace=True)
        curve_rates[curve.ccy] = tab.rates['SwapRate']
        curve_rates_chg[curve.ccy] = tab.rates.iloc[:,1:]
        curve_fwds[curve.ccy] = tab.fwds
        curve_crvs[curve.ccy] = tab.sprds
        curve_flys[curve.ccy] = tab.flys
        tab.fwdcurve.reset_index(inplace=True)
        curve_rolls[curve.ccy] = tab.fwdcurve
    
    #### outright par rates
    rates_all = pd.DataFrame()
    rates_all = curve_rates[list(curve_rates.keys())[0]]
    for i in list(curve_rates.keys())[1:]:
        rates_all = pd.concat([rates_all,curve_rates[i]], axis=1)
    rates_all.columns = curve_rates.keys()
    rates_all = rates_all.round(3)
#    rates_all = rates_all.fillna(0)
    
    #### outright par rates changes
    rates_all_changes = {}
    for j in offset:
        rates_all_changes[j] = pd.DataFrame()
        rates_all_changes[j] = curve_rates_chg[list(curve_rates_chg.keys())[0]]
        for i in list(curve_rates_chg.keys())[1:]:
            rates_all_changes[j] = pd.concat([rates_all_changes[j],curve_rates_chg[i]], axis=1)
        rates_all_changes[j].columns = curve_rates_chg.keys()
#        rates_all_changes[j] = rates_all_changes[j]
        
    
    #### outright fwd levels
    curve_all = pd.DataFrame()
    for i in curve_fwds.keys():
        curve_all[i] = np.round(curve_fwds[i]['Rate'],3)
    curve_all.index = curve_fwds[i]['Fwds']
    
    ### steepness and curvature
    steep_all = pd.DataFrame()
    
    use_len = []
    for i in curve_rolls.keys():
        use_len.append(len(curve_rolls[i]))
    max_len = list(curve_rolls.keys())[use_len.index(max(use_len))]

    for i in curve_rolls.keys():
        steep_all[i] = np.round(curve_rolls[i][0],3)
    steep_all.index = [curve_rolls[max_len ]['index'][j][5:] for j in np.arange(len(steep_all))]
    
    use_len = []
    for i in curve_rolls.keys():
        use_len.append(len(curve_rolls[i]))
    use_len.index(max(use_len)) 
    
    
    ### roll
    rolls = {}
    roll_sched = curve_rolls[i].columns[2:].tolist()
    for i in roll_sched:
        rolls[i] = pd.DataFrame()
        for j in curve_rolls.keys():
            rolls[i][j] = curve_rolls[j][0] - curve_rolls[j][i]
        rolls[i].index = steep_all.index
    
    #### changes 
    chg_all = {}
    steep_chg_all = {}
    fly_chg_all = {}
    for j in offset:
        chg_all[j] = pd.DataFrame()
        for i in curve_fwds.keys():
            chg_all[j][i] = curve_fwds[i]['d:'+str(j)]
        chg_all[j].index = curve_fwds[i]['Fwds']
        
        steep_chg_all[j] = pd.DataFrame()
        for i in curve_crvs.keys():
            steep_chg_all[j][i] = curve_crvs[i]['d:'+str(j)]
        steep_chg_all[j].index = curve_crvs[i]['Curve']
        
        fly_chg_all[j] = pd.DataFrame()
        for i in curve_flys.keys():
            fly_chg_all[j][i] = curve_flys[i]['d:'+str(j)]
        fly_chg_all[j].index = curve_flys[i]['Fly']
        fly_chg_all[j].index.name ='Curve'

        steep_chg_all[j] = pd.concat([steep_chg_all[j],fly_chg_all[j]])

    
    class curve_hmap_output():
        def __init__(self):
            self.rates = rates_all
            self.curves = curve_all
            self.steep = steep_all
            self.roll = rolls
            self.rates_chg = rates_all_changes
            self.chg = chg_all
            self.steep_chg = steep_chg_all
            self.offset = offset
            self.dates = tab.dates
            self.roll_schedule = roll_sched
    
    return curve_hmap_output()



################################################## Swap Calc for Quixotic monitor

def swap_table2(crvs, outright_rates, fwd_rates, curve_rates, fly_rates,  shift = [0,'1M','3M','6M',1], price_nodes = 1):
    
#    crvs = [sofr, sofr2]
    shift = [0,'1M','3M','6M',1]
    outright_rates = [1,2,3,4,5,6,7,8,9,10,12,15,20,25,30,40,50]
    fwd_rates = [(1,1), (2,1), (3,1), (4,1), (2,2), (3,2), (5,5), (10,5), (10,10), (15,15) ]
    curve_rates = [(2,3), (2,5), (2,10), (5,10), (5,30), (10,30)]
    fly_rates = [(2,3,5), (2,5,10), (3,5,7), (5,10,30)]

    try:
        c = ccy(crvs[0].ois_index, ql.Date(datetime.datetime.now().day,datetime.datetime.now().month,datetime.datetime.now().year))
    except:
        c = ccy(crvs[0].index, ql.Date(datetime.datetime.now().day,datetime.datetime.now().month,datetime.datetime.now().year))
    
    if c.fixing_tenor < ql.Period("6m"):
        fra_step = '3m'
    else:
        fra_step = '3m'

    if price_nodes == 1:
        x1 = []
        for i in np.arange(len(outright_rates)):
            x1.append([ Swap_Pricer([[crvs[j],0,outright_rates[i]]]).rate[0] for j in np.arange(len(crvs))] )
    
        x_fra = FUT_CT_Q(crvs[0].ref_date)[:13]
        x5 = []
        for i in x_fra['Date']:
            x5.append( [ Swap_Pricer([[crvs[j], str(i.dayOfMonth())+'-'+str(i.month())+'-'+str(i.year()), fra_step]]).rate[0] for j in np.arange(len(crvs))] )
        
        fra = flat_lst( [ (x5[i][0], [100*(x5[i][0]-x5[i][j]) for j in np.arange(1,len(crvs))]) for i in np.arange(len(x5))] )
        par = flat_lst( [ (x1[i][0], [100*(x1[i][0]-x1[i][j]) for j in np.arange(1,len(crvs))]) for i in np.arange(len(x1))] )
    else:
        fra = []
        par = []
        
    x2 = []
    for i,j in fwd_rates:
        x2.append([ Swap_Pricer([[crvs[k],i,j]]).rate[0] for k in np.arange(len(crvs))] )
    
    x3 = []
    x4 = []  
    for s in shift:
        for i,j in curve_rates:
            x3.append([ Swap_Pricer([[crvs[l],s,i],[crvs[l],s,j]]).spread for l in np.arange(len(crvs))] )
        for i,j,k in fly_rates:
            x4.append([ Swap_Pricer([[crvs[l],s,i],[crvs[l],s,j],[crvs[l],s,k]]).fly for l in np.arange(len(crvs))] )
        
    fwds = flat_lst( [ (x2[i][0], [100*(x2[i][0]-x2[i][j]) for j in np.arange(1,len(crvs))]) for i in np.arange(len(x2))] )
    curve = flat_lst( [ (x3[i][0], [1*(x3[i][0]-x3[i][j])   for j in np.arange(1,len(crvs))], [x3[ i+(len(curve_rates)*k)  ][0] for k in np.arange(1,len(shift))]) for i in np.arange(len(curve_rates))] )
    fly = flat_lst( [ (x4[i][0], [1*(x4[i][0]-x4[i][j])   for j in np.arange(1,len(crvs))], [x4[ i+(len(fly_rates)*k)  ][0] for k in np.arange(1,len(shift))]) for i in np.arange(len(fly_rates))] )
    


    class swap_table2_output():
        def __init__(self):
            self.fra = fra
            self.par = par
            self.fwds = fwds
            self.curve = curve
            self.fly = fly
    
    return swap_table2_output()


def swap_table3(crvs, outright_rates, fwd_rates, curve_rates, fly_rates, shift=[0, '1M', '3M', '6M', 1], price_nodes=1):
#    crvs = [ois_dc_build('SOFR_DC',b=0), s2[-1]]
#    shift = [0,'1M','3M','6M',1]
#    outright_rates = [1,2,3,4,5,6,7,8,9,10,12,15,20,25,30,40,50]
#    fwd_rates = [(1,1), (2,1), (3,1), (4,1), (2,2), (3,2), (5,5), (10,5), (10,10), (15,15) ]
#    curve_rates = [(2,3), (2,5), (2,10), (5,10), (5,30), (10,30)]
#    fly_rates = [(2,3,5), (2,5,10), (3,5,7), (5,10,30)]

    TU_Dict = {'D': 0, 'W': 1, 'M': 2, 'Y': 3}

    try:
        c = ccy(crvs[0].ois_index,
                ql.Date(datetime.datetime.now().day, datetime.datetime.now().month, datetime.datetime.now().year))
    except:
        c = ccy(crvs[0].index,
                ql.Date(datetime.datetime.now().day, datetime.datetime.now().month, datetime.datetime.now().year))

    if c.fixing_tenor < ql.Period("6m"):
        fra_step = '3m'
    else:
        fra_step = '3m'
    if price_nodes == 1:
        x1 = []
        for i in np.arange(len(outright_rates)):
            x1.append([quick_swap([[crvs[j], 0, outright_rates[i]]])[0] for j in np.arange(len(crvs))])

        x_fra = FUT_CT_Q(crvs[0].ref_date)[:13]
        x5 = []
        for i in x_fra['Date']:
            x5.append([Swap_Pricer(
                [[crvs[j], str(i.dayOfMonth()) + '-' + str(i.month()) + '-' + str(i.year()), fra_step]]).rate[0] for j
                       in np.arange(len(crvs))])

        fra = flat_lst(
            [(x5[i][0], [100 * (x5[i][0] - x5[i][j]) for j in np.arange(1, len(crvs))]) for i in np.arange(len(x5))])
        par = flat_lst(
            [(x1[i][0], [100 * (x1[i][0] - x1[i][j]) for j in np.arange(1, len(crvs))]) for i in np.arange(len(x1))])
    else:
        fra = []
        par = []

    x2 = []
    for i, j in fwd_rates:
        x2.append([quick_swap([[crvs[k], i, j]])[0] for k in np.arange(len(crvs))])

    x3 = []
    x4 = []
    shift2 = []
    for k in np.arange(len(shift)):
        if isinstance(shift[k], int) == True:
            shift2.append((shift[k], ql.Years))
        else:
            shift2.append(( int(shift[k][:-1]), TU_Dict[shift[k][-1]]))

    for m1, m2 in shift2:
        for i, j in curve_rates:
            x3.append([quick_swap([[crvs[l], m1, i], [crvs[l], m1, j]], u1=m2, spread =1)[0] for l in np.arange(len(crvs))])
        for i, j, k in fly_rates:
            x4.append(
                [quick_swap([[crvs[l], m1, i], [crvs[l], m1, j], [crvs[l], m1, k]], u1=m2, fly = 1)[0] for l in np.arange(len(crvs))])

    fwds = flat_lst(
        [(x2[i][0], [100 * (x2[i][0] - x2[i][j]) for j in np.arange(1, len(crvs))]) for i in np.arange(len(x2))])
    curve = flat_lst([(x3[i][0], [1 * (x3[i][0] - x3[i][j]) for j in np.arange(1, len(crvs))],
                       [x3[i + (len(curve_rates) * k)][0] for k in np.arange(1, len(shift))]) for i in
                      np.arange(len(curve_rates))])
    fly = flat_lst([(x4[i][0], [1 * (x4[i][0] - x4[i][j]) for j in np.arange(1, len(crvs))],
                     [x4[i + (len(fly_rates) * k)][0] for k in np.arange(1, len(shift))]) for i in
                    np.arange(len(fly_rates))])

    class swap_table3_output():
        def __init__(self):
            self.fra = fra
            self.par = par
            self.fwds = fwds
            self.curve = curve
            self.fly = fly

    return swap_table3_output()




