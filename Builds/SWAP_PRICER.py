############### Swap Price module
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
from Utilities import *
from OIS_DC_BUILD import ois_dc_build


def Swap_Pricer(a, fixed_leg_freq = 0):
    output_name = []
    output_rate = []
    output_dv01 = []
    output_01 = []
    output_npv = 0.0
    output_table = pd.DataFrame()
    output_start_date = []
    output_end_date = []

#    a = [[s2[-1],2,2]]
#    a = [[usd3m,0,2],[usd3m,0,3]]
#    a = [[sonia,0,10]]

    for k in range(len(a)):
        ql.Settings.instance().evaluationDate = a[k][0].trade_date
        
        n = 10000000.0
        x = 2.0
        #k=0        
        if len(a[k]) > 3:
            if a[k][3] == '':
                n = 1000000.0
            else:
                    n = a[k][3]
#                except:
#                    n = 10000000.0
        
        if len(a[k]) > 4:
            try:
                x = a[k][4]
            except:
                x = 2.0
                
        if a[k][0].ois_trigger == 0:
            custom_sw_class_index = a[k][0].index
        else:
            custom_sw_class_index = a[k][0].ois_index
        
        
        sw = swap_class(custom_sw_class_index,a[k][1],a[k][2],n,x)
        today = ql.Date(datetime.datetime.now().day,datetime.datetime.now().month,datetime.datetime.now().year)

        t = ccy(sw.index, today)
        if a[k][0].ois_trigger == 0:
            curve = a[k][0].curve[0]
            curve.enableExtrapolation()
            dc = a[k][0].curve[1]
        else:
            curve = a[k][0].curve
            curve.enableExtrapolation()
            dc = a[k][0].curve
        
        output_name.append(str(a[k][1])+" x "+str(a[k][2]))
### dates handling
        #st = str('6-11-2018')
        #int(st.split('-')[0])
        #st = '1M'
        #st = 3

        if isinstance(sw.st,str) == True:
            try:
                start = ql.Date(int(sw.st.split('-')[0]),int(sw.st.split('-')[1]),int(sw.st.split('-')[2]))
            except:
                if sw.st[-1] in ('D','d'):
                    unit = ql.Days
                elif sw.st[-1] in ('W','w'):
                    unit = ql.Weeks
                elif sw.st[-1] in ('M','m'):
                    unit = ql.Months
                elif sw.st[-1] in ('Y','y'):
                    unit = ql.Years
                start = t.cal.advance(curve.referenceDate(),int(sw.st[0:-1]),unit)

        else:
            start = t.cal.advance(curve.referenceDate(),sw.st,ql.Years)
        
        output_start_date.append(start)
        
        if isinstance(sw.mt,str) == True:
            try:
                end = ql.Date(int(sw.mt.split('-')[0]),int(sw.mt.split('-')[1]),int(sw.mt.split('-')[2]))
            except:
                end = start + ql.Period(sw.mt)

        else:
            end = t.cal.advance(start,sw.mt,ql.Years)
            
        output_end_date.append(end)


#calculating swap rate
        if fixed_leg_freq == 0:
            fix_freq = t.fixed[0]
        else:
            fix_freq = fixed_leg_freq

        fixed_schedule = ql.Schedule(start, end, fix_freq, t.cal, ql.ModifiedFollowing, ql.ModifiedFollowing, ql.DateGeneration.Forward, False)
        floating_schedule = ql.Schedule(start, end, t.floating[0], t.cal, ql.ModifiedFollowing, ql.ModifiedFollowing, ql.DateGeneration.Forward, False)
        
        discount_curve = ql.RelinkableYieldTermStructureHandle(dc)
        c_handle = ql.RelinkableYieldTermStructureHandle(curve)
        
        if (t.index_custom == 0) and (a[k][0].ois_trigger == 0):
            index = t.index(t.fixing_tenor,c_handle)
        else: 
            index =  ql.IborIndex(t.fixing, t.fixing_tenor, t.sett_d, t.curncy, t.cal, ql.ModifiedFollowing, True, t.floating[1], c_handle)

        swap = ql.VanillaSwap(ql.VanillaSwap.Payer, sw.n,fixed_schedule,sw.rate_x/100, t.fixed[1],floating_schedule, index,0.0, t.floating[1])
        swap.setPricingEngine(ql.DiscountingSwapEngine(discount_curve))
        output_rate.append(round(swap.fairRate()*100,7))


