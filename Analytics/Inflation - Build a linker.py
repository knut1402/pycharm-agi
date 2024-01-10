import QuantLib
import numpy as np
import pandas as pd

calendar = ql.UnitedKingdom()
dayCounter = ql.ActualActual(ql.ActualActual.ISDA)
convention = ql.ModifiedFollowing
lag = 3

today = ql.Date(datetime.datetime.now().day,datetime.datetime.now().month,datetime.datetime.now().year)
evaluationDate = calendar.adjust(today)
issue_date = ql.Date(1,1,2024)
maturity_date = ql.Date(22,3,2052)
baseCPI = 242.05
fixing_date = calendar.advance(evaluationDate,-lag, ql.Months)

ql.Settings.instance().setEvaluationDate(evaluationDate)
yTS = ql.YieldTermStructureHandle(ql.FlatForward(evaluationDate, 0.05, dayCounter))

tenor = ql.Period(1, ql.Months)

c = ccy_infl('UKRPI',today)
c.fixing_hist

from_date = c.fixing_hist['months'][0];
to_date   = c.fixing_hist['months'][-1:].tolist()[0];
rpiSchedule = ql.Schedule(from_date, to_date, tenor, calendar,
                               convention, convention,
                               ql.DateGeneration.Backward, False)

# this is the going to be holder the inflation curve.
cpiTS = ql.RelinkableZeroInflationTermStructureHandle()
inflationIndex = ql.UKRPI(False, cpiTS)
fixData = c.fixing_hist['index'].tolist()

dte_fixings=[dtes for dtes in rpiSchedule]
#len(fixData)
#len(dte_fixings[:len(fixData)])
#must be the same length
inflationIndex.addFixings(dte_fixings[:len(fixData)], fixData)
#Current CPI level
#last observed rate
#fixing_rate = 214.4
#inflationIndex.addFixing(fixing_date, fixing_rate)


observationLag = ql.Period(2, ql.Months)
zciisData =[( ql.Date(1, ql.January, 2025), 3.92 ),
              ( ql.Date(1, ql.January, 2026), 3.775 ),
              ( ql.Date(1, ql.January, 2027), 3.7605 ),
              ( ql.Date(1, ql.January, 2028), 3.7655 ),
              ( ql.Date(1, ql.January, 2029), 3.7855 ),
              ( ql.Date(1, ql.January, 2030), 3.795 ),
              ( ql.Date(1, ql.January, 2031), 3.74 ),
              ( ql.Date(1, ql.January, 2032), 3.68 ),
              ( ql.Date(1, ql.January, 2033), 3.62 ),
              ( ql.Date(1, ql.January, 2034), 3.575 ),
              ( ql.Date(1, ql.January, 2036), 3.51 ),
              ( ql.Date(1, ql.January, 2039), 3.44 ),
              ( ql.Date(1, ql.January, 2044), 3.36 ),
              ( ql.Date(1, ql.January, 2049), 3.26 ),
              ( ql.Date(1, ql.January, 2054), 3.19 ),
              ( ql.Date(1, ql.January, 2064), 3.07 ),
              ( ql.Date(1, ql.January, 2074), 3.045 )]

#lRates=[rtes/100.0 for rtes in zip(*zciisData)[1]]
#baseZeroRate = lRates[0]

zeroSwapHelpers = [ql.ZeroCouponInflationSwapHelper(  ql.QuoteHandle(ql.SimpleQuote(rate/100)) ,observationLag,
                                                      date, calendar, convention, dayCounter, inflationIndex,  ql.CPI.Flat, yTS) for date,rate in zciisData]

# the derived inflation curve
jj=ql.PiecewiseZeroInflation(evaluationDate, calendar, dayCounter, observationLag, inflationIndex.frequency(), inflationIndex.interpolated(),
                             3.92/100, zeroSwapHelpers, 1.0e-12, ql.Linear())

cpiTS.linkTo(jj)
################################ Testing fwds and zeroes ##################
notional = 1e6
startDate = ql.Date(15, 10, 2024)
endDate = ql.Date(15, 10, 2028)
fixedRate = 0.0392
swapType = ql.ZeroCouponInflationSwap.Payer
swap = ql.ZeroCouponInflationSwap(swapType, notional, startDate, endDate, calendar, convention, dayCounter, fixedRate, inflationIndex, observationLag,
                                  ql.CPI.Flat, inflationIndex.interpolated(), )

