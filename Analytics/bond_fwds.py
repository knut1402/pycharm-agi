###### analysing b/e bond fwds
import numpy as np
import pandas as pd

disp = pd.DataFrame()
ret = pd.DataFrame()

disp_y = pd.DataFrame()
ret_y = pd.DataFrame()


bonds = ['US912810TT51 Govt']

#US91282CHT18
#US91282CJC64

df_static = dict([(key, []) for key in bonds ])
[df_static[i].append(con.ref(i, ['ID_ISIN','CRNCY','PX_DIRTY_CLEAN','MATURITY','CPN','CPN_FREQ','DAYS_ACC','DAYS_TO_NEXT_COUPON', 'SETTLE_DT','PX_CLOSE_DT','DAYS_TO_SETTLE','BASE_CPI','ISSUE_DT'])) for i in bonds]

today = ql.Date(datetime.datetime.now().day, datetime.datetime.now().month, datetime.datetime.now().year)
cal = ql.UnitedStates(ql.UnitedStates.FederalReserve)

###### get dates
d1 = [0,'1y']
d1_a = []
for j in np.arange(len(d1)):
    if isinstance(d1[j],int) == True:
        d1_a.append(cal.advance(today,d1[j],ql.Days))
    elif isinstance(d1[j],str) == True:
        try:
            d1_a.append( ql.Date(int(d1[j].split('-')[0]),int(d1[j].split('-')[1]),int(d1[j].split('-')[2])) )
        except:
            if d1[j][-1] in ('D','d'):
                unit = ql.Days
            elif d1[j][-1] in ('W','w'):
                unit = ql.Weeks
            elif d1[j][-1] in ('M','m'):
                unit = ql.Months
            elif d1[j][-1] in ('Y', 'y'):
                unit = ql.Years
            if j > 0:
                d1_a.append(cal.advance( d1_a[0] , int(d1[j][0:-1]), unit) )
            else:
                d1_a.append(cal.advance( today , int(d1[j][0:-1]), unit) )

d1_b = [bbg_date_str(d1_a[i] , ql_date=1) for i in np.arange(len(d1)) ]
settle_dt = [cal.advance(d1_a[i],  1, ql.Days) for i in np.arange(len(d1)) ]

###### price


px = [con.bdh( bonds[j], ['PX_LAST'], d1_b[0], d1_b[0], longdata=True)['value'].tolist()[0] for j in np.arange(len(bonds))]

yields = [con.ref( bonds[j], ['YLD_YTM_BID'],
                  ovrds=[('PX_BID', px[j]), (('SETTLE_DT', bbg_date_str(settle_dt[0], ql_date=1)))])['value'][0] for j in np.arange(len(bonds))]

###### working out dirty price
coupon = df_static[bonds[0]][0][df_static[bonds[0]][0]['field'] == 'CPN']['value'].tolist()[0]
coup_feq = 1/df_static[bonds[0]][0][df_static[bonds[0]][0]['field'] == 'CPN_FREQ']['value'].tolist()[0]
day_acc = df_static[bonds[0]][0][df_static[bonds[0]][0]['field'] == 'DAYS_ACC']['value'].tolist()[0]
days_per = (df_static[bonds[0]][0][df_static[bonds[0]][0]['field'] == 'DAYS_ACC']['value'].tolist()[0] + df_static[bonds[0]][0][df_static[bonds[0]][0]['field'] == 'DAYS_TO_NEXT_COUPON']['value'].tolist()[0])

accrual = coupon*coup_feq*(day_acc/days_per)
dp = px[0] + accrual


###### fwd dirty price
fwd_dp = dp
fwd_cp = fwd_dp - accrual - (coupon)

be_yield = con.ref( bonds[0] , ['YLD_YTM_BID'], ovrds =[('PX_BID', fwd_cp ),(('SETTLE_DT',  bbg_date_str(  settle_dt[1] , ql_date=1)  ))])['value'][0]



####### returns
shifts = [-200,-150,-100,-50,0,50,100,150,200]
y_shifts = [yields[0]+(0.01*shifts[i]) for i in np.arange(len(shifts))]

px_shifts = [con.ref( bonds[0] , ['YAS_BOND_PX'], ovrds =[('YAS_BOND_YLD', yields[0]+(0.01*shifts[i]) ),(('SETTLE_DT',  bbg_date_str(  settle_dt[1] , ql_date=1)  ))])['value'][0] for i in np.arange(len(shifts))]
dp_px_shifts = np.array(px_shifts)+accrual