#calc pv01
        bp = -0.00005
        base_curve = ql.YieldTermStructureHandle(curve)
        spread = ql.SimpleQuote(1*bp)
        c_handle.linkTo(ql.ZeroSpreadedTermStructure(base_curve, ql.QuoteHandle(spread)))
        a1 = swap.fairRate()*100
        a2 = swap.NPV()

        bp = 0.00005
        base_curve = ql.YieldTermStructureHandle(curve)
        spread = ql.SimpleQuote(1*bp)
        c_handle.linkTo(ql.ZeroSpreadedTermStructure(base_curve, ql.QuoteHandle(spread)))
        b1 = swap.fairRate()*100
        b2 = swap.NPV()
        
        ind_01 = round((a2-b2)/ ((a1-b1)*sw.n/100),2)
        output_dv01.append(ind_01)
        
#pv output
        c_handle.linkTo(curve)
        output_npv = output_npv + swap.NPV()
        output_01.append(round(ind_01 * sw.n / 10000,0))
 
    output_dates = pd.DataFrame()
    output_dates['Start'] = pd.Series(output_start_date)
    output_dates['End'] = pd.Series(output_end_date)
    output_dates.index = output_name
###### output_class:
        
    class swap_pricer_output(): 
       
        def __init__(self):
            self.name = output_name
            self.dates = output_dates
            self.rate = output_rate
            self.dv01 = output_dv01
            self.risk = output_01
            self.npv = round(output_npv,0)
            if len(output_rate) == 2:
                self.spread = round(100*(self.rate[1] - self.rate[0]),1)
            if len(output_rate) == 3:
                self.fly = round(100*(2*self.rate[1] - (self.rate[0] + self.rate[2])),1)
        
            output_table['Rate'] = self.rate
            output_table['dv01'] = self.dv01
            output_table['risk'] = self.risk
            output_table['Spread'] = output_table['Rate'].diff()*100
            output_table['Fly'] = output_table['Spread'].diff()*-1
            output_table.index = output_name
            
            self.table = output_table.fillna("")
            
            
    return swap_pricer_output()




def Swap_curve_fwd(crv, inst, ratio, end_fwd_start = 10, interval = 1, fixed_leg_freq = 0):
    
#    crv = sofr
#    inst = [[2],[5],[10]]
#    ratio = [1,-2,1]
#    end_fwd_start = 10
#    interval = 0.5
    output_rate =  dict([(key, []) for key in np.arange(len(ratio))])
    
    r1 = np.arange(0, end_fwd_start+1, interval)
    today = ql.Date(datetime.datetime.now().day,datetime.datetime.now().month,datetime.datetime.now().year)
    
    if crv.ois_trigger == 0:
        custom_sw_class_index = crv.index
    else:
        custom_sw_class_index = crv.ois_index
    
    for k in range(len(inst)):
