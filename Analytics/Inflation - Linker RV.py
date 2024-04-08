import QuantLib as ql
import numpy as np
import pandas as pd
from scipy import stats
from Utilities import *


linkers = ['GB00BYY5F144', 'GB00B128DH60', 'GB00BZ1NTB69', 'GB00B3Y1JG82', 'GB0008932666', 'GB00BNNGP551', 'GB00B3D4VD98', 'GB00BMF9LJ15', 'GB00B46CGH68', 'GB0031790826', 'GB00BYZW3J87',
           'GB00B1L6W962', 'GB00BLH38265', 'GB00B3LZBF68', 'GB00BGDYHF49', 'GB00B3MYD345', 'GB00B7RN0G65', 'GB00BMF9LH90', 'GB00BYMWG366', 'GB00B24FFM16', 'GB00BZ13DV40', 'GB00B421JZ66',
           'GB00BNNGP882', 'GB00B73ZYW09', 'GB00B0CNHZ09', 'GB00BYVP4K94', 'GB00BP9DLZ64', 'GB00B4PTCY75', 'GB00BD9MZZ71', 'GB00BDX8CX86', 'GB00BM8Z2W66']

comparators = ['GB00BL68HJ26', 'GB00BDRHNP05', 'GB00BMBL1G81', 'GB00BLPK7227', 'GB00B24FF097', 'GB0004893086', 'GB0004893086', 'GB0004893086', 'GB00B52WS153', 'GB0032452392', 'GB0032452392',
               'GB00BZB26Y51', 'GB00BJQWYH73', 'GB00BJQWYH73', 'GB00BJQWYH73', 'GB00B1VWPJ53', 'GB00B84Z9V04', 'GB00BNNGP775', 'GB00BDCHBW80', 'GB00BDCHBW80', 'GB00BMBL1F74', 'GB00BMBL1F74',
               'GB00BLH38158', 'GB00B6RNH572', 'GB00B06YGN05', 'GB00BD0XH204', 'GB00B54QLM75', 'GB00BMBL1D50', 'GB00BYYMZX75', 'GB00BFMCN652', 'GB00BLBDX619']



linkers = [linkers[i] + ' Govt' for i in np.arange(len(linkers))]
comparators = [comparators[i] + ' Govt' for i in np.arange(len(comparators))]

s1 = con.ref( linkers, 'SECURITY_NAME').set_index('ticker').loc[linkers]['value'].tolist()



today = ql.Date(datetime.datetime.now().day, datetime.datetime.now().month, datetime.datetime.now().year)
start_dt = bbg_date_str(ql.UnitedKingdom().advance(today, ql.Period('-3Y')))
latest = bbg_date_str(today)

linker_feed = list(np.array(linkers)[[5,10,15]])
feed = [linkers.index(linker_feed[i]) for i in np.arange(len(linker_feed))]
comp_feed = list(np.array(comparators)[feed])


df1 = con.bdh( linker_feed, ['YLD_YTM_MID', 'Z_SPRD_MID'], start_dt, latest)
df2 = con.bdh( comp_feed, ['YLD_YTM_MID', 'Z_SPRD_MID'], start_dt, latest)

ry = get_linker_metrics(df1, linker_feed, m='fly')
nom = get_linker_metrics(df2, comp_feed, m='fly')


comb = pd.DataFrame()
comb['date'] = ry['date']
comb['fly'] = nom['fly'] - ry['fly']
comb['z_sprd'] = nom['flyz_sprd'] - ry['flyz_sprd']
comb['z_score_1m'] = roll_zscore(comb['fly'], 20)
comb['z_score_3m'] = roll_zscore(comb['fly'], 60)
comb['z_score_6m'] = roll_zscore(comb['fly'], 180)

comb['rel_z_z_score_1m'] = roll_zscore(comb['z_sprd'], 20)
comb['rel_z_z_score_3m'] = roll_zscore(comb['z_sprd'], 60)
comb['rel_z_z_score_6m'] = roll_zscore(comb['z_sprd'], 180)



plt.plot(ry['date'], comb['z_sprd'])
plt.plot(ry['date'], z1)
plt.plot(ry['date'], col_mean)
plt.plot(ry['date'], col_std)
plt.plot(ry['date'], comb['rel_z_z_score_3m'])
plt.show()

comb[600:650]
comb['z_sprd'].rolling(window=60).mean().shift(1)[600:650]

comb['z_sprd'].rolling(window=60).std(ddof=0).shift(1)



def roll_zscore(x, window):
    r = x.rolling(window=window)
    m = r.mean().shift(1)
    s = r.std(ddof=0).shift(1)
    z = (x - m) / s
    return z

def roll_zscore2(x, window):
    for i in np.arange(window,len(comb)):
        s = np.std(comb['z_sprd'][i-60:i])
        m = np.mean(comb['z_sprd'][i-60:i])
        z = (comb['z_sprd'][i] - m) / s
        print(i, m, s, z)


comb['z_sprd'].rolling(2).apply(lambda x: x[-1:])

comb['z_sprd'][590:640]
comb['z_sprd'].rolling(60).apply(lambda x: (x[-1:] - np.mean(x))/np.std(x))[600:650]

comb['fly'].rolling(180).apply(lambda x: (x[-1:] - np.mean(x))/np.std(x))

z = []
for i in np.arange(60, len(comb)):
    s = np.std(comb['z_sprd'][i - 60:i])
    m = np.mean(comb['z_sprd'][i - 60:i])
    z.append((comb['z_sprd'][i] - m) / s)
    print(i, m, s, z)

col_mean = comb["z_sprd"].rolling(window=60).mean()
col_std = comb["z_sprd"].rolling(window=60).std()
z1 = (comb["z_sprd"] - col_mean)/col_std


comb[570:620]
col_mean[600:650]

