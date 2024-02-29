# Swap Classes and conventions

## Import Libraries:

import pandas as pd
import numpy as np
import datetime
import os
import pdblp
import runpy
import QuantLib as ql
import matplotlib as mpl
import matplotlib.pyplot as plt

con = pdblp.BCon(debug=False, port=8194, timeout=5000)
con.start()
os.chdir('C:\\Users\A00007579\PycharmProjects\pythonProject')

## Futures Contract Table
def FUT_CT(eval_date):
    today = ql.Date(
        datetime.datetime.now().day,
        datetime.datetime.now().month,
        datetime.datetime.now().year,
    )
    #    eval_date = today
    FUT_CT = {
        "1": "F",
        "2": "G",
        "3": "H",
        "4": "J",
        "5": "K",
        "6": "M",
        "7": "N",
        "8": "Q",
        "9": "U",
        "10": "V",
        "11": "X",
        "12": "Z",
    }

    FUT_M = pd.DataFrame()
    if eval_date.dayOfMonth() > 15:
        a1 = ql.Date.endOfMonth(eval_date) + 15
    else:
        a1 = ql.Date(15, eval_date.month(), eval_date.year())

    s1 = pd.Series([a1 + ql.Period(i, ql.Months) for i in range(3)])
    a2 = s1.tolist()[(3 - a1.month() % 3) % 3]
    #    s2 = s1.append(pd.Series([a2+ql.Period(3*i,ql.Months) for i in range(1,20) ]))
    s2 = pd.concat(
        [s1, pd.Series([a2 + ql.Period(3 * i, ql.Months) for i in range(1, 20)])]
    )
    s3 = (s2 > today) * 1 - 2
    s3.reset_index(drop=True, inplace=True)

    FUT_M["Date"] = pd.Series(s2.tolist())
    FUT_M["TickerMonth"] = pd.Series(
        [
            FUT_CT[str(FUT_M["Date"][i].month())]
            + str(FUT_M["Date"][i].year())[s3[i] :]
            for i in range(len(FUT_M))
        ]
    )

    return FUT_M


def FUT_CT_Q(eval_date):
    today = ql.Date(
        datetime.datetime.now().day,
        datetime.datetime.now().month,
        datetime.datetime.now().year,
    )
    #    eval_date = ql.Date(1,4,2021)

    FUT_CT = {
        "1": "F",
        "2": "G",
        "3": "H",
        "4": "J",
        "5": "K",
        "6": "M",
        "7": "N",
        "8": "Q",
        "9": "U",
        "10": "V",
        "11": "X",
        "12": "Z",
    }

    FUT_M = pd.DataFrame()

    if eval_date.dayOfMonth() > 15:
        a1 = ql.Date.endOfMonth(eval_date) + 15
    else:
        a1 = ql.Date(15, eval_date.month(), eval_date.year())

    s1 = pd.Series([a1 + ql.Period(i, ql.Months) for i in range(3)])
    a2 = s1.tolist()[(3 - a1.month() % 3) % 3]
    s2 = pd.Series([a2 + ql.Period(3 * i, ql.Months) for i in range(0, 20)])
    s3 = (s2 > today) * 1 - 2
    s3.reset_index(drop=True, inplace=True)

    FUT_M["Date"] = pd.Series(s2.tolist())
    # FUT_M['TickerMonth'] = pd.Series([FUT_CT[str(FUT_M['Date'][i].month())]+str(FUT_M['Date'][i].year())[-1:] for i in range(len(FUT_M))])
    FUT_M["TickerMonth"] = pd.Series(
        [
            FUT_CT[str(FUT_M["Date"][i].month())]
            + str(FUT_M["Date"][i].year())[s3[i] :]
            for i in range(len(FUT_M))
        ]
    )

    return FUT_M

## conventions