#        k = 0
        if len(inst[0]) == 1:
            sw = swap_class(custom_sw_class_index,  0,  inst[k][0], 10000000.0,2.0)
        else:
            sw = swap_class(custom_sw_class_index,  inst[k][0],  inst[k][1], 10000000.0,2.0)
            
        t = ccy(sw.index, today)
        if crv.ois_trigger == 0:
            curve = crv.curve[0]
            curve.enableExtrapolation()
            dc = crv.curve[1]
        else:
            curve = crv.curve
            curve.enableExtrapolation()
            dc = crv.curve
            
        ### dates handling
        if isinstance(sw.st,str) == True:
            try:
                start = ql.Date(int(sw.st.split('-')[0]),int(sw.st.split('-')[1]),int(sw.st.split('-')[2]))
            except:
                if sw.st[-1] in ('D','d'):
                    unit = ql.Days
                elif sw.st[-1] in ('W','w'):
                    unit = ql.Weeks
                elif sw.st[-1] in ('M','m'):
                    unit = ql.Months
                elif sw.st[-1] in ('Y','y'):
                    unit = ql.Years
                start = t.cal.advance(curve.referenceDate(),int(sw.st[0:-1]),unit)

        else:
            start = t.cal.advance(curve.referenceDate(),sw.st,ql.Years)
        
        if interval >=1:
            start_d = [t.cal.advance(start,int(i),ql.Years) for i in r1]
        else:
            start_d = [t.cal.advance(start,int(i*12),ql.Months) for i in r1]

        end_d = [t.cal.advance(i,sw.mt,ql.Years) for i in start_d]
        
        
        #calculating swap rate
        if fixed_leg_freq == 0:
            fix_freq = t.fixed[0]
        else:
            fix_freq = fixed_leg_freq
        
        discount_curve = ql.RelinkableYieldTermStructureHandle(dc)
        c_handle = ql.RelinkableYieldTermStructureHandle(curve)
        
        if (t.index_custom == 0) and (crv.ois_trigger == 0):
            index = t.index(t.fixing_tenor,c_handle)
        else: 
            index =  ql.IborIndex(t.fixing, t.fixing_tenor, t.sett_d, t.curncy, t.cal, ql.ModifiedFollowing, True, t.floating[1], c_handle)
            
        for i in np.arange(len(r1)):
            fixed_schedule = ql.Schedule(start_d[i], end_d[i], fix_freq, t.cal, ql.ModifiedFollowing, ql.ModifiedFollowing, ql.DateGeneration.Forward, False)
            floating_schedule = ql.Schedule(start_d[i], end_d[i], t.floating[0], t.cal, ql.ModifiedFollowing, ql.ModifiedFollowing, ql.DateGeneration.Forward, False)
        
            swap = ql.VanillaSwap(ql.VanillaSwap.Payer, sw.n,fixed_schedule,sw.rate_x/100, t.fixed[1],floating_schedule, index,0.0, t.floating[1])
            swap.setPricingEngine(ql.DiscountingSwapEngine(discount_curve))
        
            output_rate[k].append(round(swap.fairRate()*100,7))
        

    curve_fwds_output = np.array([-100*np.sum([ output_rate[i][j]*ratio[i] for i in np.arange(len(ratio)) ]) for j in np.arange(len(r1)) ])
    curve_fwds_carry = -1*np.diff(curve_fwds_output)
    
    class swap_curve_fwd_output(): 
       
        def __init__(self):
            self.rate = curve_fwds_output
            self.carry = curve_fwds_carry
            
    return swap_curve_fwd_output()


    

def quick_swap(a, u1=ql.Years, u2=ql.Years, spread =0, fly = 0):
    ''' Quick Swap only works when actual dates do not need to be specified. settlement_days not specified currently '''
    output_rate=[]
    for k in np.arange(len(a)):
        ql.Settings.instance().evaluationDate = a[k][0].trade_date
        termStructure = ql.YieldTermStructureHandle(a[k][0].curve)
        index = a[k][0].index(termStructure)
        engine = ql.DiscountingSwapEngine(termStructure)
        start = ql.Period(a[k][1], u1)
        swapTenor = ql.Period(a[k][2], u2)
        swap = ql.MakeVanillaSwap(swapTenor, index, 0.0, start, pricingEngine=engine, settlementDays=2)
        output_rate.append(100*swap.fairRate())

    if spread == 1:
        output_rate = [100*(output_rate[1]-output_rate[0])]
    if fly == 1:
        output_rate = [np.round(np.dot(np.array(output_rate), np.array([-100, 200, -100])), 3)]
    return output_rate






