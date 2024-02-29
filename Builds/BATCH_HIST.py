##### batch ois
import QuantLib as ql
import datetime
import pandas as pd

from Utilities import *
from OIS_DC_BUILD import ois_dc_build, get_wirp, get_wirp_hist, ois_from_nodes
from Conventions import FUT_CT,FUT_CT_Q, ccy, ccy_infl, hist

#### ois hist
df_crv = pd.read_csv("./DataLake/query-usd-ois.csv")
df_crv = pd.read_csv("./DataLake/query-gbp-sonia.csv")
df_crv = pd.read_csv("./DataLake/query-eur-ester.csv")
df_crv = df_crv[-100:]
df_crv.reset_index(inplace=True, drop=True)
a = 'SOFR_DC'
out_pickle = 'SOFR_H'

batch_ois(df_crv, a, out_pickle)


def batch_ois(df_crv, a, out_pickle = 'test_', write = 0):
    today = ql.Date(datetime.datetime.now().day, datetime.datetime.now().month, datetime.datetime.now().year)
    c = ccy(a, today)
    TU_Dict = {'D': 0, 'W': 1, 'M': 2, 'Y': 3}

    ois_db = pd.DataFrame()
    ois_db.index = df_crv['Date']

    r_index = []
    r_ref_date = []
    r_dates = []
    r_rates = []
    r_fixing = []
    r_tab = []
    r_fwdtab = []
    r_swap_rates = []
    fwd_terms = [('1m', '3m'), ('2m', '3m'), ('3m', '3m'), ('6m', '3m'), ('9m', '3m'), ('12m', '3m'), ('15m', '3m'),('18m', '3m'), ('21m', '3m'),
                 ('1y', '1y'), ('2y', '1y'), ('3y', '1y'), ('4y', '1y'), ('5y', '1y'), ('6y', '1y'), ('7y', '1y'), ('8y', '1y'), ('9y', '1y'), ('10y', '1y'),
                 ('11y', '1y'), ('12y', '1y'), ('13y', '1y'), ('14y', '1y'), ('15y', '1y'), ('16y', '1y'), ('17y', '1y'), ('18y', '1y'), ('19y', '1y'), ('20y', '1y'),
                 ('21y', '1y'), ('22y', '1y'), ('23y', '1y'), ('24y', '1y'), ('25y', '1y'), ('26y', '1y'), ('27y', '1y'), ('28y', '1y'), ('29y', '1y')]

