##### Conditioning 


ff = con.bdh('FDTR Index' , 'PX_LAST', '19800101', '20230130', longdata = True)

dt1 = ['19800605','19840221','19880828','19940809','19991117','20060130','20180624']    ##### 6months before last hike 

dt1a = [ql.Date( int(i[-2:]), int(i[-4:-2]), int(i[:4])) for i in dt1]

cal = ql.UnitedStates()
dt1b = [cal.advance(i, ql.Period(6, ql.Months)) for i in dt1a ]

dt2 = [ bbg_date_str(i, ql_date = 1) for i in dt1b]

inst = ['FDTR Index','SPX Index', 'DXY Index', 'GT2 Govt', 'GT5 Govt', 'GT10 Govt','GT30 Govt']

i = 0
df1 = con.bdh(inst , 'PX_LAST', dt2[i], dt2[i], longdata = True)['value'] - con.bdh(inst , 'PX_LAST', dt1[i], dt1[i], longdata = True)['value']



plf = con.bdh('OUTFGAF Index' , 'PX_LAST', '19650101', '20230130', longdata = True)
cpi = con.bdh('CPI YOY Index' , 'PX_LAST', '19650101', '20230130', longdata = True)


plf['filter'] = [min( plf['value'][i], 4) for i in np.arange(len(plf))]

f2 = plf[plf['filter'] < 4]
f3 = cpi[[cpi['date'][i] in list(f2['date']) for i in np.arange(len(cpi))]]

f3['value'].mean()
f3['value'].median()

plt.hist(f3['value'][:-1], f3['value'], weights=counts)

counts, bins = np.histogram(f3['value'])
plt.bar(counts, bins)
plt.hist(bins[:-1], bins, weights=counts)


f4 = plf.loc[list(f2.index+12)[:-13]]
f5 = np.array(f4['value']) - np.array(f2[:-13]['value'])
counts, bins = np.histogram(f5)
plt.hist(bins[:-1], bins, weights=counts)
f5.mean()
np.median(f5)


f6 = cpi.loc[list(f3.index+12)[:-13]]
f7 = np.array(f6['value']) - np.array(f3[:-13]['value'])
counts, bins = np.histogram(f7)
plt.hist(bins[:-1], bins, weights=counts)
f7.mean()
np.median(f7)


f2[200:]

i1 = [22, 79, 146, 163, 172, 269, 365, 392, 486, 519,]
i2 = np.array(i1)+12

f4 = plf.loc[i2]
f5 = np.array(f4['value']) - np.array(plf.loc[i1]['value'])
counts, bins = np.histogram(f5)
plt.hist(bins[:-1], bins, weights=counts)
f5.mean()
np.median(f5)

f6 = cpi.loc[i2]
f7 = np.array(f6['value']) - np.array(cpi.loc[i1]['value'])
counts, bins = np.histogram(f7)
plt.hist(bins[:-1], bins, weights=counts)
f7.mean()
np.median(f7)





#######################################################################################
#### housing

mhs = con.bdh('BIUSMUNS Index' , 'PX_LAST', '19700101', '20230228', longdata = True)
mhs['year'] = [mhs['date'][i].year for i in np.arange(len(mhs))]
d1 = mhs.groupby(['year']).sum() 

mh_rent = con.bdh('NHSPSMRT Index' , 'PX_LAST', '19700101', '20230228', longdata = True)
mh_rent.index = mh_rent['date']
mh_rent['year'] = [mh_rent['date'][i].year for i in np.arange(len(mh_rent))]
d2 = mh_rent.groupby(['year']).sum() 
#mh_rent = mh_rent.resample('Y').last()
mh_rent['date'] = [mh_rent['date'][i].year for i in np.arange(len(mh_rent))]

mh_sales = con.bdh('NHSPSMSS Index' , 'PX_LAST', '19700101', '20230228', longdata = True)
mh_sales.index = mh_sales['date']
mh_sales['year'] = [mh_sales['date'][i].year for i in np.arange(len(mh_sales))]
d3 = mh_sales.groupby(['year']).sum() 
#mh_sales = mh_sales.resample('Y').last()
mh_sales['date'] = [mh_sales['date'][i].year for i in np.arange(len(mh_sales))]


p2 = plt.bar(pd.to_datetime(d1.index, format='%Y'),d1['value'], facecolor='lightgreen', alpha=0.75)
p1 = plt.plot(mh_rent['date'], mh_rent['value'], c='blue', alpha=0.75)
plt.show()

p1.show
plt.show()

fig, axs = plt.subplots(1, 1, figsize=(10, 8))
ax1 = plt.subplot(1, 1, 1)
#ax1.set_title('Curve', fontdict={'fontsize':9})
ax1.bar(d1.index, d1['value'], facecolor='lightgreen', alpha=0.75, label='MFH Starts')
ax1.xaxis.set_tick_params(labelsize=10)
ax1.yaxis.set_tick_params(labelsize=10)

ax2 = ax1.twinx()
ax2.plot(d2.index, d2['value'], c='blue', alpha=0.75, label='MFH: For Rents')
ax2.plot(d3.index, d3['value'], c='darkblue', alpha=0.75, label='MFH: For Sales')
ax2.legend(loc='upper left')
ax1.legend(loc='lower left')
plt.show()
#ax2 = ax1.twinx()
#ax2.plot(mh_rent['date'], mh_rent['value'], c='blue', alpha=0.75, label='MFH: For Rents')
#ax2.plot(mh_sales['date'], mh_sales['value'], c='darkblue', alpha=0.75, label='MFH: For Sales')
#ax2.legend(loc='upper left')
#ax1.legend(loc='lower left')



mh_rent

pd.to_datetime(d1.index, format='%Y')[0]
mh_rent['date'][0]