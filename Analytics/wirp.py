#### WIRP

curve = 'US'
method = '0'
inst = 'B'
datatype = 'FR'




x = con.bulkref('FDTR Index','ECO_FUTURE_RELEASE_DATE_LIST')['value']
y = pd.Series([ datetime.datetime(int(x[i][0:4]),int(x[i][5:7]),int(x[i][8:10])) for i in range(len(x)) ])
y = pd.DataFrame(y[y > (datetime.datetime.now()+pd.DateOffset(days=-1))], columns = ['Meets'])
y.reset_index(inplace=True, drop = True)

#y['Meets'][13].strftime("%b").upper()+y['Meets'][13].strftime("%Y")+' Index'

y1 = [curve+method+inst+datatype+' '+y['Meets'][i].strftime("%b").upper()+y['Meets'][i].strftime("%Y")+' Index' for i in np.arange(len(y)) ]

con.bdh(y1,'PX_LAST','20220810','20220810', longdata = True)

con.ref(y1[0], 'PX_LAST')['value'][0]


datetime.datetime.now().strftime("%b").upper()+datetime.datetime.now().strftime("%Y")


datetime.datetime.now()+datetime.timedelta(30).strftime("%b%Y")

datetime.datetime.now.AddMonths(1)


datetime.datetime.now().AddMonths(1)

relativedelta(months=3)

datetime.timedelta(3*365/12)