swapEngine = ql.DiscountingSwapEngine(yTS)
swap.setPricingEngine(swapEngine)
npv = swap.NPV()
100*swap.fairRate()

c.fixing_hist[-20:]


notional = 1000000
fixedRates = [0.25/100]

fixedDayCounter = ql.Actual365Fixed()
fixedPaymentConvention = ql.ModifiedFollowing
fixedPaymentCalendar = ql.UnitedKingdom()
contractObservationLag = ql.Period(3, ql.Months)
observationInterpolation = ql.CPI.Linear
settlementDays = 3
growthOnly = False


fixedSchedule = ql.Schedule(issue_date,
                  maturity_date,
                  ql.Period(ql.Semiannual),
                  fixedPaymentCalendar,
                  ql.Unadjusted,
                  ql.Unadjusted,
                  ql.DateGeneration.Backward,
                  False)

bond = ql.CPIBond(settlementDays,
                    notional,
                    growthOnly,
                    baseCPI,
                    contractObservationLag,
                    inflationIndex,
                    observationInterpolation,
                    fixedSchedule,
                    fixedRates,
                    fixedDayCounter,
                    fixedPaymentConvention)


for cf in bond.cashflows():
    print(cf.date().ISO(), cf.amount())


bondEngine=ql.DiscountingBondEngine(yTS)
bond.setPricingEngine(bondEngine)
bond.NPV()
bond.cleanPrice()
compounding = ql.Compounded
yield_rate = bond.bondYield(fixedDayCounter,compounding,ql.Semiannual)
y_curve = ql.InterestRate(yield_rate,fixedDayCounter,compounding,ql.Semiannual)
##Collate results
print "Clean Price:", bond.cleanPrice()
print "Dirty Price:", bond.dirtyPrice()
print "Notional:", bond.notional()
print "Yield:", yield_rate
print "Accrued Amount:", bond.accruedAmount()
print "Settlement Value:", bond.settlementValue()

#suspect there's more to this for TIPS
print "Duration:", ql.BondFunctions.duration(bond,y_curve)
print "Convexity:", ql.BondFunctions.convexity(bond,y_curve)
print "Bps:", ql.BondFunctions.bps(bond,y_curve)
print "Basis Point Value:", ql.BondFunctions.basisPointValue(bond,y_curve)
print "Yield Value Basis Point:", ql.BondFunctions.yieldValueBasisPoint(bond,y_curve)

print "NPV:", bond.NPV()

# get the cash flows:
#cf_list=[(cf.amount(),cf.date()) for cf in bond.cashflows()]

def to_datetime(d):
    return dt.datetime(d.year(),d.month(), d.dayOfMonth())

for cf in bond.cashflows():
    try:
        amt=cf.amount()
        rte=jj.zeroRate(cf.date())
        zc=yTS.zeroRate(cf.date(),fixedDayCounter,compounding,ql.Semiannual).rate()
    except:
        amt=0
        rte=0
        zc=0
    print to_datetime(cf.date()),amt,rte,zc



#########################################################################################
############# build a linker from scratch

### set up
today = ql.Date(datetime.datetime.now().day, datetime.datetime.now().month, datetime.datetime.now().year)
c = ccy('SONIA_DC', today)

#### get inflation curve
rpi = infl_zc_swap_build('UKRPI', b=-1)
rpi.fixing_hist

### get sonia curve
sonia_live = ois_dc_build('SONIA_DC',b=0)
sonia_cls = ois_dc_build('SONIA_DC',b=-1)

### bond details  == ukti nov 2032

cpn = 1.25
cpn_f = 2
iss_dt = ql.Date(29,10,2008)
mat = ql.Date(22,11,2032)
lag = 3

