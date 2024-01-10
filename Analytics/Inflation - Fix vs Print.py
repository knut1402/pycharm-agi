##### inflation fixings vs prints vs central bank forecats
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import matplotlib.patches as mpatches
import pandas as pd

### RPI
rpi_ticker = 'UKRPI Index'
cpi_ticker = 'UKRPCHVJ Index'

#### dates!!
latest = ql.Date(10,7,2023)
d1 = [ql.UnitedKingdom().advance(latest,-int(i),ql.Days) for i in np.arange(1,4800)]
start = bbg_date_str(d1[-1])
latest_bbg = bbg_date_str(latest)

#### get rpi prints
g1 = con.bdh(rpi_ticker , 'PX_LAST', bbg_date_str(d1[-1]-ql.Period(12,ql.Months)), latest_bbg, longdata = True)#
g1['rpi_print']= 100*g1['value'].pct_change(periods=12)

h1 = con.bdh(cpi_ticker , 'PX_LAST', bbg_date_str(d1[-1]-ql.Period(12,ql.Months)), latest_bbg, longdata = True)#
h1['cpi_print']= 100*h1['value'].pct_change(periods=12)

g1['wedge'] = g1['rpi_print'] - h1['cpi_print']

m1 = np.array(g1['wedge'].dropna()).mean()
m2 = np.median(np.array(g1['wedge'].dropna()))

### plot wedge
plt.plot(g1['date'],g1['wedge'], label = 'CPI/RPI Wedge', lw = '1.5')
#plt.axhline(m1, ls = '--', lw = 1.5, c='lightblue', label = 'Mean = 1.2%')
plt.axhline(m2, ls = '--', lw = 1.5, c='lightblue', label = 'Median = 0.90%')
plt.legend(fontsize = 8)
plt.grid(visible=True, linestyle='--', linewidth=0.2)
plt.xticks(rotation = 90)
plt.xticks(fontsize=7.5)
plt.ylabel('%')
plt.yticks(fontsize=7.5)
plt.show()

#### get all fixings
rpi_fix_ticker = ['BPSWIF1 INFF Index', 'BPSWIF2 INFF Index', 'BPSWIF3 INFF Index', 'BPSWIF4 INFF Index',
                  'BPSWIF5 INFF Index', 'BPSWIF6 INFF Index', 'BPSWIF7 INFF Index', 'BPSWIF8 INFF Index',
                  'BPSWIF9 INFF Index', 'BPSWIF10 INFF Index', 'BPSWIF11 INFF Index', 'BPSWIF12 INFF Index']

f1 = con.bdh(rpi_fix_ticker , 'PX_LAST', start, latest_bbg, longdata = True)

d2 = np.unique([datetime_to_ql(f1['date'][i]) for i in np.arange(len(f1['date'])) ])
#d2[0]

f2 = dict()
for i in np.arange(len(d2)):
    f3 = f1[f1['date']== ql_to_datetime(d2[i])]['ticker'].tolist()
    f4 = [int(f3[j].split()[0][6:]) for j in np.arange(len(f3))]
    f5 = (0.01*f1[f1['date'] == ql_to_datetime(d2[i])]['value']).tolist()
    f6 = [ ql_to_datetime (ql.Date(15, f4[j], d2[i].year() + (f4[j] < d2[i].month()))) for j in np.arange(len(f4))]

    f2[d2[i]] = pd.DataFrame({'ticker': f3,'fix_date':f6, 'fixing': f5})
    f2[d2[i]] = f2[d2[i]].sort_values('fix_date')[:-1]


############### MPC projections
mpc = pd.ExcelFile("./DataLake/mpc_projection.xlsx")
mpc_df = pd.read_excel(mpc,"CPI Forecast")
mpc_df2 = mpc_df[mpc_df['Type'] == 'Market Median']
mpc_df2.columns = ['Year', 'Month', 'Type']+ [ql.Date(15, (3*(int(mpc_df2.columns[i][-1])-1))+2, int(mpc_df2.columns[i][:4])) for i in np.arange(3,len(mpc_df2.columns))]


m1 = dict()
for i in np.arange( len(mpc_df2.columns) - sum([mpc_df2.columns[i] > ql.Date(1,6,2013) for i in np.arange(3,len(mpc_df2.columns))]),len(mpc_df2.columns)):
    try:
        w1 = g1[g1['date'] == ql_to_datetime(ql.Date.endOfMonth(mpc_df2.columns[i]))]['wedge'].tolist()[0]
    except:
        w1 = 1.0
    m1[mpc_df2.columns[i]] = (w1+mpc_df2[mpc_df2.columns[i]].dropna()).tolist()   ###### w1 = realised wedge


m2 = dict()
for j in m1.keys():
    if len(m1[j]) > 7:
        if j>ql.Date(1,8,2023):
            m2[j] = m1[j][7:]
        else:
            m2[j] = m1[j][7:-1]


xtx = [ql_to_datetime(list(m2.keys())[i]) for i in np.arange(len(m2.keys()))]
xtx_l = [str(xtx[i])[:10] for i in np.arange(len(xtx))]

### plot mpc projections
for j in m2.keys():
    cp =  sns.color_palette("ch:start=.2,rot=-.3", n_colors=len(m2[j]))
    plt.scatter( np.repeat( ql_to_datetime(j), len(m2[j]) ), m2[j], color = cp, s=5 )
plt.show()


################## plot

plt.figure(figsize=(18,12))
for i in np.arange(len(d2)):
    plt.plot(f2[d2[i]]['fix_date'], f2[d2[i]]['fixing'], c='grey', linewidth=0.2)
for j in m2.keys():
    cp =  sns.color_palette("ch:start=.3,rot=-.3", n_colors=len(m2[j]))
    plt.plot( np.repeat( ql_to_datetime(ql.Date.endOfMonth(j)), len(m2[j]) ), m2[j], color = 'b', linewidth=0.5)
    plt.scatter(np.repeat(ql_to_datetime(ql.Date.endOfMonth(j)), len(m2[j])), m2[j], color=cp, s=10)

plt.scatter(g1['date'][12:],g1['rpi_print'][12:], c='red', s=10)
plt.xticks(xtx[::2], labels = xtx_l[::2], rotation=90)
plt.grid(linestyle='--', linewidth=0.3)
plt.xlabel('Fixing Date')
plt.ylabel('UKRPI YoY (%)')
line = Line2D([0], [0], label='RPI Swap Fixings', color='grey')
point_fix = Line2D([0], [0], label='RPI Print', marker='o', markersize=3, markeredgecolor='r', markerfacecolor='r', linestyle='')
point_mpc = Line2D([0], [0], label='MPC Projection: Median Mkt-Based', marker='o', markersize=3, markeredgecolor='b', markerfacecolor='b', linestyle='')
point_wedge = Line2D([0], [0], label='CPI/RPI Wedge assumption: \nPast prints: Realised \nFwd prints: +100bps', marker='o', markersize=3, markeredgecolor='w', markerfacecolor='w', linestyle='')
plt.legend(handles=[line,point_fix,point_mpc,point_wedge])
plt.title('UKRPI: Fixing vs Print vs MPC')
plt.tight_layout()
plt.show()