def ccy(a, eval_date):
    os.chdir('C:\\Users\A00007579\PycharmProjects\pythonProject')
    if a == "USD_3M":
        ois_trigger = 0
        batch_trigger = 1
        curncy = ql.USDCurrency()
        fixing = "US0003M Index"
        fixing_tenor = ql.Period(3, ql.Months)
        bbg_curve = "YCSW0023 INDEX"
        bbgplot_curve_tickers = ['USSW', 'S0025FS', 'EESF']
        start_swap = "2Y"
        add_tenors = pd.DataFrame()
        add_conv_corr = pd.DataFrame()
        FUT_M = FUT_CT(eval_date)
        add_tenors["FRA"] = [
            "ED" + FUT_M["TickerMonth"][i] + " Comdty" for i in range(14)
        ]
        add_conv_corr["CC"] = [
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0.0015,
            0.0025,
            0.004,
            0.005,
            0.007,
            0.01,
        ]
        add_inst = "FUT"
        fut_type = ql.Futures.IMM
        sett_d = 2
        dc_index = "SOFR_DC"
        fixed_leg = ql.Period(6, ql.Months)
        fixed_acc = ql.Thirty360(ql.Thirty360.BondBasis)
        fixed_freq = ql.Semiannual
        fixed_dcc1 = ql.Thirty360(ql.Thirty360.BondBasis)
        fixed_dcc2 = ql.ModifiedFollowing
        floating_leg = ql.Period(3, ql.Months)
        floating_acc = ql.Actual360()
        custom_index_trigger = 1
        index = ql.USDLibor
        index_a = index(ql.Period(3, ql.Months))
        calendar = ql.UnitedStates(ql.UnitedStates.FederalReserve)
    elif a == "USD_6M":
        ois_trigger = 0
        batch_trigger = 1
        fixing = "US0006M Index"
        curncy = ql.USDCurrency()
        fixing_tenor = ql.Period(6, ql.Months)
        bbg_curve = "YCSW0051 INDEX"
        bbgplot_curve_tickers = ['USSW', 'S0051FS', 'EESF']
        start_swap = "2Y"
        add_tenors = pd.DataFrame()
        add_conv_corr = pd.DataFrame()
        add_tenors["FRA"] = [
            "USFR0AG PREB Curncy",
            "USFR0BH PREB Curncy",
            "USFR0CI PREB Curncy",
            "USFR0DJ  PREB Curncy",
            "USFR0EK PREB Curncy",
            "USFR0F1 PREB Curncy",
            "USFR0G1A PREB Curncy",
            "USFR0H1B PREB Curncy",
            "USFR0I1C PREB Curncy",
            "USFR0J1D PREB Curncy",
            "USFR0K1E PREB Curncy",
            "USFR011F PREB Curncy",
        ]
        add_conv_corr["CC"] = [0] * len(add_tenors)
        add_inst = "FRA"
        fut_type = "none"
        sett_d = 2
        dc_index = "SOFR_DC"
        fixed_leg = ql.Period(6, ql.Months)
        fixed_acc = ql.Thirty360(ql.Thirty360.BondBasis)
        fixed_freq = ql.Semiannual
        fixed_dcc1 = ql.Thirty360(ql.Thirty360.BondBasis)
        fixed_dcc2 = ql.ModifiedFollowing
        floating_leg = ql.Period(6, ql.Months)
        floating_acc = ql.Actual360()
        custom_index_trigger = 0
        index = ql.USDLibor
        index_a = index(ql.Period(6, ql.Months))
        calendar = ql.UnitedStates(ql.UnitedStates.Settlement)
    elif a == "EUR_6M":
        ois_trigger = 0
        batch_trigger = 1
        curncy = ql.EURCurrency()
        fixing = "EUR006M Index"
        fixing_tenor = ql.Period(6, ql.Months)
        bbg_curve = "YCSW0045 INDEX"
        bbgplot_curve_tickers = ['EUSW', 'S0045FS', 'USSOSR']
        start_swap = "2Y"
        add_tenors = pd.DataFrame()
        add_conv_corr = pd.DataFrame()
        add_tenors["FRA"] = [
            "EUFR0AG Curncy",
            "EUFR0BH Curncy",
            "EUFR0CI Curncy",
            "EUFR0DJ Curncy",
            "EUFR0EK Curncy",
            "EUFR0F1 Curncy",
            "EUFR0G1A Curncy",
            "EUFR0H1B Curncy",
            "EUFR0I1C Curncy",
            "EUFR0J1D Curncy",
            "EUFR0K1E Curncy",
            "EUFR011F Curncy",
        ]
        add_conv_corr["CC"] = [0] * len(add_tenors)
        add_inst = "FRA"
        fut_type = "none"
        sett_d = 2
        dc_index = "ESTER_DC"
        fixed_leg = ql.Period(1, ql.Years)
        fixed_acc = ql.Thirty360(ql.Thirty360.BondBasis)
        fixed_freq = ql.Annual
        fixed_dcc1 = ql.Thirty360(ql.Thirty360.BondBasis)
        fixed_dcc2 = ql.ModifiedFollowing
        floating_leg = ql.Period(6, ql.Months)
        floating_acc = ql.Actual360()
        custom_index_trigger = 0
        index = ql.Euribor
        index_a = index(ql.Period(6, ql.Months))
        calendar = ql.TARGET()
    elif a == "EUR_3M":
        ois_trigger = 0
        curncy = ql.EURCurrency()
        fixing = "EUR003M Index"
        fixing_tenor = ql.Period(3, ql.Months)
        bbg_curve = "YCSW0201 INDEX"
        bbgplot_curve_tickers = ['EUSW', 'S0201FS', 'EESF']
        start_swap = "3Y"  ##################### we need to amend this to start at 2Y
        add_tenors = pd.DataFrame()
        add_conv_corr = pd.DataFrame()
        FUT_M = FUT_CT(eval_date)
        add_tenors["FRA"] = [
            "ER" + FUT_M["TickerMonth"][i] + " Comdty" for i in range(14)
        ]
        add_conv_corr["CC"] = [
            0,
            0,
            0,
            0,
            0.001,
            0.002,
            0.003,
            0.004,
            0.005,
            0.0065,
            0.008,
            0.010,
            0.0115,
            0.0135,
        ]
        add_inst = "FUT"
        fut_type = ql.Futures.IMM
        sett_d = 2
        dc_index = "ESTER_DC"
        fixed_leg = ql.Period(1, ql.Years)
        fixed_acc = ql.Thirty360(ql.Thirty360.BondBasis)
        fixed_freq = ql.Annual
        fixed_dcc1 = ql.Thirty360(ql.Thirty360.BondBasis)
        fixed_dcc2 = ql.ModifiedFollowing
        floating_leg = ql.Period(3, ql.Months)
        floating_acc = ql.Actual360()
        custom_index_trigger = 0
        index = ql.Euribor
        index_a = index(ql.Period(3, ql.Months))
        calendar = ql.TARGET()
    elif a == "GBP_6M":
        ois_trigger = 0
        batch_trigger = 1
        curncy = ql.GBPCurrency()
        fixing = "BP0006M Index"
        fixing_tenor = ql.Period(6, ql.Months)
        bbg_curve = "YCSW0022 INDEX"
        bbgplot_curve_tickers = ['BPSW', 'S0022FS', 'GPSF']
        start_swap = "2Y"
        add_tenors = pd.DataFrame()
        add_conv_corr = pd.DataFrame()
        add_tenors["FRA"] = [
            "BPFR0AG Curncy",
            "BPFR0BH Curncy",
            "BPFR0CI Curncy",
            "BPFR0DJ Curncy",
            "BPFR0EK Curncy",
            "BPFR0F1 Curncy",
            "BPFR0I1C Curncy",
            "BPFR011F Curncy",
        ]
        add_conv_corr["CC"] = [0] * len(add_tenors)
        add_inst = "FRA"
        fut_type = "none"
        sett_d = 0
        dc_index = "SONIA_DC"
        fixed_leg = ql.Period(6, ql.Months)
        fixed_acc = ql.Actual365Fixed()
        fixed_freq = ql.Semiannual
        fixed_dcc1 = ql.Actual365Fixed(ql.Actual365Fixed.Standard)
        fixed_dcc2 = ql.ModifiedFollowing
        floating_leg = ql.Period(6, ql.Months)
        floating_acc = ql.Actual365Fixed()
        custom_index_trigger = 0
        index = ql.GBPLibor
        index_a = index(ql.Period(6, ql.Months))
        calendar = ql.UnitedKingdom()
    elif a == "GBP_3M":
        ois_trigger = 0
        curncy = ql.GBPCurrency()
        fixing = "BP0003M Index"
        fixing_tenor = ql.Period(3, ql.Months)
        bbg_curve = "YCSW0222 INDEX"
        bbgplot_curve_tickers = ['BPSW', 'S0222FS', 'GPSF']
        start_swap = "3Y"
        add_tenors = pd.DataFrame()
        add_conv_corr = pd.DataFrame()
        FUT_M = FUT_CT(eval_date)
        add_tenors["FRA"] = [
            "L " + FUT_M["TickerMonth"][i] + " Comdty" for i in range(14)
        ]
        add_conv_corr["CC"] = [
            0,
            0,
            0,
            0,
            0.001,
            0.002,
            0.003,
            0.004,
            0.005,
            0.0065,
            0.008,
            0.010,
            0.0115,
            0.0135,
        ]
        add_inst = "FUT"
        fut_type = ql.Futures.IMM
        sett_d = 0
        dc_index = "SONIA_DC"
        fixed_leg = ql.Period(3, ql.Months)
        fixed_acc = ql.Actual365Fixed()
        fixed_freq = ql.Quarterly
        fixed_dcc1 = ql.Actual365Fixed(ql.Actual365Fixed.Standard)
        fixed_dcc2 = ql.ModifiedFollowing
        floating_leg = ql.Period(3, ql.Months)
        floating_acc = ql.Actual365Fixed()
        custom_index_trigger = 0
        index = ql.GBPLibor
        index_a = index(ql.Period(3, ql.Months))
        calendar = ql.UnitedKingdom()
    elif a == "CHF_6M":
        ois_trigger = 0
        curncy = ql.CHFCurrency()
        fixing = "SF0006M Index"
        fixing_tenor = ql.Period(6, ql.Months)
        bbg_curve = "YCSW0021 INDEX"
        start_swap = "2Y"
        add_tenors = pd.DataFrame()
        add_conv_corr = pd.DataFrame()
        add_tenors["FRA"] = [
            "SFFR0AG Curncy",
            "SFFR0BH Curncy",
            "SFFR0CI Curncy",
            "SFFR0DJ Curncy",
            "SFFR0EK Curncy",
            "SFFR0F1 Curncy",
            "SFFR0I1C Curncy",
            "SFFR011F Curncy",
        ]
        add_conv_corr["CC"] = [0] * len(add_tenors)
        add_inst = "FRA"
        fut_type = "none"
        sett_d = 2
        dc_index = "CHF_OIS_DC"
        fixed_leg = ql.Period(1, ql.Years)
        fixed_acc = ql.Thirty360(ql.Thirty360.BondBasis)
        fixed_freq = ql.Annual
        fixed_dcc1 = ql.Thirty360(ql.Thirty360.BondBasis)
        fixed_dcc2 = ql.ModifiedFollowing
        floating_leg = ql.Period(6, ql.Months)
        floating_acc = ql.Actual360()
        custom_index_trigger = 1
        index = ql.IborIndex(
            "CHF_Libor_6M",
            ql.Period("6m"),
            sett_d,
            curncy,
            ql.Switzerland(),
            ql.ModifiedFollowing,
            True,
            ql.Actual360(),
        )
        index_a = ql.IborIndex(
            "CHF_Libor_6M",
            ql.Period("6m"),
            sett_d,
            curncy,
            ql.Switzerland(),
            ql.ModifiedFollowing,
            True,
            ql.Actual360(),
        )
        calendar = ql.Switzerland()
    elif a == "CHF_3M":
        ois_trigger = 0
        curncy = ql.CHFCurrency()
        fixing = "SF0003M Index"
        fixing_tenor = ql.Period(3, ql.Months)
        bbg_curve = "YCSW0254 INDEX"
        start_swap = "2Y"
        add_tenors = pd.DataFrame()
        add_conv_corr = pd.DataFrame()
        FUT_M = FUT_CT_Q(eval_date)
        add_tenors["FRA"] = [
            "ES" + FUT_M["TickerMonth"][i] + " Comdty" for i in range(6)
        ]
        add_conv_corr["CC"] = [0, 0, 0, 0, 0.001, 0.002]
        add_inst = "FUT"
        fut_type = ql.Futures.IMM
        sett_d = 2
        dc_index = "CHF_OIS_DC"
        fixed_leg = ql.Period(1, ql.Years)
        fixed_acc = ql.Thirty360(ql.Thirty360.BondBasis)
        fixed_freq = ql.Annual
        fixed_dcc1 = ql.Thirty360(ql.Thirty360.BondBasis)
        fixed_dcc2 = ql.ModifiedFollowing
        floating_leg = ql.Period(3, ql.Months)
        floating_acc = ql.Actual360()
        custom_index_trigger = 1
        index = ql.IborIndex(
            "CHF_Libor_3M",
            ql.Period("3m"),
            sett_d,
            curncy,
            ql.Switzerland(),
            ql.ModifiedFollowing,
            True,
            ql.Actual360(),
        )
        index_a = ql.IborIndex(
            "CHF_Libor_3M",
            ql.Period("3m"),
            sett_d,
            curncy,
            ql.Switzerland(),
            ql.ModifiedFollowing,
            True,
            ql.Actual360(),
        )
        calendar = ql.Switzerland()
    elif a == "JPY_6M":
        ois_trigger = 0
        curncy = ql.JPYCurrency()
        fixing = "JY0006M Index"
        fixing_tenor = ql.Period(6, ql.Months)
        bbg_curve = "YCSW0013 INDEX"
        start_swap = "2Y"
        add_tenors = pd.DataFrame()
        add_conv_corr = pd.DataFrame()
        add_tenors["FRA"] = [
            "JYFR1/7 Curncy",
            "JYFR2/8 Curncy",
            "JYFR3/9 Curncy",
            "JYFR4/10 Curncy",
            "JYFR5/11 Curncy",
            "JYFR6/12 Curncy",
            "JYFR1218 Curncy",
        ]
        add_conv_corr["CC"] = [0] * len(add_tenors)
        add_inst = "FRA"
        fut_type = "none"
        sett_d = 2
        dc_index = "TONAR_DC"
        fixed_leg = ql.Period(6, ql.Months)
        fixed_acc = ql.Actual365Fixed()
        fixed_freq = ql.Semiannual
        fixed_dcc1 = ql.Actual365Fixed(ql.Actual365Fixed.Standard)
        fixed_dcc2 = ql.ModifiedFollowing
        floating_leg = ql.Period(6, ql.Months)
        floating_acc = ql.Actual360()
        custom_index_trigger = 0
        index = ql.JPYLibor
        index_a = index(ql.Period(6, ql.Months))
        calendar = ql.Japan()
    elif a == "AUD_6M":
        ois_trigger = 0
        batch_trigger = 0
        curncy = ql.AUDCurrency()
        fixing = "BBSW6M Index"
        fixing_tenor = ql.Period(6, ql.Months)
        bbg_curve = "YCSW0302 INDEX"
        bbgplot_curve_tickers = ['ADSWAP', 'S0302FS']
        start_swap = "2Y"
        add_tenors = pd.DataFrame()
        add_conv_corr = pd.DataFrame()
        add_tenors["FRA"] = [
            "ADFR0AG Curncy",
            "ADFR0BH Curncy",
            "ADFR0CI Curncy",
            "ADFR0DJ Curncy",
            "ADFR0EK Curncy",
            "ADFR0F1 Curncy",
            "ADFR0I1C Curncy",
            "ADFR011F Curncy",
        ]
        add_conv_corr["CC"] = [0] * len(add_tenors)
        add_inst = "FRA"
        fut_type = "none"
        sett_d = 1
        dc_index = "AONIA_DC"
        fixed_leg = ql.Period(6, ql.Months)
        fixed_acc = ql.Actual365Fixed()
        fixed_freq = ql.Semiannual
        fixed_dcc1 = ql.Actual365Fixed(ql.Actual365Fixed.Standard)
        fixed_dcc2 = ql.ModifiedFollowing
        floating_leg = ql.Period(6, ql.Months)
        floating_acc = ql.Actual365Fixed()
        custom_index_trigger = 1
        index = ql.IborIndex(
            "AUD_Libor_6M",
            ql.Period("6m"),
            sett_d,
            curncy,
            ql.Australia(),
            ql.ModifiedFollowing,
            True,
            ql.Actual365Fixed(),
        )
        index_a = ql.IborIndex(
            "AUD_Libor_6M",
            ql.Period("6m"),
            sett_d,
            curncy,
            ql.Australia(),
            ql.ModifiedFollowing,
            True,
            ql.Actual365Fixed(),
        )
        calendar = ql.Australia()
    elif a == "AUD_3M":
        ois_trigger = 0
        batch_trigger = 0
        curncy = ql.AUDCurrency()
        fixing = "BBSW3M Index"
        fixing_tenor = ql.Period(3, ql.Months)
        bbg_curve = "YCSW0303 INDEX"
        bbgplot_curve_tickers = ['ADSWAP', 'S0303FS']
        start_swap = "2Y"
        add_tenors = pd.DataFrame()
        add_conv_corr = pd.DataFrame()
        FUT_M = FUT_CT_Q(eval_date)
        add_tenors["FRA"] = [
            "IR" + FUT_M["TickerMonth"][i] + " Comdty" for i in range(6)
        ]
        add_conv_corr["CC"] = [0, 0, 0, 0, 0.001, 0.002]
        add_inst = "FUT"
        fut_type = ql.Futures.ASX
        sett_d = 1
        dc_index = "AONIA_DC"
        fixed_leg = ql.Period(3, ql.Months)
        fixed_acc = ql.Actual365Fixed()
        fixed_freq = ql.Quarterly
        fixed_dcc1 = ql.Actual365Fixed(ql.Actual365Fixed.Standard)
        fixed_dcc2 = ql.ModifiedFollowing
        floating_leg = ql.Period(3, ql.Months)
        floating_acc = ql.Actual365Fixed()
        custom_index_trigger = 1
        index = ql.IborIndex(
            "AUD_Libor_3M",
            ql.Period("3m"),
            sett_d,
            curncy,
            ql.Australia(),
            ql.ModifiedFollowing,
            True,
            ql.Actual365Fixed(),
        )
        index_a = ql.IborIndex(
            "AUD_Libor_3M",
            ql.Period("3m"),
            sett_d,
            curncy,
            ql.Australia(),
            ql.ModifiedFollowing,
            True,
            ql.Actual365Fixed(),
        )
        calendar = ql.Australia()
    elif a == "CAD_3M":
        ois_trigger = 0
        batch_trigger = 0
        curncy = ql.CADCurrency()
        fixing = "CDOR03 Index"
        fixing_tenor = ql.Period(3, ql.Months)
        bbg_curve = "YCSW0004 INDEX"
        bbgplot_curve_tickers = ['CDSW', 'S0004FS', 'CDSF']
        start_swap = "2Y"
        add_tenors = pd.DataFrame()
        add_conv_corr = pd.DataFrame()
        FUT_M = FUT_CT_Q(eval_date)
        add_tenors["FRA"] = [
            "BA" + FUT_M["TickerMonth"][i] + " Comdty" for i in range(10)
        ]
        add_conv_corr["CC"] = [0, 0, 0, 0, 0.001, 0.002, 0.003, 0.004, 0.005, 0.0065]
        add_inst = "FUT"
        fut_type = ql.Futures.IMM
        sett_d = 2
        dc_index = "CAD_OIS_DC"
        fixed_leg = ql.Period(6, ql.Months)
        fixed_acc = ql.Actual365Fixed()
        fixed_freq = ql.Semiannual
        fixed_dcc1 = ql.Actual365Fixed(ql.Actual365Fixed.Standard)
        fixed_dcc2 = ql.ModifiedFollowing
        floating_leg = ql.Period(3, ql.Months)
        floating_acc = ql.Actual365Fixed()
        custom_index_trigger = 1
        index = ql.IborIndex(
            "CAD_Libor_3M",
            ql.Period("3m"),
            sett_d,
            curncy,
            ql.Canada(),
            ql.ModifiedFollowing,
            True,
            ql.Actual365Fixed(),
        )
        index_a = ql.IborIndex(
            "CAD_Libor_3M",
            ql.Period("3m"),
            sett_d,
            curncy,
            ql.Canada(),
            ql.ModifiedFollowing,
            True,
            ql.Actual365Fixed(),
        )
        calendar = ql.Canada()
    elif a == "NZD_3M":
        ois_trigger = 0
        curncy = ql.NZDCurrency()
        fixing = "NDFR00C Curncy"  #################### this is the 0x3 FRA - real fix accessible via NFIX3FRA Index
        fixing_tenor = ql.Period(3, ql.Months)
        bbg_curve = "YCSW0015 INDEX"
        start_swap = "2Y"
        add_tenors = pd.DataFrame()
        #        add_tenors['value'] = ['NDSWAP25 Curncy','NDSWAP30 Curncy']
        #        add_tenors['Tenor'] = ['25Y','30Y']
        add_conv_corr = pd.DataFrame()
        add_tenors["FRA"] = [
            "NDFR0AD Curncy",
            "NDFR0BE Curncy",
            "NDFR0CF Curncy",
            "NDFR0DG Curncy",
            "NDFR0FI Curncy",
            "NDFR0GJ Curncy",
            "NDFR0HK Curncy",
            "NDFR0I1 Curncy",
        ]
        add_conv_corr["CC"] = [0] * len(add_tenors)
        add_inst = "FRA"
        fut_type = "none"
        sett_d = 2
        dc_index = "NZD_OIS_DC"
        fixed_leg = ql.Period(6, ql.Months)
        fixed_acc = ql.Actual365Fixed()
        fixed_freq = ql.Semiannual
        fixed_dcc1 = ql.Actual365Fixed(ql.Actual365Fixed.Standard)
        fixed_dcc2 = ql.ModifiedFollowing
        floating_leg = ql.Period(3, ql.Months)
        floating_acc = ql.Actual365Fixed()
        custom_index_trigger = 1
        index = ql.IborIndex(
            "NZD_Libor_3M",
            ql.Period("3m"),
            sett_d,
            curncy,
            ql.NewZealand(),
            ql.ModifiedFollowing,
            True,
            ql.Actual365Fixed(),
        )
        index_a = ql.IborIndex(
            "NZD_Libor_3M",
            ql.Period("3m"),
            sett_d,
            curncy,
            ql.NewZealand(),
            ql.ModifiedFollowing,
            True,
            ql.Actual365Fixed(),
        )
        calendar = ql.NewZealand()
    elif a == "KRW_3M":
        ois_trigger = 0
        curncy = ql.KRWCurrency()
        fixing = "KWCDC Index"
        fixing_tenor = ql.Period(3, ql.Months)
        bbg_curve = "YCSW0205 INDEX"
        start_swap = "9M"
        add_tenors = pd.DataFrame()
        add_conv_corr = pd.DataFrame()
        #        add_tenors['FRA']= ['KWFS0A0C Curncy', 'KWFC0B0C Curncy', 'KWFS0C0C Curncy', 'KWFC0D0C Curncy', 'KWFC0E0C Curncy',
        #                            'KWFS0F0C Curncy','KWFC0G0C Curncy', 'KWFC0H0C Curncy']
        add_conv_corr["CC"] = [0] * len(add_tenors)
        add_inst = "NONE"
        fut_type = "none"
        sett_d = 1
        dc_index = "SOFR_DC"
        fixed_leg = ql.Period(3, ql.Months)
        fixed_acc = ql.Actual365Fixed()
        fixed_freq = ql.Quarterly
        fixed_dcc1 = ql.Actual365Fixed(ql.Actual365Fixed.Standard)
        fixed_dcc2 = ql.ModifiedFollowing
        floating_leg = ql.Period(3, ql.Months)
        floating_acc = ql.Actual365Fixed()
        custom_index_trigger = 1
        index = ql.IborIndex(
            "KRW_CD_3M",
            ql.Period("3m"),
            sett_d,
            curncy,
            ql.SouthKorea(),
            ql.ModifiedFollowing,
            True,
            ql.Actual365Fixed(),
        )
        index_a = ql.IborIndex(
            "KRW_CD_3M",
            ql.Period("3m"),
            sett_d,
            curncy,
            ql.SouthKorea(),
            ql.ModifiedFollowing,
            True,
            ql.Actual365Fixed(),
        )
        calendar = ql.SouthKorea()
    elif a == "SEK_3M":  ##################### Haveto convert 3m FRAs to Futures equivalent
        ois_trigger = 0
        curncy = ql.SEKCurrency()
        fixing = "STIB3M Index"
        fixing_tenor = ql.Period(3, ql.Months)
        bbg_curve = "YCSW0020 INDEX"
        start_swap = "2Y"
        add_tenors = pd.DataFrame()
        add_conv_corr = pd.DataFrame()
        add_tenors["FRA"] = [
            "SKF30001 Curncy",
            "SKF30101 Curncy",
            "SKF30201 Curncy",
            "SKF30301 Curncy",
            "SKF30401 Curncy",
            "SKF30501 Curncy",
        ]
        add_conv_corr["CC"] = [0] * len(add_tenors)
        add_inst = "FUT"
        fut_type = ql.Futures.IMM
        sett_d = 2
        dc_index = "SEK_OIS_DC"
        fixed_leg = ql.Period(1, ql.Years)
        fixed_acc = ql.Thirty360(ql.Thirty360.BondBasis)
        fixed_freq = ql.Annual
        fixed_dcc1 = ql.Thirty360(ql.Thirty360.BondBasis)
        fixed_dcc2 = ql.ModifiedFollowing
        floating_leg = ql.Period(3, ql.Months)
        floating_acc = ql.Actual360()
        custom_index_trigger = 0
        index = ql.SEKLibor
        index_a = index(ql.Period(3, ql.Months))
        calendar = ql.Sweden()
    elif a == "NOK_3M":
        ois_trigger = 0
        curncy = ql.NOKCurrency()
        fixing = "NIBOR3M Index"
        fixing_tenor = ql.Period(3, ql.Months)
        bbg_curve = "YCSW0312 INDEX"
        start_swap = "2Y"
        add_tenors = pd.DataFrame()
        add_conv_corr = pd.DataFrame()
        add_tenors["FRA"] = [
            "NKF30001 Curncy",
            "NKF30101 Curncy",
            "NKF30201 Curncy",
            "NKF30301 Curncy",
            "NKF30401 Curncy",
            "NKF30501 Curncy",
        ]
        add_conv_corr["CC"] = [0] * len(add_tenors)
        add_inst = "FUT"
        fut_type = ql.Futures.IMM
        sett_d = 2
        dc_index = "NOK_3M"
        fixed_leg = ql.Period(1, ql.Years)
        fixed_acc = ql.Thirty360(ql.Thirty360.BondBasis)
        fixed_freq = ql.Annual
        fixed_dcc1 = ql.Thirty360(ql.Thirty360.BondBasis)
        fixed_dcc2 = ql.ModifiedFollowing
        floating_leg = ql.Period(3, ql.Months)
        floating_acc = ql.Actual360()
        custom_index_trigger = 1
        index = ql.IborIndex(
            "NOK_Libor_3M",
            ql.Period("3m"),
            sett_d,
            curncy,
            ql.Norway(),
            ql.ModifiedFollowing,
            True,
            ql.Actual360(),
        )
        index_a = ql.IborIndex(
            "NOK_Libor_3M",
            ql.Period("3m"),
            sett_d,
            curncy,
            ql.Norway(),
            ql.ModifiedFollowing,
            True,
            ql.Actual360(),
        )
        calendar = ql.Norway()
    elif a == "NOK_6M":
        ois_trigger = 0
        curncy = ql.NOKCurrency()
        fixing = "NIBOR6M Index"
        fixing_tenor = ql.Period(6, ql.Months)
        bbg_curve = "YCSW0313 INDEX"
        start_swap = "2Y"
        add_tenors = pd.DataFrame()
        add_conv_corr = pd.DataFrame()
        add_tenors["FRA"] = [
            "NKF60001 Curncy",
            "NKF60101 Curncy",
            "NKF60201 Curncy",
            "NKF60301 Curncy",
            "NKF60401 Curncy",
        ]
        add_conv_corr["CC"] = [0] * len(add_tenors)
        add_inst = "FUT"
        fut_type = ql.Futures.IMM
        sett_d = 2
        dc_index = "NOK_3M"
        fixed_leg = ql.Period(1, ql.Years)
        fixed_acc = ql.Thirty360(ql.Thirty360.BondBasis)
        fixed_freq = ql.Annual
        fixed_dcc1 = ql.Thirty360(ql.Thirty360.BondBasis)
        fixed_dcc2 = ql.ModifiedFollowing
        floating_leg = ql.Period(3, ql.Months)
        floating_acc = ql.Actual360()
        custom_index_trigger = 1
        index = ql.IborIndex(
            "NOK_Libor_3M",
            ql.Period("3m"),
            sett_d,
            curncy,
            ql.Norway(),
            ql.ModifiedFollowing,
            True,
            ql.Actual360(),
        )
        index_a = ql.IborIndex(
            "NOK_Libor_3M",
            ql.Period("3m"),
            sett_d,
            curncy,
            ql.Norway(),
            ql.ModifiedFollowing,
            True,
            ql.Actual360(),
        )
        calendar = ql.Norway()
    elif a == "PLN_3M":
        ois_trigger = 0
        curncy = ql.PLNCurrency()
        fixing = "WIBR3M Index"
        fixing_tenor = ql.Period(3, ql.Months)
        bbg_curve = "YCSW0322 INDEX"
        start_swap = "3Y"
        add_tenors = pd.DataFrame()
        add_conv_corr = pd.DataFrame()
        add_tenors["FRA"] = [
            "PZFR0AD Curncy",
            "PZFR0BE Curncy",
            "PZFR0CF Curncy",
            "PZFR0DG Curncy",
            "PZFR0EH Curncy",
            "PZFR0FI Curncy",
            "PZFR0GJ Curncy",
            "PZFR0HK Curncy",
            "PZFR0I1 Curncy",
            "PZFR011C Curncy",
            "PZFR1C1F Curncy",
            "PZFR1F1I Curncy",
            "PZFR1I2 Curncy",
        ]
        add_conv_corr["CC"] = [0] * len(add_tenors)
        add_inst = "FRA"
        fut_type = "none"
        sett_d = 2
        dc_index = "PLN_3M"
        fixed_leg = ql.Period(1, ql.Years)
        fixed_acc = ql.ActualActual(ql.ActualActual.ISDA)
        fixed_freq = ql.Annual
        fixed_dcc1 = ql.ActualActual(ql.ActualActual.ISDA)
        fixed_dcc2 = ql.ModifiedFollowing
        floating_leg = ql.Period(3, ql.Months)
        floating_acc = ql.Actual365Fixed()
        custom_index_trigger = 1
        index = ql.IborIndex(
            "PLN_Wibor_3M",
            ql.Period("3m"),
            sett_d,
            curncy,
            ql.Poland(),
            ql.ModifiedFollowing,
            True,
            ql.Actual365Fixed(),
        )
        index_a = ql.IborIndex(
            "PLN_Wibor_3M",
            ql.Period("3m"),
            sett_d,
            curncy,
            ql.Poland(),
            ql.ModifiedFollowing,
            True,
            ql.Actual365Fixed(),
        )
        calendar = ql.Poland()
    elif a == "PLN_6M":
        ois_trigger = 0
        curncy = ql.PLNCurrency()
        fixing = "WIBR6M Index"
        fixing_tenor = ql.Period(3, ql.Months)
        bbg_curve = "YCSW0323 INDEX"
        start_swap = "2Y"
        add_tenors = pd.DataFrame()
        add_conv_corr = pd.DataFrame()
        add_tenors["FRA"] = [
            "PZFR0AG Curncy",
            "PZFR0BH Curncy",
            "PZFR0CI Curncy",
            "PZFR0DJ Curncy",
            "PZFR0EK Curncy",
            "PZFR0F1 Curncy",
            "PZFR011F Curncy",
        ]
        add_conv_corr["CC"] = [0] * len(add_tenors)
        add_inst = "FRA"
        fut_type = "none"
        sett_d = 2
        dc_index = "PLN_6M"
        fixed_leg = ql.Period(1, ql.Years)
        fixed_acc = ql.ActualActual(ql.ActualActual.ISDA)
        fixed_freq = ql.Annual
        fixed_dcc1 = ql.ActualActual(ql.ActualActual.ISDA)
        fixed_dcc2 = ql.ModifiedFollowing
        floating_leg = ql.Period(6, ql.Months)
        floating_acc = ql.Actual365Fixed()
        custom_index_trigger = 1
        index = ql.IborIndex(
            "PLN_Wibor_6M",
            ql.Period("6m"),
            sett_d,
            curncy,
            ql.Poland(),
            ql.ModifiedFollowing,
            True,
            ql.Actual365Fixed(),
        )
        index_a = ql.IborIndex(
            "PLN_Wibor_6M",
            ql.Period("6m"),
            sett_d,
            curncy,
            ql.Poland(),
            ql.ModifiedFollowing,
            True,
            ql.Actual365Fixed(),
        )
        calendar = ql.Poland()
    elif a == "CZK_3M":
        ois_trigger = 0
        curncy = ql.CZKCurrency()
        fixing = "PRIB03M Index"
        fixing_tenor = ql.Period(3, ql.Months)
        bbg_curve = "YCSW0319 INDEX"
        start_swap = "2Y"
        add_tenors = pd.DataFrame()
        add_conv_corr = pd.DataFrame()
        add_tenors["FRA"] = [
            "CKFR0AD Curncy",
            "CKFR0BE Curncy",
            "CKFR0CF Curncy",
            "CKFR0DG Curncy",
            "CKFR0EH Curncy",
            "CKFR0FI Curncy",
            "CKFR0GJ Curncy",
            "CKFR0HK Curncy",
            "CKFR0I1 Curncy",
            "CKFR011C Curncy",
            "CKFR1C1F Curncy",
            "CKFR1F1I Curncy",
        ]
        add_conv_corr["CC"] = [0] * len(add_tenors)
        add_inst = "FRA"
        fut_type = "none"
        sett_d = 2
        dc_index = "CZK_3M"
        fixed_leg = ql.Period(1, ql.Years)
        fixed_acc = ql.Actual360()
        fixed_freq = ql.Annual
        fixed_dcc1 = ql.Actual360()
        fixed_dcc2 = ql.ModifiedFollowing
        floating_leg = ql.Period(3, ql.Months)
        floating_acc = ql.Actual360()
        custom_index_trigger = 1
        index = ql.IborIndex(
            "CZK_Pribor_3M",
            ql.Period("3m"),
            sett_d,
            curncy,
            ql.CzechRepublic(),
            ql.ModifiedFollowing,
            True,
            ql.Actual360(),
        )
        index_a = ql.IborIndex(
            "CZK_Pribor_3M",
            ql.Period("3m"),
            sett_d,
            curncy,
            ql.CzechRepublic(),
            ql.ModifiedFollowing,
            True,
            ql.Actual360(),
        )
        calendar = ql.CzechRepublic()
    elif a == "CZK_6M":
        ois_trigger = 0
        curncy = ql.CZKCurrency()
        fixing = "PRIB06M Index"
        fixing_tenor = ql.Period(6, ql.Months)
        bbg_curve = "YCSW0320 INDEX"
        start_swap = "2Y"
        add_tenors = pd.DataFrame()
        add_conv_corr = pd.DataFrame()
        add_tenors["FRA"] = [
            "CKFR0AG Curncy",
            "CKFR0BH Curncy",
            "CKFR0CI Curncy",
            "CKFR0DJ Curncy",
            "CKFR0EK Curncy",
            "CKFR0F1 Curncy",
            "CKFR011F Curncy",
        ]
        add_conv_corr["CC"] = [0] * len(add_tenors)
        add_inst = "FRA"
        fut_type = "none"
        sett_d = 2
        dc_index = "CZK_6M"
        fixed_leg = ql.Period(1, ql.Years)
        fixed_acc = ql.Actual360()
        fixed_freq = ql.Annual
        fixed_dcc1 = ql.Actual360()
        fixed_dcc2 = ql.ModifiedFollowing
        floating_leg = ql.Period(6, ql.Months)
        floating_acc = ql.Actual360()
        custom_index_trigger = 1
        index = ql.IborIndex(
            "CZK_Pribor_6M",
            ql.Period("6m"),
            sett_d,
            curncy,
            ql.CzechRepublic(),
            ql.ModifiedFollowing,
            True,
            ql.Actual360(),
        )
        index_a = ql.IborIndex(
            "CZK_Pribor_6M",
            ql.Period("6m"),
            sett_d,
            curncy,
            ql.CzechRepublic(),
            ql.ModifiedFollowing,
            True,
            ql.Actual360(),
        )
        calendar = ql.CzechRepublic()
    elif a == "HUF_3M":
        ois_trigger = 0
        curncy = ql.HUFCurrency()
        fixing = "BUBOR03M Index"
        fixing_tenor = ql.Period(3, ql.Months)
        bbg_curve = "YCSW0324 INDEX"
        start_swap = "2Y"
        add_tenors = pd.DataFrame()
        add_conv_corr = pd.DataFrame()
        add_tenors["FRA"] = [
            "HFFR0AD Curncy",
            "HFFR0BE Curncy",
            "HFFR0CF Curncy",
            "HFFR0DG Curncy",
            "HFFR0EH Curncy",
            "HFFR0FI Curncy",
            "HFFR0I1 Curncy",
            "HFFR011C Curncy",
            "HFFR1C1F Curncy",
            "HFFR1F1I Curncy",
        ]
        add_conv_corr["CC"] = [0] * len(add_tenors)
        add_inst = "FRA"
        fut_type = "none"
        sett_d = 2
        dc_index = "HUF_3M"
        fixed_leg = ql.Period(3, ql.Months)
        fixed_acc = ql.Actual365Fixed()
        fixed_freq = ql.Quarterly
        fixed_dcc1 = ql.Actual365Fixed(ql.Actual365Fixed.Standard)
        fixed_dcc2 = ql.ModifiedFollowing
        floating_leg = ql.Period(3, ql.Months)
        floating_acc = ql.Actual360()
        custom_index_trigger = 1
        index = ql.IborIndex(
            "HUF_Bubor_3M",
            ql.Period("3m"),
            sett_d,
            curncy,
            ql.Hungary(),
            ql.ModifiedFollowing,
            True,
            ql.Actual360(),
        )
        index_a = ql.IborIndex(
            "HUF_Bubor_3M",
            ql.Period("3m"),
            sett_d,
            curncy,
            ql.Hungary(),
            ql.ModifiedFollowing,
            True,
            ql.Actual360(),
        )
        calendar = ql.Hungary()
    elif a == "HUF_6M":
        ois_trigger = 0
        curncy = ql.HUFCurrency()
        fixing = "BUBOR06M Index"
        fixing_tenor = ql.Period(6, ql.Months)
        bbg_curve = "YCSW0325 INDEX"
        start_swap = "2Y"
        add_tenors = pd.DataFrame()
        add_conv_corr = pd.DataFrame()
        add_tenors["FRA"] = [
            "HFFR0AG Curncy",
            "HFFR0BH Curncy",
            "HFFR0CI Curncy",
            "HFFR0DJ Curncy",
            "HFFR0EK Curncy",
            "HFFR0F1 Curncy",
            "HFFR011F Curncy",
        ]
        add_conv_corr["CC"] = [0] * len(add_tenors)
        add_inst = "FRA"
        fut_type = "none"
        sett_d = 2
        dc_index = "HUF_6M"
        fixed_leg = ql.Period(1, ql.Years)
        fixed_acc = ql.Actual365Fixed()
        fixed_freq = ql.Annual
        fixed_dcc1 = ql.Actual365Fixed(ql.Actual365Fixed.Standard)
        fixed_dcc2 = ql.ModifiedFollowing
        floating_leg = ql.Period(6, ql.Months)
        floating_acc = ql.Actual360()
        custom_index_trigger = 1
        index = ql.IborIndex(
            "HUF_Bubor_6M",
            ql.Period("6m"),
            sett_d,
            curncy,
            ql.Hungary(),
            ql.ModifiedFollowing,
            True,
            ql.Actual360(),
        )
        index_a = ql.IborIndex(
            "HUF_Bubor_6M",
            ql.Period("6m"),
            sett_d,
            curncy,
            ql.Hungary(),
            ql.ModifiedFollowing,
            True,
            ql.Actual360(),
        )
        calendar = ql.Hungary()
    elif a == "ZAR_3M":
        ois_trigger = 0
        curncy = ql.ZARCurrency()
        fixing = "JIBA3M Index"
        fixing_tenor = ql.Period(3, ql.Months)
        bbg_curve = "YCSW0018 INDEX"
        start_swap = "3Y"
        add_tenors = pd.DataFrame()
        add_conv_corr = pd.DataFrame()
        add_tenors["FRA"] = [
            "SAFR0AD Curncy",
            "SAFR0BE Curncy",
            "SAFR0CF Curncy",
            "SAFR0DG Curncy",
            "SAFR0EH Curncy",
            "SAFR0FI Curncy",
            "SAFR0GJ Curncy",
            "SAFR0HK Curncy",
            "SAFR0I1 Curncy",
            "SAFR011C Curncy",
            "SAFR1C1F Curncy",
            "SAFR1F1I Curncy",
            "SAFR1I2 Curncy",
        ]
        add_conv_corr["CC"] = [0] * len(add_tenors)
        add_inst = "FRA"
        fut_type = "none"
        sett_d = 0
        dc_index = "ZAR_3M"
        fixed_leg = ql.Period(3, ql.Months)
        fixed_acc = ql.Actual365Fixed()
        fixed_freq = ql.Quarterly
        fixed_dcc1 = ql.Actual365Fixed(ql.Actual365Fixed.Standard)
        fixed_dcc2 = ql.ModifiedFollowing
        floating_leg = ql.Period(3, ql.Months)
        floating_acc = ql.Actual365Fixed()
        custom_index_trigger = 1
        index = ql.IborIndex(
            "ZAR_Jibar_3M",
            ql.Period("3m"),
            sett_d,
            curncy,
            ql.SouthAfrica(),
            ql.ModifiedFollowing,
            True,
            ql.Actual365Fixed(),
        )
        index_a = ql.IborIndex(
            "ZAR_Jibar_3M",
            ql.Period("3m"),
            sett_d,
            curncy,
            ql.SouthAfrica(),
            ql.ModifiedFollowing,
            True,
            ql.Actual365Fixed(),
        )
        calendar = ql.SouthAfrica()
    elif a == "ILS_3M":
        ois_trigger = 0
        curncy = ql.ILSCurrency()
        fixing = "TELBOR03 Index"
        fixing_tenor = ql.Period(3, ql.Months)
        bbg_curve = "YCSW0162 INDEX"
        start_swap = "2Y"
        add_tenors = pd.DataFrame()
        add_conv_corr = pd.DataFrame()
        add_tenors["FRA"] = [
            "ISFR0AD Curncy",
            "ISFR0BE Curncy",
            "ISFR0CF Curncy",
            "ISFR0FI Curncy",
            "ISFR0I1 Curncy",
            "ISFR011C Curncy",
            "ISFR1C1F Curncy",
            "ISFR1F1I Curncy",
        ]
        add_conv_corr["CC"] = [0] * len(add_tenors)
        add_inst = "FRA"
        fut_type = "none"
        sett_d = 2
        dc_index = "ILS_3M"
        fixed_leg = ql.Period(1, ql.Years)
        fixed_acc = ql.Actual365Fixed()
        fixed_freq = ql.Annual
        fixed_dcc1 = ql.Actual365Fixed(ql.Actual365Fixed.Standard)
        fixed_dcc2 = ql.ModifiedFollowing
        floating_leg = ql.Period(3, ql.Months)
        floating_acc = ql.Actual365Fixed()
        custom_index_trigger = 1
        index = ql.IborIndex(
            "ILS_Telbor_3M",
            ql.Period("3m"),
            sett_d,
            curncy,
            ql.Israel(),
            ql.ModifiedFollowing,
            True,
            ql.Actual365Fixed(),
        )
        index_a = ql.IborIndex(
            "ILS_Telbor_3M",
            ql.Period("3m"),
            sett_d,
            curncy,
            ql.Israel(),
            ql.ModifiedFollowing,
            True,
            ql.Actual365Fixed(),
        )
        calendar = ql.Israel()
    elif a == "RUB_3M":
        ois_trigger = 0
        curncy = ql.RUBCurrency()
        fixing = "MOSKP3 Index"
        fixing_tenor = ql.Period(3, ql.Months)
        bbg_curve = "YCSW0179 INDEX"
        start_swap = "2Y"
        add_tenors = pd.DataFrame()
        add_conv_corr = pd.DataFrame()
        add_tenors["FRA"] = [
            "RRFR0AD Curncy",
            "RRFR0BE Curncy",
            "RRFR0CF Curncy",
            "RRFR0FI Curncy",
            "RRFR0I1 Curncy",
            "RRFR011C Curncy",
            "RRFR1C1F Curncy",
            "RRFR1F1I Curncy",
        ]
        add_conv_corr["CC"] = [0] * len(add_tenors)
        add_inst = "FRA"
        fut_type = "none"
        sett_d = 1
        dc_index = "RUONIA_DC"
        fixed_leg = ql.Period(1, ql.Years)
        fixed_acc = ql.ActualActual(ql.ActualActual.ISDA)
        fixed_freq = ql.Annual
        fixed_dcc1 = ql.ActualActual(ql.ActualActual.ISDA)
        fixed_dcc2 = ql.ModifiedFollowing
        floating_leg = ql.Period(3, ql.Months)
        floating_acc = ql.ActualActual(ql.ActualActual.ISDA)
        custom_index_trigger = 1
        index = ql.IborIndex(
            "RUB_Prime_3M",
            ql.Period("3m"),
            sett_d,
            curncy,
            ql.Russia(),
            ql.ModifiedFollowing,
            True,
            ql.ActualActual(ql.ActualActual.ISDA),
        )
        index_a = ql.IborIndex(
            "RUB_Prime_3M",
            ql.Period("3m"),
            sett_d,
            curncy,
            ql.Russia(),
            ql.ModifiedFollowing,
            True,
            ql.ActualActual(ql.ActualActual.ISDA),
        )
        calendar = ql.Russia()
    elif a == "MXN_TIIE":
        ois_trigger = 0
        curncy = ql.MXNCurrency()
        fixing = "MXIBTIIE Index"
        fixing_tenor = ql.Period(28, ql.Days)
        bbg_curve = "YCSW0083 INDEX"
        start_swap = "3M"  ###################
        add_tenors = pd.DataFrame()
        add_conv_corr = pd.DataFrame()
        add_conv_corr["CC"] = [0] * len(add_tenors)
        add_inst = "NONE"
        fut_type = "none"
        sett_d = 1
        dc_index = "SOFR_DC"
        fixed_leg = ql.Period(28, ql.Days)
        fixed_acc = ql.Actual360()
        fixed_freq = ql.EveryFourthWeek
        fixed_dcc1 = ql.Actual360()
        fixed_dcc2 = ql.ModifiedFollowing
        floating_leg = ql.Period(28, ql.Days)
        floating_acc = ql.Actual360()
        custom_index_trigger = 1
        index = ql.IborIndex(
            "MXN_TIIE_28D",
            ql.Period("28D"),
            sett_d,
            curncy,
            ql.Mexico(),
            ql.ModifiedFollowing,
            True,
            ql.Actual360(),
        )
        index_a = ql.IborIndex(
            "MXN_TIIE_28D",
            ql.Period("28D"),
            sett_d,
            curncy,
            ql.Mexico(),
            ql.ModifiedFollowing,
            True,
            ql.Actual360(),
        )
        calendar = ql.Mexico()

    elif a == "EONIA_DC":
        ois_trigger = 1
        batch_trigger = 0
        curncy = ql.EURCurrency()
        fixing = "EONIA Index"
        fixing_tenor = ql.Period(1, ql.Days)
        bbg_curve = "YCSW0133 INDEX"
        add_tenors = pd.DataFrame()
        sett_d = 2
        fixed_leg = ql.Period(1, ql.Years)
        fixed_acc = ql.Actual360()
        fixed_freq = ql.Annual
        floating_leg = ql.Period(1, ql.Years)
        floating_acc = ql.Actual360()
        custom_index_trigger = 0
        index = ql.Eonia
        index_a = ql.Eonia()
        calendar = ql.TARGET()
        fut_type = "none"
        eom = -1.0 / 3600000
        eoq = -2.0 / 3600000
        eoy = -15.0 / 3600000
    elif a == "ESTER_DC":
        ois_trigger = 1
        batch_trigger = 1
        curncy = ql.EURCurrency()
        base_ticker = 'EURR002W Index'
        fixing = "ESTRON Index"
        fixing_tenor = ql.Period(1, ql.Days)
        bbg_curve = "YCSW0514 INDEX"
        bbgplot_curve_tickers = ['EESWE', 'S0514FS','EESF']
        ois_contrib = ['TRSO',15]
        ois_meet_hist = pd.read_pickle("./DataLake/ESTER_DC_OIS_MEETING_HIST.pkl")
        add_tenors = pd.DataFrame()
        sett_d = 2
        fixed_leg = ql.Period(1, ql.Years)
        fixed_acc = ql.Actual360()
        fixed_freq = ql.Annual
        floating_leg = ql.Period(1, ql.Years)
        floating_acc = ql.Actual360()
        custom_index_trigger = 1
        index = ql.OvernightIndex(
            "ESTER", 1, ql.EURCurrency(), ql.TARGET(), ql.Actual360()
        )
        index_a = ql.OvernightIndex(
            "ESTER", 1, ql.EURCurrency(), ql.TARGET(), ql.Actual360()
        )
        calendar = ql.TARGET()
        fut_type = "none"
        eom = -1.0 / 3600000
        eoq = -2.0 / 3600000
        eoy = -15.0 / 3600000
    elif a == "SOFR_DC":
        ois_trigger = 1
        batch_trigger = 1
        curncy = ql.USDCurrency()
        base_ticker = 'FDTR Index'
        fixing = "SOFRRATE Index"
        fixing_tenor = ql.Period(1, ql.Days)
        bbg_curve = "YCSW0490 INDEX"
        bbgplot_curve_tickers = ['USOSFR', 'S0490FS', 'USSOSR']
        ois_contrib = ['TRSO', 16]
        ois_meet_hist = pd.read_pickle("./DataLake/SOFR_DC_OIS_MEETING_HIST.pkl")
        add_tenors = pd.DataFrame()
        sett_d = 2
        fixed_leg = ql.Period(1, ql.Years)
        fixed_acc = ql.Actual360()
        fixed_freq = ql.Annual
        floating_leg = ql.Period(1, ql.Years)
        floating_acc = ql.Actual360()
        custom_index_trigger = 1
        index = ql.Sofr
        index_a = ql.OvernightIndex(
            'SOFR', 1, ql.USDCurrency(), ql.UnitedStates(ql.UnitedStates.FederalReserve), ql.Actual360()
        )
        calendar = ql.UnitedStates(ql.UnitedStates.FederalReserve)
        fut_type = "none"
        eom = 0.0 / 3600000
        eoq = 0.0 / 3600000
        eoy = 0.0 / 3600000
    elif a == "FED_DC":
        ois_trigger = 1
        batch_trigger = 0
        curncy = ql.USDCurrency()
        base_ticker = 'FDTR Index'
        fixing = "FEDL01 Index"
        fixing_tenor = ql.Period(1, ql.Days)
        bbg_curve = "YCSW0042 INDEX"
        bbgplot_curve_tickers = ['USSO', 'S0042FS', 'USSOSR']
        ois_contrib = ['TRSO', 16]
        ois_meet_hist = pd.read_pickle("./DataLake/SOFR_DC_OIS_MEETING_HIST.pkl")
        add_tenors = pd.DataFrame()
        add_tenors["value"] = [
            "USSO15 Curncy",
            "USSO20 Curncy",
            "USSO30 Curncy",
            "USSO40 Curncy",
        ]
        add_tenors["Tenor"] = ["15Y", "20Y", "30Y", "40Y"]
        sett_d = 2
        fixed_leg = ql.Period(1, ql.Years)
        fixed_acc = ql.Actual360()
        fixed_freq = ql.Annual
        floating_leg = ql.Period(1, ql.Years)
        floating_acc = ql.Actual360()
        custom_index_trigger = 0
        index = ql.FedFunds
        index_a = ql.FedFunds()
        calendar = ql.UnitedStates(ql.UnitedStates.FederalReserve)
        fut_type = "none"
        eom = -1.0 / 3600000
        eoq = -1.0 / 3600000
        eoy = -10.0 / 3600000
    elif a == "SONIA_DC":
        ois_trigger = 1
        batch_trigger = 1
        curncy = ql.GBPCurrency()
        base_ticker = 'UKBRBASE Index'
        fixing = "SONIO/N Index"
        fixing_tenor = ql.Period(1, ql.Days)
        bbg_curve = "YCSW0141 INDEX"
        bbgplot_curve_tickers = ['BPSWS', 'S0141FS', 'GPSF']
        ois_contrib = ['TRUK',15]
        ois_meet_hist = pd.read_pickle("./DataLake/SONIA_DC_OIS_MEETING_HIST.pkl")
        add_tenors = pd.DataFrame()
        sett_d = 0
        fixed_leg = ql.Period(1, ql.Years)
        fixed_acc = ql.Actual365Fixed()
        fixed_freq = ql.Annual
        floating_leg = ql.Period(1, ql.Years)
        floating_acc = ql.Actual365Fixed()
        custom_index_trigger = 0
        index = ql.Sonia
        index_a = ql.Sonia()
        calendar = ql.UnitedKingdom()
        fut_type = "none"
        eom = -0.25 / 3600000
        eoq = -0.25 / 3600000
        eoy = -0.25 / 3600000
    elif a == "AONIA_DC":
        ois_trigger = 1
        batch_trigger = 0
        curncy = ql.AUDCurrency()
        base_ticker = 'RBATCTR Index'
        fixing = "RBACOR Index"
        fixing_tenor = ql.Period(1, ql.Days)
        bbg_curve = "YCSW0159 INDEX"
        bbgplot_curve_tickers = ['ADSO', 'S0159FS', 'ADSF1A']
        ois_contrib = 'BLC'
        ois_meet_hist = pd.read_pickle("./DataLake/SOFR_DC_OIS_MEETING_HIST.pkl")
        add_tenors = pd.DataFrame()
        sett_d = 1
        fixed_leg = ql.Period(1, ql.Years)
        fixed_acc = ql.Actual365Fixed()
        fixed_freq = ql.Annual
        floating_leg = ql.Period(1, ql.Years)
        floating_acc = ql.Actual365Fixed()
        custom_index_trigger = 1
        index = ql.OvernightIndex(
            "AONIA", 1, ql.AUDCurrency(), ql.Australia(), ql.Actual365Fixed()
        )
        index_a = ql.OvernightIndex(
            "AONIA", 1, ql.AUDCurrency(), ql.Australia(), ql.Actual365Fixed()
        )
        calendar = ql.Australia()
        fut_type = "none"
        eom = -1.0 / 3600000
        eoq = -1.0 / 3600000
        eoy = -10.0 / 3600000
    elif a == "NZD_OIS_DC":
        ois_trigger = 1
        curncy = ql.NZDCurrency()
        fixing = "NZOCRS Index"
        fixing_tenor = ql.Period(1, ql.Days)
        bbg_curve = "YCSW0198 INDEX"
        add_tenors = pd.DataFrame()
        sett_d = 2
        fixed_leg = ql.Period(1, ql.Years)
        fixed_acc = ql.Actual365Fixed()
        fixed_freq = ql.Annual
        floating_leg = ql.Period(1, ql.Years)
        floating_acc = ql.Actual365Fixed()
        custom_index_trigger = 1
        index = ql.OvernightIndex(
            "NZD_OIS", 1, ql.NZDCurrency(), ql.NewZealand(), ql.Actual365Fixed()
        )
        index_a = ql.OvernightIndex(
            "NZD_OIS", 1, ql.NZDCurrency(), ql.NewZealand(), ql.Actual365Fixed()
        )
        calendar = ql.NewZealand()
        fut_type = "none"
        eom = -1.0 / 3600000
        eoq = -1.0 / 3600000
        eoy = -10.0 / 3600000
    elif a == "CAD_OIS_DC":
        ois_trigger = 1
        batch_trigger = 0
        curncy = ql.CADCurrency()
        base_ticker = 'CABROVER Index'
        fixing = "CAONREPO Index"
        fixing_tenor = ql.Period(1, ql.Days)
        bbg_curve = "YCSW0147 INDEX"
        bbgplot_curve_tickers = ['CDSO', 'S0147FS', 'CDSF']
        ois_contrib = 'BLC'
        ois_meet_hist = pd.read_pickle("./DataLake/SOFR_DC_OIS_MEETING_HIST.pkl")
        add_tenors = pd.DataFrame()
        add_tenors["value"] = [
            "CDSO7 Curncy",
            "CDSO10 Curncy",
            "CDSO12 Curncy",
            "CDSO15 Curncy",
            "CDSO20 Curncy",
            "CDSO25 Curncy",
            "CDSO30 Curncy",
        ]
        add_tenors["Tenor"] = ["7Y", "10Y", "12Y", "15Y", "20Y", "25Y", "30Y"]
        sett_d = 1
        fixed_leg = ql.Period(6, ql.Months)
        fixed_acc = ql.Actual365Fixed()
        fixed_freq = ql.Semiannual
        floating_leg = ql.Period(6, ql.Months)
        floating_acc = ql.Actual365Fixed()
        custom_index_trigger = 1
        index = ql.OvernightIndex(
            "CAD_OIS", 1, ql.CADCurrency(), ql.Canada(), ql.Actual365Fixed()
        )
        index_a = ql.OvernightIndex(
            "CAD_OIS", 1, ql.CADCurrency(), ql.Canada(), ql.Actual365Fixed()
        )
        calendar = ql.Canada()
        fut_type = "none"
        eom = -1.0 / 3600000
        eoq = -1.0 / 3600000
        eoy = -10.0 / 3600000
    elif a == "CHF_OIS_DC":
        ois_trigger = 1
        curncy = ql.CHFCurrency()
        fixing = "SRFXON3 Index"
        fixing_tenor = ql.Period(1, ql.Days)
        bbg_curve = "YCSW0234 INDEX"
        add_tenors = pd.DataFrame()
        sett_d = 2
        fixed_leg = ql.Period(1, ql.Years)
        fixed_acc = ql.Actual360()
        fixed_freq = ql.Annual
        floating_leg = ql.Period(1, ql.Years)
        floating_acc = ql.Actual360()
        custom_index_trigger = 1
        index = ql.OvernightIndex(
            "CHF_OIS", 1, ql.CHFCurrency(), ql.Switzerland(), ql.Actual360()
        )
        index_a = ql.OvernightIndex(
            "CHF_OIS", 1, ql.CHFCurrency(), ql.Switzerland(), ql.Actual360()
        )
        calendar = ql.Switzerland()
        fut_type = "none"
        eom = -1.0 / 3600000
        eoq = -1.0 / 3600000
        eoy = -10.0 / 3600000
    elif a == "SEK_OIS_DC":
        ois_trigger = 1
        curncy = ql.SEKCurrency()
        fixing = "STIB1D Index"
        fixing_tenor = ql.Period(1, ql.Days)
        bbg_curve = "YCSW0185 INDEX"
        add_tenors = pd.DataFrame()
        sett_d = 2
        fixed_leg = ql.Period(1, ql.Years)
        fixed_acc = ql.Actual360()
        fixed_freq = ql.Annual
        floating_leg = ql.Period(1, ql.Years)
        floating_acc = ql.Actual360()
        custom_index_trigger = 1
        index = ql.OvernightIndex(
            "SEK_OIS", 1, ql.SEKCurrency(), ql.Sweden(), ql.Actual360()
        )
        index_a = ql.OvernightIndex(
            "SEK_OIS", 1, ql.SEKCurrency(), ql.Sweden(), ql.Actual360()
        )
        calendar = ql.Sweden()
        fut_type = "none"
        eom = -1.0 / 3600000
        eoq = -1.0 / 3600000
        eoy = -10.0 / 3600000
    elif a == "TONAR_DC":
        ois_trigger = 1
        curncy = ql.JPYCurrency()
        fixing = "MUTKCALM Index"
        fixing_tenor = ql.Period(1, ql.Days)
        bbg_curve = "YCSW0195 INDEX"
        add_tenors = pd.DataFrame()
        sett_d = 2
        fixed_leg = ql.Period(1, ql.Years)
        fixed_acc = ql.Actual365Fixed()
        fixed_freq = ql.Annual
        floating_leg = ql.Period(1, ql.Years)
        floating_acc = ql.Actual365Fixed()
        custom_index_trigger = 1
        index = ql.OvernightIndex(
            "TONAR", 1, ql.JPYCurrency(), ql.Japan(), ql.Actual365Fixed()
        )
        index_a = ql.OvernightIndex(
            "TONAR", 1, ql.JPYCurrency(), ql.Japan(), ql.Actual365Fixed()
        )
        calendar = ql.Japan()
        fut_type = "none"
        eom = -1.0 / 3600000
        eoq = -1.0 / 3600000
        eoy = -10.0 / 3600000
    elif a == "RUONIA_DC":
        ois_trigger = 1
        curncy = ql.RUBCurrency()
        fixing = "RUONIA Index"
        fixing_tenor = ql.Period(1, ql.Days)
        bbg_curve = "YCSW0356 INDEX"
        add_tenors = pd.DataFrame()
        sett_d = 0
        fixed_leg = ql.Period(1, ql.Years)
        fixed_acc = ql.ActualActual(ql.ActualActual.ISDA)
        fixed_freq = ql.Annual
        floating_leg = ql.Period(1, ql.Years)
        floating_acc = ql.ActualActual(ql.ActualActual.ISDA)
        custom_index_trigger = 1
        index = ql.OvernightIndex(
            "RUONIA",
            sett_d,
            ql.RUBCurrency(),
            ql.Russia(),
            ql.ActualActual(ql.ActualActual.ISDA),
        )
        index_a = ql.OvernightIndex(
            "RUONIA",
            sett_d,
            ql.RUBCurrency(),
            ql.Russia(),
            ql.ActualActual(ql.ActualActual.ISDA),
        )
        calendar = ql.Russia()
        fut_type = "none"
        eom = -1.0 / 3600000
        eoq = -5.0 / 3600000
        eoy = -20.0 / 3600000
    elif a == "COP_OIS_DC":
        ois_trigger = 1
        curncy = ql.COPCurrency()
        fixing = "COOVIBR Index"
        fixing_tenor = ql.Period(1, ql.Days)
        bbg_curve = "YCSW0329 INDEX"
        add_tenors = pd.DataFrame()
        sett_d = 2
        fixed_leg = ql.Period(3, ql.Months)
        fixed_acc = ql.Actual360()
        fixed_freq = ql.Quarterly
        floating_leg = ql.Period(3, ql.Months)
        floating_acc = ql.Actual360()
        custom_index_trigger = 1
        index = ql.OvernightIndex(
            "COP_OIS",
            sett_d,
            ql.COPCurrency(),
            ql.UnitedStates(ql.UnitedStates.FederalReserve),
            ql.Actual360(),
        )
        index_a = ql.OvernightIndex(
            "COP_OIS",
            sett_d,
            ql.COPCurrency(),
            ql.UnitedStates(ql.UnitedStates.FederalReserve),
            ql.Actual360(),
        )
        calendar = ql.UnitedStates(ql.UnitedStates.FederalReserve)
        fut_type = "none"
        eom = -1.0 / 3600000
        eoq = -5.0 / 3600000
        eoy = -20.0 / 3600000

    class dict:
        def __init__(self):
            self.ois_trigger = ois_trigger
            self.batch_trigger = batch_trigger
            self.fixing = fixing
            self.fixing_tenor = fixing_tenor
            self.bbg_curve = bbg_curve
            self.bbgplot_tickers = bbgplot_curve_tickers
            self.add_tenors = add_tenors
            self.sett_d = sett_d
            self.index = index
            self.index_a = index_a
            self.fut_type = fut_type
            self.cal = calendar
            self.index_custom = custom_index_trigger
            self.curncy = curncy
            if ois_trigger == 1:
                self.eom = eom
                self.eoq = eoq
                self.eoy = eoy
                self.fixed = (fixed_leg, fixed_acc, fixed_freq)
                self.floating = (floating_leg, floating_acc)
                self.base_ticker = base_ticker
                self.contrib = ois_contrib
                self.ois_meet_hist = ois_meet_hist

            else:
                self.dc_index = dc_index
                self.fixed = (fixed_leg, fixed_acc, fixed_freq, fixed_dcc1, fixed_dcc2)
                self.floating = (floating_leg, floating_acc)
                self.add_conv_corr = add_conv_corr
                self.add_inst = add_inst
                self.start_swap = start_swap
    return dict()