### handle for getting inflation index
def get_inflation_index(fix_hist, cal1, d):
#    d = ql.Date(10,1,2024)
#    fix_hist = rpi.curve[1]
#    cal1 = c.cal

    d1 = d.dayOfMonth()
    d2 = ql.Date.endOfMonth(d).dayOfMonth()

    m3 = cal1.advance(d,-3,ql.Months)- cal1.advance(d,-3,ql.Months).dayOfMonth() + 1
    m2 = cal1.advance(d,-2,ql.Months)- cal1.advance(d,-2,ql.Months).dayOfMonth() + 1

    i3 = fix_hist[fix_hist['months'] == m3]['index'].tolist()[0]
    i2 = fix_hist[fix_hist['months'] == m2]['index'].tolist()[0]

    return np.round(i3+((d1-1)*(i2-i3)/d2),6)

### handle for bond coupon schedule
def bond_schedule(mat_dt, cpn_freq, fwd = 0):
    cpn_sch = []
    today = ql.Date(datetime.datetime.now().day, datetime.datetime.now().month, datetime.datetime.now().year)

    if fwd == 0:
        start_dt = today
    else: start_dt = fwd


    if cpn_freq == 2:
        t1 = 6
    elif cpn_freq == 1:
        t1 = 12

    d1 = mat_dt
    while d1 > start_dt:
        cpn_sch.append(d1)
        d1 = d1-ql.Period(t1,ql.Months)

    cpn_sch = cpn_sch[::-1] + [mat_dt]   #### adding extra date for principal repay
    return cpn_sch

### get cashflows

def linker_cashflow(infc, oisc, mat_dt, cpn, cpn_freq, cal2, iss_dt):
    today = ql.Date(datetime.datetime.now().day, datetime.datetime.now().month, datetime.datetime.now().year)

    cs1 = bond_schedule(mat_dt, cpn_freq)
    base_index = get_inflation_index(infc.curve[1], cal2, iss_dt)

    cf1 = np.array([np.round(get_inflation_index(infc.curve[1], cal2, cs1[i]) / base_index,5) for i in np.arange(len(cs1))])
    cs2 = [cs1[0]-ql.Period(int(12/cpn_freq),ql.Months)]+cs1[:-1]   #### need to change today to settle date
    cf2 = np.array(list(np.array([cs2[i+1] - cs2[i] for i in np.arange(len(cs2)-1)])*cpn/365)+[100])
    cf3 = np.multiply(cf1, cf2)
    discf1 = [oisc.discount(cs1[i]) for i in np.arange(len(cs1))]

    out_cf = pd.DataFrame()
    out_cf['date'] = cs1
    out_cf['ind_ratio'] = cf1
    out_cf['coupon_dc'] = cf2
    out_cf['cf'] = cf3
    out_cf['dcf'] = np.multiply(cf3, discf1)

    class linker_cashflow_output():

        def __init__(self):
            self.tab = out_cf
            self.pv = np.sum(out_cf['dcf'])
            self.base_index = base_index

    return linker_cashflow_output()

def z_sprd_linker(infc, oisc, mat_dt, cpn, cpn_freq, cal2, iss_dt, dp):
    def optimizer_func(x: float):
        return linker_cashflow(rpi, ql.ZeroSpreadedTermStructure(ql.YieldTermStructureHandle(oisc),ql.QuoteHandle(ql.SimpleQuote(x/10000))),
                               mat_dt, cpn, cpn_freq, cal2, iss_dt).pv - dp

    Optm = ql.Brent()
    return    Optm.solve(optimizer_func, 0.00001, 50, 0.1)


z_sprd_linker(rpi, sonia_cls.curve, ql.Date(22,11,2047), 0.75, 2, c.cal, ql.Date(22,11,2007), 165.78)
z_sprd_linker(rpi, sonia_cls.curve, ql.Date(22,11,2032), 1.25, 2, c.cal, ql.Date(29,10,2008), 188.98)



def bond_cashflow(oisc, mat_dt, cpn, cpn_freq):
    today = ql.Date(datetime.datetime.now().day, datetime.datetime.now().month, datetime.datetime.now().year)

    cs1 = bond_schedule(mat_dt, cpn_freq)
    cs2 = [cs1[0]-ql.Period(int(12/cpn_freq),ql.Months)]+cs1[:-1]
    cf2 = np.array(list(np.array([cs2[i+1] - cs2[i] for i in np.arange(len(cs2)-1)])*cpn/365)+[100])
    discf1 = [oisc.discount(cs1[i]) for i in np.arange(len(cs1))]

    out_cf = pd.DataFrame()
    out_cf['date'] = cs1
    out_cf['coupon_dc'] = cf2
    out_cf['dcf'] = np.multiply(cf2, discf1)

    class bond_cashflow_output():

        def __init__(self):
            self.tab = out_cf
            self.pv = np.sum(out_cf['dcf'])

    return bond_cashflow_output()

