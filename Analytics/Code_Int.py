##### getting data for Code Interpreter
import matplotlib.pyplot as plt
import pandas as pd

## Eco data
us = get_data(data_df, 'US', '20000101', end=-1, cat1='all', cat2='all', change=6, roc =3, zs_period = 3)
us.raw
us.zs_pct

us.zs_raw.to_excel("usdata_zs.xlsx")


#### UST data

f1 = con.bdh('USYC2Y10 Index' , 'PX_LAST', '19770201', '20230707', longdata = True)
f2 = con.bdh('GT10 Govt' , 'PX_LAST', '19770201', '20230707', longdata = True)

g1 = pd.DataFrame()
g1['date'] = f1['date']

g1 = pd.merge(f1, f2, on='date', how='outer')
g1 = g1.dropna()

g1['usd_2s10s'] = g1['value_x']
g1['usd_10s'] = g1['value_y']

g2 = g1[['date','usd_10s','usd_2s10s']]
g2.to_excel("us_2s10s.xlsx")


#### conditional on fed
f1 = con.bdh('USYC2Y10 Index' , 'PX_LAST', '19770201', '20230707', longdata = True)
f2 = con.bdh('GT10 Govt' , 'PX_LAST', '19770201', '20230707', longdata = True)
f3 = con.bdh('GT5 Govt' , 'PX_LAST', '19770201', '20230707', longdata = True)
f4 = con.bdh('SPX Index' , 'PX_LAST', '19770201', '20230707', longdata = True)
f5 = con.bdh('FDTR Index' , 'PX_LAST', '19770201', '20230707', longdata = True)
f6 = con.bdh('EURUSD Curncy' , 'PX_LAST', '19770201', '20230707', longdata = True)
f7 = con.bdh('BCOM Curncy' , 'PX_LAST', '19770201', '20230707', longdata = True)

df = [f1,f2,f3,f4,f5,f6,f7]
from functools import reduce
df_merged = reduce(lambda  left,right: pd.merge(left,right,on=['date'], how='outer'), df)

g1 = df_merged.dropna()

g1.columns = ['date','t1','px1','usd_2s10s',
              't2','px2','usd_10s',
              't3','px3','usd_5s',
              't4','px4','spx',
              't5','px5','fed',
              't6','px6','eurusd',
              't7','px7','bcom']


g2 = g1[['date','fed', 'usd_10s', 'usd_5s','usd_2s10s', 'spx', 'eurusd', 'bcom']]
g2.to_excel("us_fed.xlsx")


############ find start and end of rate hiking cycles

def rate_cycle(d1, base):
#    d1 = g2
#    base = 'fed'

    d1['rate_change'] = g2[base].diff()

    # Create a new DataFrame that only includes the dates where the rate changed
    df_rate_change = d1[d1['rate_change'] != 0].copy()

    # Add a column for the direction of the rate change
    df_rate_change['change_direction'] = df_rate_change['rate_change'].apply(lambda x: 'increase' if x > 0 else 'decrease')

    # Initialize the first group
    df_rate_change['group'] = 'A'
    current_group = 'A'
    current_direction = df_rate_change['change_direction'].iloc[0]

    # Loop through the rate change DataFrame
    for i in range(1, len(df_rate_change)):
        # If the current rate change is in the same direction as the previous rate change, assign it to the current group
        if df_rate_change['change_direction'].iloc[i] == current_direction:
            df_rate_change['group'].iloc[i] = current_group
        # If the current rate change is in a different direction, start a new group
        else:
            current_group = chr(ord(current_group) + 1)  # Increment the group letter
            current_direction = df_rate_change['change_direction'].iloc[i]  # Update the current direction
            df_rate_change['group'].iloc[i] = current_group

    start_date_incr = []
    end_date_incr = []
    for i in df_rate_change[df_rate_change['change_direction'] == 'increase']['group'].unique():
        dt_range = df_rate_change[df_rate_change['group'] == i]['date'].tolist()
        start_date_incr.append(dt_range[0])
        end_date_incr.append(dt_range[-1])

    start_date_decr = []
    end_date_decr = []
    for i in df_rate_change[df_rate_change['change_direction'] == 'decrease']['group'].unique():
        dt_range = df_rate_change[df_rate_change['group'] == i]['date'].tolist()
        start_date_decr.append(dt_range[0])
        end_date_decr.append(dt_range[-1])


    class rate_cycle_output():
        def __init__(self):
            self.df = df_rate_change
            self.start_hike = np.array(start_date_incr)
            self.end_hike = np.array(end_date_incr)
            self.start_cut = np.array(start_date_decr)
            self.end_cut = np.array(end_date_decr)

    return rate_cycle_output()

