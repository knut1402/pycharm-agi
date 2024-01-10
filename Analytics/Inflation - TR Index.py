
latest = '20231130'
bench = 'LF94TRUU Index'

raw_df = con.bulkref(bench, 'INDX_MWEIGHT_PX')

uniq_mem = np.unique(raw_df['position'])

df_b = pd.DataFrame()
df_b['cusip'] = raw_df[raw_df['name'] == 'Index Member']['value'].tolist()
df_b['weight'] = raw_df[raw_df['name'] == 'Percent Weight']['value'].tolist()
df_b['outst'] = raw_df[raw_df['name'] == 'Actual Weight']['value'].tolist()
df_b['px_base'] = raw_df[raw_df['name'] == 'Current Price']['value'].tolist()

att = ['COUNTRY', 'PX_LAST', 'SECURITY_DES', 'MATURITY', 'CPN', 'REFERENCE_INDEX','SETTLE_DT', 'DAYS_TO_SETTLE', 'PX_YEST_CLOSE']

country = []
des = []
cpn = []
maturity = []
px_last = []
px_close = []
ref_index = []
settle_date = []
dts = []

for i in np.arange(len(df_b)):
    print(i)
    a1 = con.ref(df_b['cusip'][i] + ' Govt', ['COUNTRY', 'PX_LAST', 'SECURITY_DES', 'MATURITY', 'CPN', 'REFERENCE_INDEX', 'SETTLE_DT', 'DAYS_TO_SETTLE','PX_YEST_CLOSE'])
    country += a1[a1['field'] == 'COUNTRY']['value'].tolist()
    des += a1[a1['field'] == 'SECURITY_DES']['value'].tolist()
    maturity += a1[a1['field'] == 'MATURITY']['value'].tolist()
    cpn += a1[a1['field'] == 'CPN']['value'].tolist()
    px_last += a1[a1['field'] == 'PX_LAST']['value'].tolist()
    px_close += a1[a1['field'] == 'PX_YEST_CLOSE']['value'].tolist()
    ref_index += a1[a1['field'] == 'REFERENCE_INDEX']['value'].tolist()
    settle_date += a1[a1['field'] == 'SETTLE_DT']['value'].tolist()
    dts += a1[a1['field'] == 'DAYS_TO_SETTLE']['value'].tolist()


df_b['country'] = country
df_b['des'] = des
df_b['cpn'] = cpn
df_b['maturity'] = maturity
df_b['px_last'] = px_last
df_b['px_close'] = px_close
df_b['ref_index'] = ref_index
df_b['settle_dt'] = settle_date
df_b['dts'] = dts



df_b['country'].value_counts()
df_b.groupby(ref_index).sum()




[con.ref( df_b['cusip'][0]+' Govt' , ['COUNTRY','PX_LAST','SECURITY_DES', 'MATURITY', 'CPN', 'REFERENCE_INDEX','SETTLE_DT', 'DAYS_TO_SETTLE', 'PX_YEST_CLOSE'])['value'][0] for i in np.arange(len(df_b))]
[con.bdh( df_b['cusip'][i]+' Govt' , ['PX_LAST'], '20231130', '20231130', longdata=True)['value'][0] for i in np.arange(len(df_b))]
df_b['cusip']
[df_b['cusip'][i]+' Govt' for i in np.arange(len(df_b))]