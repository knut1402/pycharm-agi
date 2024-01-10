

#### dates!!
start = ql.Date(1,1,2023)
latest = ql.Date(19,7,2023)
start_bbg = bbg_date_str(start)
latest_bbg = bbg_date_str(latest)


at = dict()
at['GDP'] = 'GDGCAFJP Index'
at['PCE'] = 'GDGCAKRA Index'
at['Res Inv'] = 'GDGCBJOI Index'
at['Non-Res Inv'] = 'GDGCBGFT Index'
at['Inv'] = 'GDGCCVDD Index'
at['Govt'] = 'GDGCBMQC Index'
at['Net Exp'] = 'GDGCCRRB Index'

at.keys()


con.bdh("GDGCCVDD Index" , 'PX_LAST', start_bbg, latest_bbg, longdata = True)