#    i=0
    for i in np.arange(len(df_crv)):
        b= df_crv['Date'][i]
        print(b)
        ref_date = ql.Date(int(b.split('/')[0]), int(b.split('/')[1]), int(b.split('/')[2]))
        ref_date_1 = c.cal.advance(ref_date, -1, ql.Days)
        ql.Settings.instance().evaluationDate = ref_date

    #### get o/n ois fixing
        OIS_ON = df_crv['1d'][i]
        deposits = {(0, 1, ql.Days): OIS_ON}
        for sett_num, n, unit in deposits.keys():
            deposits[(sett_num, n, unit)] = ql.SimpleQuote(
                deposits[(sett_num, n, unit)] / 100.0)

        helpers = [ ql.DepositRateHelper(
            ql.QuoteHandle(deposits[(sett_num, n, unit)]),
            ql.Period(n, unit),
            c.sett_d,                 ##### using 2 for SOFR_DC, 0 for SONIA_DC
            c.cal,
            ql.Following,
            False,
            c.floating[1],
                )
                for sett_num, n, unit in deposits.keys()]

        OIS_DC = c.index_a

    #### get ois swap rates
        x1 = pd.DataFrame()
        x1['Tenor'] = [df_crv.columns[k].upper() for k in np.arange(2,len(df_crv.columns))]
        x1['Rate'] = [df_crv.iloc[i,j] for j in np.arange(2,len(df_crv.columns))]
        x1 = x1.dropna()
        x1 = x1.reset_index(drop=True)

        x1['TenorNum'] = pd.Series([int(x1['Tenor'][i][0:-1]) for i in range(len(x1))])
        x1['TenorUnit'] = pd.Series(dtype=float)
        x1['TenorUnit'] = [TU_Dict[x1['Tenor'].tolist()[i][-1]] for i in range(len(x1))]
        x1['List'] = [(x1['Rate'][i], (int(x1['TenorNum'][i]), int(x1['TenorUnit'][i]))) for i in range(len(x1))]
        L1 = x1['List'].tolist()

        helpers += [ql.OISRateHelper(c.sett_d, ql.Period(*tenor), ql.QuoteHandle(ql.SimpleQuote(rate / 100)), OIS_DC) for rate, tenor in L1]

    ## build curve
        OIS_DC_curve = ql.PiecewiseLogCubicDiscount(c.sett_d, c.cal, helpers, c.floating[1] )
        OIS_DC_curve.enableExtrapolation()

        n1 = OIS_DC_curve.nodes()
        r_index.append(a)
        r_fixing.append(OIS_ON)
        r_ref_date.append(ql_to_datetime(ref_date))
        r_tab.append(x1)
        r_swap_rates.append(x1[x1['TenorUnit']==3][['Tenor','Rate']].reset_index(drop=True))
        r_dates.append([datetime.datetime(n1[j][0].year(), n1[j][0].month(), n1[j][0].dayOfMonth()) for j in range(len(n1))])
        r_rates.append([n1[k][1] for k in range(len(n1))])

    ## calc fwd rates
        fwd_rate = []
        for i in np.arange(len(fwd_terms)):
            start = c.cal.advance(OIS_DC_curve.referenceDate(), ql.Period(fwd_terms[i][0]))
            end = c.cal.advance(start, ql.Period(fwd_terms[i][1]))
            fixed_schedule = ql.Schedule(start, end, c.fixed[0], c.cal, ql.ModifiedFollowing, ql.ModifiedFollowing, ql.DateGeneration.Forward, False)
            floating_schedule = ql.Schedule(start, end, c.floating[0], c.cal, ql.ModifiedFollowing, ql.ModifiedFollowing, ql.DateGeneration.Forward, False)
            c_handle = ql.RelinkableYieldTermStructureHandle(OIS_DC_curve)
            index = ql.IborIndex(c.fixing, c.fixing_tenor, c.sett_d, c.curncy, c.cal, ql.ModifiedFollowing, True, c.floating[1], c_handle)
            swap = ql.VanillaSwap(ql.VanillaSwap.Payer, 100, fixed_schedule, 0.03, c.fixed[1], floating_schedule, index, 0.0, c.floating[1])
            swap.setPricingEngine(ql.DiscountingSwapEngine(c_handle))
            fwd_rate.append(round(swap.fairRate() * 100, 7))
        x2 = pd.DataFrame(fwd_terms)
        x2.columns = ['Fwd_st', 'Tenor']
        x2["Fwd"] = x2['Fwd_st'].astype(str) +'.'+ x2['Tenor'].astype(str)
        x2['Rate'] = fwd_rate
        r_fwdtab.append(x2)

    ois_db['Ref_Date'] = r_ref_date
    ois_db['Dates'] = r_dates
    ois_db['Rates'] = r_rates
    ois_db['Swap_Rates'] = r_swap_rates
    ois_db['Fwd_Rates'] = r_fwdtab
    ois_db['Index'] = r_index
    ois_db['Fixing'] = r_fixing
    ois_db['Table'] = r_tab

    if write == 1:
        ois_db.to_pickle('./DataLake/'+out_pickle+'.pkl')
    return ois_db


def batch_ois_update(dr_crv, a, out_pickle):
#    a = 'SONIA_DC'
#    out_pickle = 'SONIA_H'
    cut_off_date = hist[a].index[-1]
    df_feed = df_crv.iloc[df_crv.index[df_crv['Date'] == cut_off_date].tolist()[0]+1:,:]
    df_feed.reset_index(inplace=True, drop=True)
    df_hist_add = batch_ois(df_feed, a)

    hist[a] = pd.concat([hist[a], df_hist_add])
    hist[a].to_pickle('./DataLake/'+out_pickle+'.pkl')
    return print('hist update: '+str(len(df_feed)))

#batch_ois_update(df_crv, 'SOFR_DC', out_pickle='SOFR_H')


#### libor hist
df_crv2 = pd.read_csv("./DataLake/query-gbp-6m.csv")
df_crv2 = pd.read_csv("./DataLake/query-eur-6m.csv")
df_crv2 = pd.read_csv("./DataLake/query-usd-3m.csv")
#df_crv2 = df_crv2[-10:]
#df_crv2.reset_index(inplace=True, drop=True)
a = 'USD_3M'
out_pickle = 'USD_3M_H'