ester_cls = ois_dc_build('ESTER_DC',b=-1)
bcf = bond_cashflow(ester_cls.curve, ql.Date(25,4,2055), 4.0, 1)

bcf.tab
bcf.pv

(137.85-118.76)/.22


def z_sprd_nom(oisc, mat_dt, cpn, cpn_freq, dp):
    def optimizer_func(x: float):
        return bond_cashflow(ql.ZeroSpreadedTermStructure(ql.YieldTermStructureHandle(oisc),ql.QuoteHandle(ql.SimpleQuote(x/10000))),
                             mat_dt, cpn, cpn_freq).pv - dp

    Optm = ql.Brent()
    return    Optm.solve(optimizer_func, 0.00001, 50, 0.1)

z_sprd_nom(ester_cls.curve, ql.Date(25,4,2055), 4, 1, 118.75)





################# yield yield spread
########## invoice spread
bond_schedule(ql.Date(15,2,2033), 1, fwd = ql.Date(11,3,2024))
ester_live = ois_dc_build('ESTER_DC',b=0)

Swap_Pricer([[ester_live,'11-03-2024','15-08-2048']], fixed_leg_freq = 0).rate
Swap_Pricer([[ester_live,'11-03-2024','15-02-2033']], fixed_leg_freq = 0).rate
Swap_Pricer([[ester_live,'11-03-2024','12-12-2025']], fixed_leg_freq = 0).rate


####  par-par spread
def bond_par_par(oisc, mat_dt, cpn, cpn_freq, px):
    oisc = ester_cls
    mat_dt = ql.Date(25,5,2040)
    cpn = 0.5
    cpn_freq = 1

    today = ql.Date(datetime.datetime.now().day, datetime.datetime.now().month, datetime.datetime.now().year)
    sw = Swap_Pricer([[oisc, 0, '25-05-2040']], fixed_leg_freq=0)

    bcs1 = bond_schedule(mat_dt, cpn_freq)
    bcs2 = [bcs1[0]-ql.Period(int(12/cpn_freq),ql.Months)]+bcs1[:-1]
    cf2 = np.array(list(np.array([bcs2[i+1] - bcs2[i] for i in np.arange(len(bcs2)-1)])*((cpn)/365)))
    discf1 = [oisc.curve.discount(bcs1[i]) for i in np.arange(len(bcs1)-1)]

    scs2 = [today+2] + bcs1[:-1]
    cf3 = np.array(list(np.array([scs2[i + 1] - scs2[i] for i in np.arange(len(scs2)-1)]) * ((sw.rate[0]) / 365)))
    discf2 = [oisc.curve.discount(bcs1[i]) for i in np.arange(len(bcs1)-1)]

    np.sum(np.multiply(np.array(list(np.array([scs2[i + 1] - scs2[i] for i in np.arange(len(scs2)-1)]) / 365)),discf2))
    sw.dv01
    sum(discf1)

    out_cf = pd.DataFrame()
    out_cf['date'] = bcs1[:-1]
    out_cf['bond_coupon_dc'] = cf2
    out_cf['bond_dcf'] = np.multiply(cf2, discf1)
    out_cf['sw_coupon_dc'] = cf3
    out_cf['sw_dcf'] = np.multiply(cf3, discf2)

    (100-68.279+(np.sum(out_cf['bond_dcf'])/100)-(np.sum(out_cf['sw_dcf'])/100)) / 13


    class bond_cashflow_output():

        def __init__(self):
            self.tab = out_cf
            self.pv = np.sum(out_cf['dcf'])

    return bond_cashflow_output()

len(cf2)

bond_cashflow(ester_cls.curve, ql.Date(25,4,2055), 1, 1).pv



(-118.76+100+(np.sum(out_cf['dcf'])/100))/risk01


oisc.curve.discount(scs2[0]+1)

len(cf3)
len(discf2)
len(scs2)

len(bcs2)
len(cf2)
len(discf1)


(100-68.28)


