



def get_wirp(a, d1):
#    a = 'SOFR_DC'
#    d1 = datetime.date(2024, 2, 7)
    d2 = datetime_to_ql(d1)

    today = ql.Date(datetime.datetime.now().day, datetime.datetime.now().month, datetime.datetime.now().year)
    c = ccy(a, d2)

    ticker = c.bbgplot_tickers[2]
    contrib = c.contrib
    base_ticker = c.base_ticker


    ### Get bbg tickers
    t_list = [ticker+str(i)+' '+contrib+' Curncy' for i in range(1,16) ]
    df1 = con.bdh(t_list, 'PX_LAST', bbg_date_str(d2), bbg_date_str(d2), longdata=True)
    df1.ticker = df1.ticker.astype("category")
    df1.ticker = df1.ticker.cat.set_categories(t_list)
    df1 = df1.sort_values(["ticker"])
    df1.reset_index(inplace=True, drop=True)

    ### Get FOMC Dates and set index
    if d2 == today:
        x = con.bulkref(base_ticker,'ECO_FUTURE_RELEASE_DATE_LIST')['value']
        y = pd.Series([ pd.datetime(int(x[i][0:4]),int(x[i][5:7]),int(x[i][8:10])) for i in range(len(x)) ])
        y = pd.DataFrame(y[y > (pd.datetime.now()+pd.DateOffset(days=-1))], columns = ['Meets'])
        y1 = y['Meets'].append( pd.Series( [   y[-1:]['Meets'].values[0]+np.timedelta64(50*i,'D') for i in range(1, len(t_list)-len(y)+1 )] ) )
        y2 = pd.DataFrame(y1)
        meet_index = pd.Series( [y2.iloc[i,][0].strftime('%b') +'-'+ y2.iloc[i,][0].strftime('%y') for i in range(len((y2))) ] )
        df1['meet_date'] = meet_index
    else:
        df1['meet_date'] = np.arange(1,len(df1)+1)

    ois_fix = con.bdh(c.fixing, 'PX_LAST', bbg_date_str(c.cal.advance(d2, ql.Period('-2D'))), bbg_date_str(c.cal.advance(d2, ql.Period('-2D'))), longdata=True)['value'][0]
    base_fix = con.bdh(base_ticker, 'PX_LAST', bbg_date_str(c.cal.advance(d2, ql.Period('-2D'))), bbg_date_str(c.cal.advance(d2, ql.Period('-2D'))), longdata=True)['value'][0]
    basis = base_fix - ois_fix

    df1['cb'] = np.round(df1['value']+basis,2)
    df1['step'] = 100*np.array([df1['cb'][0]-base_fix] +df1['cb'].diff()[1:].tolist())
    df1['cum'] = df1['step'].cumsum()

    return df1



con.bulkref('FDTR Index','ECO_FUTURE_RELEASE_DATE_LIST', ovrds=[("START_DT","20200101"), ("END_DT","20251214")])