def batch_libor(df_crv2, a, out_pickle = 'test_', write = 0):

    today = ql.Date(datetime.datetime.now().day, datetime.datetime.now().month, datetime.datetime.now().year)
    c = ccy(a, today)
    TU_Dict = {'D': 0, 'W': 1, 'M': 2, 'Y': 3}

    crv_db = pd.DataFrame()
    crv_db.index = df_crv2['Date']

    r_index = []
    r_ref_date = []
    r_dates = []
    r_rates = []
    r_fwdtab = []
    r_fixing = []
    r_tab = []
    r_swap_rates = []
    fwd_terms = [('1m', '3m'), ('2m', '3m'), ('3m', '3m'), ('6m', '3m'), ('9m', '3m'), ('12m', '3m'), ('15m', '3m'),('18m', '3m'), ('21m', '3m'),
                 ('1y', '1y'), ('2y', '1y'), ('3y', '1y'), ('4y', '1y'), ('5y', '1y'), ('6y', '1y'), ('7y', '1y'), ('8y', '1y'), ('9y', '1y'), ('10y', '1y'),
                 ('11y', '1y'), ('12y', '1y'), ('13y', '1y'), ('14y', '1y'), ('15y', '1y'), ('16y', '1y'), ('17y', '1y'), ('18y', '1y'), ('19y', '1y'), ('20y', '1y'),
                 ('21y', '1y'), ('22y', '1y'), ('23y', '1y'), ('24y', '1y'), ('25y', '1y'), ('26y', '1y'), ('27y', '1y'), ('28y', '1y'), ('29y', '1y')]

    ## dc curve hist
    ois_hist = hist[c.dc_index]

