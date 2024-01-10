## 1. usd ois from jpm data query

df1 = pd.read_excel('./DataLake/citi_gbp_raw.xlsx', sheet_name = "gbp_sonia_citi_raw")
#df_gbp = df_gbp[-100:]
#df_gbp.reset_index(inplace=True, drop=True)


create_batch_ois(df1, 'SONIA_DC', 'SONIA_H')

def create_batch_ois(df, a, batch_name):
#    df = df
#    a = 'SONIA_DC'

    today = ql.Date(datetime.datetime.now().day, datetime.datetime.now().month, datetime.datetime.now().year)
    c = ccy(a, today)
    TU_Dict = {'D': 0, 'W': 1, 'M': 2, 'Y': 3}

    db = pd.DataFrame()
    db.index = df['Date']

    r_index = []
    r_ref_date = []
    r_dates = []
    r_rates = []
    r_fixing = []
    r_tab = []
    r_swap_rates = []

    for i in np.arange(len(df)):
        b= df['Date'][i]
        print(b)
#        ref_date = ql.Date(int(b.split('/')[0]), int(b.split('/')[1]), int(b.split('/')[2]))
        ref_date = datetime_to_ql(b)
        ref_date_1 = c.cal.advance(ref_date, -1, ql.Days)
        ql.Settings.instance().evaluationDate = ref_date

    #### get o/n ois fixing
        OIS_ON = df['1d'][i]
        deposits = {(0, 1, ql.Days): OIS_ON}
        for sett_num, n, unit in deposits.keys():
            deposits[(sett_num, n, unit)] = ql.SimpleQuote(
                deposits[(sett_num, n, unit)] / 100.0)

        helpers = [ ql.DepositRateHelper(
            ql.QuoteHandle(deposits[(sett_num, n, unit)]),
            ql.Period(n, unit),
            c.sett_d,
            c.cal,
            ql.Following,
            False,
            c.floating[1],
        )
            for sett_num, n, unit in deposits.keys()]

        OIS_DC = c.index_a

    #### get ois swap rates
        x1 = pd.DataFrame()
        x1['Tenor'] = [df.columns[k].upper() for k in np.arange(2,len(df.columns))]
        x1['Rate'] = [df.iloc[i,j] for j in np.arange(2,len(df.columns))]
        x1.dropna(inplace=True)
        x1.reset_index(inplace=True, drop = True)

        x1['TenorNum'] = pd.Series([int(x1['Tenor'][i][0:-1]) for i in range(len(x1))])
        x1['TenorUnit'] = pd.Series(dtype=float)
        x1['TenorUnit'] = [TU_Dict[x1['Tenor'].tolist()[i][-1]] for i in range(len(x1))]
        x1['List'] = [(x1['Rate'][i], (int(x1['TenorNum'][i]), int(x1['TenorUnit'][i]))) for i in range(len(x1))]
        L1 = x1['List'].tolist()

        helpers += [ql.OISRateHelper(c.sett_d, ql.Period(*tenor),
                                     ql.QuoteHandle(ql.SimpleQuote(rate / 100)), OIS_DC)
                    for rate, tenor in L1]

    # build curve
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

    db['Ref_Date'] = r_ref_date
    db['Dates'] = r_dates
    db['Rates'] = r_rates
    db['Swap_Rates'] = r_swap_rates
    db['Index'] = r_index
    db['Fixing'] = r_fixing
    db['Table'] = r_tab
    db.to_pickle('./DataLake/'+batch_name+'.pkl')

    return



sonia_h = pd.read_pickle("./DataLake/SONIA_H.pkl")

