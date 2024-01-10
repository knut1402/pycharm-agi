#### NFP 
import datetime
year = datetime.datetime.today().year


d1 = con.bdh(t1[-1] , 'PX_LAST', '19200101', '20230115', longdata = True)
d1['year'] = [d1['date'][i].year for i in np.arange(len(d1))]

d2 = d1.groupby(by="year")["value"].sum()

d3 = con.bdh('OEUSQWBV Index' , 'PX_LAST', '19200101', '20230115', longdata = True)

d3.index = d3['date']
d3 = d3.resample('Y').last()
d3['year'] = [d3['date'][i].year for i in np.arange(len(d3))]
d3.index = d3['year']

new_row = pd.DataFrame({'date':'1939-12-31', 'ticker':'OEUSQWBV Index', 'field':'PX_LAST', 'value':53300.0, 'year': 1939}, index=[1939])
d3 = pd.concat([new_row,d3.loc[:]])

d2 = pd.DataFrame(d2)
d2.columns = ['# Chg in NFP']

d4 = d2.merge(d3, how='outer', left_index=True, right_index=True)
d5 = d4.interpolate(method='linear', axis=0).ffill().bfill()

d6 = pd.DataFrame([ 100*(d2.iloc[i][0] / d5.iloc[i]['value']) for i in np.arange(len(d2))])
d6.index= d2.index
d6.columns = ['Chg in NFP as a % of Active force']

d6.plot.bar(figsize=[14,10])


f1 = d6.index[d6['Chg in NFP as a % of Active force'] < 0] - 1
d6.loc[f1].sum()
d6.loc[f1].mean()


fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(16, 10))
d2.plot(ax=axes[0], kind='bar')
d6.plot(ax=axes[1], kind='bar');


####################### 

d1[-50:]
d1['value'][500:].plot.bar()

d1[d1['value'] < 0][-50:]

###### manually establish start of job losses
i2 = [51, 146, 209, 246, 367, 426, 494, 617, 675, 736, 821, 973]

d7 = pd.DataFrame([np.sum(d1.iloc[(i2[i]-12):i2[i]]['value']) for i in np.arange(len(i2))])

d7['year'] = [d1.iloc[i2]['date'][i].year for i in i2]
d7['active'] = [d5[d5['year'] == d7['year'][i]]['value'].iloc[0] for i in np.arange(len(d7))]
d7['chg'] = 100*d7[0]/d7['active']
d7.index = d7['year']
d7['chg'].plot.bar()
d7['chg'].mean()