px_perf = 100*(dp_px_shifts - dp + coupon)/dp


######## RETURNS AT YIELDS = X
yield_sim = [2.5, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 6.5]

px_shifts = [con.ref( bonds[0] , ['YAS_BOND_PX'], ovrds =[('YAS_BOND_YLD', yield_sim[i] ),(('SETTLE_DT',  bbg_date_str(  settle_dt[1] , ql_date=1)  ))])['value'][0] for i in np.arange(len(yield_sim))]
dp_px_shifts = np.array(px_shifts)+accrual

px_perf = 100*(dp_px_shifts - dp + coupon)/dp











###### add to db
m = '30y'
disp_y[m] = yield_sim+[be_yield]
ret_y[m] = px_perf.tolist()+[0.0]






fig, ax1 = plt.subplots(figsize=(10,8))
ax1.plot(disp['2y'],ret['2y'], label ='US: 2y')
ax1.plot(disp['3y'],ret['3y'], label ='US: 3y')
ax1.plot(disp['10y'],ret['10y'], label ='US: 10y')
ax1.scatter(disp['30y'],ret['30y'], label ='US: 30y', s = 6, c = 'red')
ax1.axhline(y= 0, color = 'black', lw = 0.5, ls = '-.')
ax1.axvline(x= 0, color = 'black', lw = 0.5, ls = '-.')
ax1.set_ylabel("1Y PX Return (%)", color="black", fontsize=10)
ax1.set_xlabel("Change in Yield (bps)", color="black", fontsize=10)
plt.legend(loc = 'upper right')
#plt.title('China Credit Impulse', color = 'darkblue')
#plt.annotate('Source: Bloomberg', (0,0), (0,-20), fontsize=6, xycoords='axes fraction', textcoords='offset points', va='top', style='italic')
plt.show()







fig, ax1 = plt.subplots(figsize=(10,8))
ax1.plot(disp_y['2y'],ret_y['2y'], label ='US: 2y')
ax1.plot(disp_y['3y'],ret_y['3y'], label ='US: 3y')
ax1.plot(disp_y['10y'],ret_y['10y'], label ='US: 10y')
ax1.scatter(disp_y['30y'],ret_y['30y'], label ='US: 30y', s = 6, c = 'red')
ax1.axhline(y= 0, color = 'black', lw = 0.5, ls = '-.')
#ax1.axvline(x= 0, color = 'black', lw = 0.5, ls = '-.')
ax1.set_ylabel("1Y PX Return (%)", color="black", fontsize=10)
ax1.set_xlabel("Yield (%)", color="black", fontsize=10)
plt.legend(loc = 'upper right')
#plt.title('China Credit Impulse', color = 'darkblue')
#plt.annotate('Source: Bloomberg', (0,0), (0,-20), fontsize=6, xycoords='axes fraction', textcoords='offset points', va='top', style='italic')
plt.show()


fig, ax1  = plt.subplots(1,2,figsize=(12,10))
ax1[0].plot(disp['2y'],ret['2y'], label ='US: 2y')
ax1[0].plot(disp['3y'],ret['3y'], label ='US: 3y')
ax1[0].plot(disp['10y'],ret['10y'], label ='US: 10y')
ax1[0].scatter(disp['30y'],ret['30y'], label ='US: 30y', s = 6, c = 'red')
ax1[0].axhline(y= 0, color = 'black', lw = 0.5, ls = '-.')
ax1[0].axvline(x= 0, color = 'black', lw = 0.5, ls = '-.')
ax1[0].set_ylabel("1Y PX Return (%)", color="black", fontsize=10)
ax1[0].set_xlabel("Change in Yield (bps)", color="black", fontsize=10)
ax1[0].legend(loc = 'upper right')
ax1[1].plot(disp_y['2y'],ret_y['2y'], label ='US: 2y')
ax1[1].plot(disp_y['3y'],ret_y['3y'], label ='US: 3y')
ax1[1].plot(disp_y['10y'],ret_y['10y'], label ='US: 10y')
ax1[1].scatter(disp_y['30y'],ret_y['30y'], label ='US: 30y', s = 6, c = 'red')
ax1[1].axhline(y= 0, color = 'black', lw = 0.5, ls = '-.')
#ax1.axvline(x= 0, color = 'black', lw = 0.5, ls = '-.')
#ax1[1].set_ylabel("1Y PX Return (%)", color="black", fontsize=10)
ax1[1].set_xlabel("Yield (%)", color="black", fontsize=10)
plt.show()
