## history
hist = dict([(key, []) for key in ['SOFR_DC', 'SONIA_DC', 'ESTER_DC', 'USD_3M','GBP_6M', 'EUR_6M']])
hist['SOFR_DC'] = pd.read_pickle("./DataLake/SOFR_H.pkl")
hist['SONIA_DC'] = pd.read_pickle("./DataLake/SONIA_H.pkl")
hist['ESTER_DC'] = pd.read_pickle("./DataLake/ESTER_H.pkl")
hist['USD_3M'] = pd.read_pickle("./DataLake/USD_3M_H.pkl")
hist['EUR_6M'] = pd.read_pickle("./DataLake/EUR_6M_H.pkl")
hist['GBP_6M'] = pd.read_pickle("./DataLake/GBP_6M_H.pkl")




## inflation curve conventions

def ccy_infl(a, eval_date):
    if a == "HICPxT":
        calendar = ql.TARGET()
        inf_index = "CPTFEMU Index"
        interpol = 0
        inf_index_hist = pd.read_pickle("./DataLake/HICPxT_hist.pkl")
        inf_index_hist["months"] = [
            ql.Date(
                inf_index_hist["months"][i].day,
                inf_index_hist["months"][i].month,
                inf_index_hist["months"][i].year,
            )
            for i in np.arange(len(inf_index_hist))
        ]

        seas = pd.DataFrame(columns=("months", "seas"))
        seas["months"] = [
            "Jan",
            "Feb",
            "Mar",
            "Apr",
            "May",
            "Jun",
            "Jul",
            "Aug",
            "Sep",
            "Oct",
            "Nov",
            "Dec",
        ]
        seas["seas"] = [
            -1.0726,
            0.2529,
            0.8436,
            0.3293,
            -0.0000,
            0.0397,
            -0.5115,
            0.1857,
            0.1042,
            0.0764,
            -0.4153,
            0.1677,
        ]
        base_month = (
            calendar.advance(eval_date, 2, ql.Days)
            - ql.Period("3M")
            - (calendar.advance(eval_date, 2, ql.Days) - ql.Period("3M")).dayOfMonth()
            + 1
        )

        inf_swap_ticker_temp = ["EUSWI"]
        inf_swap_ticker = [
            inf_swap_ticker_temp[0] + str(i) + " Curncy"
            for i in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 15, 20, 25, 30, 40]
        ]
        fix_t1 = "EUSWIF"
        fix_t2 = " INFA Curncy"
        last_month_dt = con.ref(inf_index, "LAST_UPDATE_DT")["value"][0]
        last_month_fix = ql.Date(1, last_month_dt.month, last_month_dt.year)
        currency = "EUR"
        dc_curve = "ESTER_DC"

    if a == "FRCPI":
        calendar = ql.TARGET()
        inf_index = "FRCPXTOB Index"
        interpol = 1
        inf_index_hist = pd.read_pickle("./DataLake/FRCPI_hist.pkl")
        inf_index_hist["months"] = [
            ql.Date(
                inf_index_hist["months"][i].day,
                inf_index_hist["months"][i].month,
                inf_index_hist["months"][i].year,
            )
            for i in np.arange(len(inf_index_hist))
        ]

        seas = pd.DataFrame(columns=("months", "seas"))
        seas["months"] = [
            "Jan",
            "Feb",
            "Mar",
            "Apr",
            "May",
            "Jun",
            "Jul",
            "Aug",
            "Sep",
            "Oct",
            "Nov",
            "Dec",
        ]
        seas["seas"] = [
            -0.5104,
            0.2717,
            0.3759,
            0.0926,
            0.0555,
            0.0183,
            -0.1692,
            0.524,
            -0.658,
            -0.0468,
            -0.1451,
            0.1916,
        ]
        base_month = (
            calendar.advance(eval_date, 2, ql.Days)
            - ql.Period("3M")
            - (calendar.advance(eval_date, 2, ql.Days) - ql.Period("3M")).dayOfMonth()
            + 1
        )

        inf_swap_ticker_temp = ["FRSWI"]
        inf_swap_ticker = [
            inf_swap_ticker_temp[0] + str(i) + " Curncy"
            for i in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 15, 20, 25, 30, 40]
        ]
        fix_t1 = "none"
        fix_t2 = " none"
        last_month_dt = con.ref(inf_index, "LAST_UPDATE_DT")["value"][0]
        last_month_fix = ql.Date(1, last_month_dt.month, last_month_dt.year)
        currency = "EUR"
        dc_curve = "ESTER_DC"

    if a == "UKRPI":
        #        eval_date = ql.Date(datetime.datetime.now().day,datetime.datetime.now().month,datetime.datetime.now().year)-1
        calendar = ql.UnitedKingdom()
        inf_index = "UKRPI Index"
        interpol = 0
        inf_index_hist = pd.read_pickle("./DataLake/UKRPI_hist.pkl")
        inf_index_hist["months"] = [
            ql.Date(
                inf_index_hist["months"][i].day,
                inf_index_hist["months"][i].month,
                inf_index_hist["months"][i].year,
            )
            for i in np.arange(len(inf_index_hist))
        ]

        seas = pd.DataFrame(columns=("months", "seas"))
        seas["months"] = [
            "Jan",
            "Feb",
            "Mar",
            "Apr",
            "May",
            "Jun",
            "Jul",
            "Aug",
            "Sep",
            "Oct",
            "Nov",
            "Dec",
        ]
        seas["seas"] = [
            -0.7993,
            0.442,
            0.0323,
            0.317,
            0.0696,
            -0.0384,
            -0.2223,
            0.312,
            -0.1348,
            -0.1531,
            -0.1182,
            0.3086,
        ]
        base_month = (
            calendar.advance(eval_date, 2, ql.Days)
            - ql.Period("2M")
            - (calendar.advance(eval_date, 2, ql.Days) - ql.Period("2M")).dayOfMonth()
            + 1
        )

        inf_swap_ticker_temp = ["BPSWIT"]
        inf_swap_ticker = [
            inf_swap_ticker_temp[0] + str(i) + " Curncy"
            for i in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 15, 20, 25, 30, 40, 50]
        ]
        fix_t1 = "BPSWIF"
        fix_t2 = " INFA Curncy"
        last_month_dt = con.ref(inf_index, "LAST_UPDATE_DT")["value"][0]
        last_month_fix = ql.Date(1, last_month_dt.month, last_month_dt.year)
        currency = "GBP"
        dc_curve = "SONIA_DC"

    if a == "USCPI":
        eval_date = ql.Date(
            datetime.datetime.now().day,
            datetime.datetime.now().month,
            datetime.datetime.now().year,
        )
        calendar = ql.UnitedStates(ql.UnitedStates.FederalReserve)
        inf_index = "CPURNSA Index"
        interpol = 0
        inf_index_hist = pd.read_pickle("./DataLake/USCPI_hist.pkl")
        inf_index_hist["months"] = [
            ql.Date(
                inf_index_hist["months"][i].day,
                inf_index_hist["months"][i].month,
                inf_index_hist["months"][i].year,
            )
            for i in np.arange(len(inf_index_hist))
        ]

        seas = pd.DataFrame(columns=("months", "seas"))
        seas["months"] = [
            "Jan",
            "Feb",
            "Mar",
            "Apr",
            "May",
            "Jun",
            "Jul",
            "Aug",
            "Sep",
            "Oct",
            "Nov",
            "Dec",
        ]
        seas["seas"] = [
            0.1678,
            0.2013,
            0.2419,
            0.1494,
            0.0625,
            -0.0111,
            -0.0754,
            -0.0286,
            -0.0413,
            -0.1732,
            -0.2769,
            -0.2164,
        ]
        base_month = (
            calendar.advance(eval_date, 2, ql.Days)
            - ql.Period("3M")
            - (calendar.advance(eval_date, 2, ql.Days) - ql.Period("3M")).dayOfMonth()
            + 1
        )

        inf_swap_ticker_temp = ["USSWIT"]
        inf_swap_ticker = [
            inf_swap_ticker_temp[0] + str(i) + " Curncy"
            for i in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 15, 20, 25, 30]
        ]
        fix_t1 = "none"
        fix_t2 = " XTRA Curncy"
        last_month_dt = con.ref(inf_index, "LAST_UPDATE_DT")["value"][0]
        last_month_fix = ql.Date(1, last_month_dt.month, last_month_dt.year)
        currency = "USD"
        dc_curve = "SOFR_DC"

    if a == "CACPI":
        eval_date = ql.Date(
            datetime.datetime.now().day,
            datetime.datetime.now().month,
            datetime.datetime.now().year,
        )
        calendar = ql.Canada()
        inf_index = "CACPI Index"
        interpol = 0
        inf_index_hist = pd.read_pickle("./DataLake/CACPI_hist.pkl")
        inf_index_hist["months"] = [
            ql.Date(
                inf_index_hist["months"][i].day,
                inf_index_hist["months"][i].month,
                inf_index_hist["months"][i].year,
            )
            for i in np.arange(len(inf_index_hist))
        ]

        seas = pd.DataFrame(columns=("months", "seas"))
        seas["months"] = [
            "Jan",
            "Feb",
            "Mar",
            "Apr",
            "May",
            "Jun",
            "Jul",
            "Aug",
            "Sep",
            "Oct",
            "Nov",
            "Dec",
        ]
        seas["seas"] = [
            0.1678,
            0.2013,
            0.2419,
            0.1494,
            0.0625,
            -0.0111,
            -0.0754,
            -0.0286,
            -0.0413,
            -0.1732,
            -0.2769,
            -0.2164,
        ]
        base_month = (
            calendar.advance(eval_date, 2, ql.Days)
            - ql.Period("2M")
            - (calendar.advance(eval_date, 2, ql.Days) - ql.Period("2M")).dayOfMonth()
            + 1
        )

        inf_swap_ticker_temp = ["CDSWIT"]
        inf_swap_ticker = [
            inf_swap_ticker_temp[0] + str(i) + " BLC Curncy"
            for i in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 15, 20, 25, 30]
        ]
        fix_t1 = "none"
        fix_t2 = " none"
        last_month_dt = con.ref(inf_index, "LAST_UPDATE_DT")["value"][0]
        last_month_fix = ql.Date(1, last_month_dt.month, last_month_dt.year)
        currency = "CAD"
        dc_curve = "CAD_OIS_DC"

    class ccy_infl_output:
        def __init__(self):
            self.fixing_hist = inf_index_hist
            self.seas = seas
            self.cal = calendar
            self.index = inf_index
            self.interp = interpol
            self.base_month = base_month
            self.ticker = inf_swap_ticker
            self.fix_ticker = (fix_t1, fix_t2)
            self.last_fix_month = last_month_fix
            self.ccy = currency
            self.dc_curve = dc_curve

    return ccy_infl_output()