#    i=5200
    fail=[]
    for i in np.arange(len(df_crv2)):
        try:
            b= df_crv2['Date'][i]
            print(i , b)
            ref_date = ql.Date(int(b.split('/')[0]), int(b.split('/')[1]), int(b.split('/')[2]))
            ref_date_1 = c.cal.advance(ref_date, -1, ql.Days)
            ql.Settings.instance().evaluationDate = ref_date

        #### get o/n ois fixing
            OIS_ON = df_crv2['1d'][i]
            deposits = {(0, 1, ql.Days): OIS_ON}
            for sett_num, n, unit in deposits.keys():
                deposits[(sett_num, n, unit)] = ql.SimpleQuote(
                    deposits[(sett_num, n, unit)] / 100.0)

            helpers = [ ql.DepositRateHelper(
                ql.QuoteHandle(deposits[(sett_num, n, unit)]),
                ql.Period(n, unit),
                c.sett_d,                 ##### using 2 for SOFR_DC, 0 for SONIA_DC
                c.cal,
                ql.Following,
                False,
                c.floating[1],
                    )
                    for sett_num, n, unit in deposits.keys()]

        #### get ois swap rates
            x1 = pd.DataFrame()
            x1['Tenor'] = [df_crv2.columns[k].upper() for k in np.arange(2,len(df_crv2.columns))]
            x1['Rate'] = [df_crv2.iloc[i,j] for j in np.arange(2,len(df_crv2.columns))]
            x1 = x1.dropna()
            x1 = x1.reset_index(drop=True)

            x1['TenorNum'] = pd.Series([int(x1['Tenor'][i][0:-1]) for i in range(len(x1))])
            x1['TenorUnit'] = pd.Series(dtype=float)
            x1['TenorUnit'] = [TU_Dict[x1['Tenor'].tolist()[i][-1]] for i in range(len(x1))]
            x1['List'] = [(x1['Rate'][i], (int(x1['TenorNum'][i]), int(x1['TenorUnit'][i]))) for i in range(len(x1))]
            L1 = x1['List'].tolist()

            if ql_to_datetime(ref_date).strftime('%d/%m/%Y') in  ois_hist.index:
                ois_dc = ois_from_nodes(  ois_hist.loc[ql_to_datetime(ref_date).strftime('%d/%m/%Y')] , ccy(c.dc_index, today)).curve
                dc = ql.RelinkableYieldTermStructureHandle(ois_dc)
                helpers += [ql.SwapRateHelper(ql.QuoteHandle(ql.SimpleQuote(rate / 100)), ql.Period(*tenor), c.cal, c.fixed[2], c.fixed[4], c.fixed[3], c.index_a,
                                              ql.QuoteHandle(), ql.Period(0, ql.Days), dc) for rate, tenor in L1]
            else:
    #            index_2 = c.index_a    #### using this for GBP_6M and EUR_6M   and the alternative belwo for USD_3M  ###### needs to be resolved for function!
                index_2 = ql.IborIndex('MyIndex', ql.Period('3m'), 2, ql.USDCurrency(), ql.UnitedStates(ql.UnitedStates.FederalReserve), ql.ModifiedFollowing, True, ql.Actual360())
                helpers += [ql.SwapRateHelper(ql.QuoteHandle(ql.SimpleQuote(rate / 100)), ql.Period(*tenor), c.cal, c.fixed[2], c.fixed[4], c.fixed[3], index_2) for rate, tenor in L1]

        # build curve
            swap_curve = ql.PiecewiseLogCubicDiscount(c.sett_d, c.cal, helpers, c.floating[1] )
            swap_curve.enableExtrapolation()

            n1 = swap_curve.nodes()
            r_index.append(a)
            r_fixing.append(OIS_ON)
            r_ref_date.append(ql_to_datetime(ref_date))
            r_tab.append(x1)
            r_swap_rates.append(x1[x1['TenorUnit']==3][['Tenor','Rate']].reset_index(drop=True))
            r_dates.append([datetime.datetime(n1[j][0].year(), n1[j][0].month(), n1[j][0].dayOfMonth()) for j in range(len(n1))])
            r_rates.append([n1[k][1] for k in range(len(n1))])

        ##### hard code fwd rates
            fwd_rate = []
            for i in np.arange(len(fwd_terms)):
                start = c.cal.advance(swap_curve.referenceDate(), ql.Period(fwd_terms[i][0]))
                end = c.cal.advance(start, ql.Period(fwd_terms[i][1]))
                fixed_schedule = ql.Schedule(start, end, c.fixed[0], c.cal, ql.ModifiedFollowing, ql.ModifiedFollowing, ql.DateGeneration.Forward, False)
                floating_schedule = ql.Schedule(start, end, c.floating[0], c.cal, ql.ModifiedFollowing, ql.ModifiedFollowing, ql.DateGeneration.Forward, False)
                c_handle = ql.RelinkableYieldTermStructureHandle(swap_curve)
                if ql_to_datetime(ref_date).strftime('%d/%m/%Y') in ois_hist.index:
                    discount_curve = dc
                else:
                    discount_curve = c_handle

                if (c.index_custom == 0):  ##### uses index_custom == 1 for USD_3M
                    index = c.index(c.fixing_tenor, c_handle)
                else:
                    index = ql.IborIndex(c.fixing, c.fixing_tenor, c.sett_d, c.curncy, c.cal, ql.ModifiedFollowing, True, c.floating[1], c_handle)

                swap = ql.VanillaSwap(ql.VanillaSwap.Payer, 100, fixed_schedule, 0.03, c.fixed[1], floating_schedule, index, 0.0, c.floating[1])
                swap.setPricingEngine(ql.DiscountingSwapEngine(discount_curve))
                fwd_rate.append(round(swap.fairRate() * 100, 7))
            x2 = pd.DataFrame(fwd_terms)
            x2.columns = ['Fwd_st', 'Tenor']
            x2["Fwd"] = x2['Fwd_st'].astype(str) + '.' + x2['Tenor'].astype(str)
            x2['Rate'] = fwd_rate
            r_fwdtab.append(x2)

        except:
            print('fail', i, b)
            fail.append(b)

    crv_db = pd.DataFrame()
    crv_db.index = [x for x in df_crv2['Date'] if x not in fail]

    crv_db['Ref_Date'] = r_ref_date
    crv_db['Dates'] = r_dates
    crv_db['Rates'] = r_rates
    crv_db['Swap_Rates'] = r_swap_rates
    crv_db['Fwd_Rates'] = r_fwdtab
    crv_db['Index'] = r_index
    crv_db['Fixing'] = r_fixing
    crv_db['Table'] = r_tab

    if write == 1:
        crv_db.to_pickle('./DataLake/'+out_pickle+'.pkl')
    return crv_db