rc = rate_cycle(g2,'fed')

rc.end_hike


# Get the unique groups
groups = rc.df[rc.df['change_direction'] == 'increase']['group'].unique()

# Define a list of colors for the groups
plt.figure(figsize=(18, 10))
plt.plot(g2['date'], g2['fed'], label='Federal Reserve base rate')

# Shade the areas based on the group
palette = sns.color_palette("viridis", 50)
for group, color in zip(groups, palette):
    df_group = rc.df[rc.df['group'] == group]
    for i in range(len(df_group) - 1):
        plt.axvspan(df_group['date'].iloc[i], df_group['date'].iloc[i+1], facecolor=color, alpha=0.3)

plt.legend()
plt.xlabel('Date')
plt.ylabel('Rate (%)')
plt.show()




fig, axs = plt.subplots(2, 1,  figsize=(12, 10))
axs[0].plot(g2['date'], g2['fed'], label='Federal Reserve base rate')
for group, color in zip(groups, palette):
    df_group = rc.df[rc.df['group'] == group]
    for i in range(len(df_group) - 1):
        axs[0].axvspan(df_group['date'].iloc[i], df_group['date'].iloc[i+1], facecolor=color, alpha=0.3)
#axs[0].set_xlabel('Date')
axs[0].set_ylabel('Fed Base')
axs[0].title.set_text('Hiking Cycle')

plt.show()


from pandas.tseries.offsets import DateOffset

g4 = {key: [] for key in ['fed', 'usd_10s', 'usd_5s', 'usd_2s10s', 'spx', 'eurusd', 'bcom']}
for i in rc.end_hike[11:-1]:
    exact_date = i + DateOffset(months=6)
    closest_date = g2.iloc[(g2['date'] - exact_date).abs().argsort()[:1]]['date'].values[0]
#    print(i, exact_date, closest_date)
    g3 = g2[( (g2['date'] == i) | (g2['date'] == closest_date) )].reset_index(drop=True)

    for j in ['fed','usd_10s','usd_5s','usd_2s10s']:
        g4[j].append(100*g3[j].diff().iloc[1])
    for j in ['spx','eurusd','bcom']:
        g4[j].append(100*g3[j].pct_change().iloc[1])
g4['usd_2s10s'] = list(0.01*np.array(g4['usd_2s10s']))


fig, axs = plt.subplots(1,len(g4),figsize=(10,  5), sharey=False)
colors = ['lightblue', 'lightgreen']
for i in np.arange(len(g4)):
    bplot = axs[i].boxplot(pd.DataFrame(g4).iloc[:,i].tolist(), labels= [list(g4.keys())[i]], whis=(0,100), patch_artist=True )
    axs[i].tick_params(axis='both', labelsize=6)
    axs[i].spines['right'].set_visible(False)
    axs[i].spines['top'].set_visible(False)
    axs[i].spines['bottom'].set_visible(False)
    for patch in bplot['boxes']:
        patch.set(color= colors[i%2])
axs[3].title.set_text('Distribution of Chg 6m after last hike - last 7 cycles')
plt.show()











