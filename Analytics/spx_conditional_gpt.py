#####


d1 = con.bdh(['FDTR Index', 'CPI YOY Index', 'SPX Index'] , 'PX_LAST', '19200101', '20220415', longdata = False)
d1 = d1.resample('M').last()

d2 = pd.DataFrame(d1['CPI YOY Index']['PX_LAST'])
d2['FDTR'] = pd.DataFrame(d1['FDTR Index']['PX_LAST'])
d2['SPX'] = pd.DataFrame(d1['SPX Index']['PX_LAST'])
d2.columns = ['CPI','FDTR','SPX']

df=d2

#from scipy.signal import argrelextrema
#cpi_window_size = 15
#base_window_size = 0
# Find the local maxima in the base rate and CPI columns
#base_rate_maxima = argrelextrema(df['FDTR'].values, np.greater)[0]
#cpi_maxima = argrelextrema(df['CPI'].values, np.greater, order=cpi_window_size)[0]

from scipy.signal import find_peaks
peaks_base, _ = find_peaks(d2['FDTR'][:-12], height=0, distance = 12)
peaks_cpi, _ = find_peaks(d2['CPI'][:-12], height=5, distance = 18)

# Get the values of the SPX and CPI columns at the turning points
spx_base_rate_maxima = df.iloc[peaks_base]['SPX']
spx_cpi_maxima = df.iloc[peaks_cpi]['SPX']
cpi_maxima_values = df.iloc[peaks_cpi]['CPI']
base_maxima_values = df.iloc[peaks_base]['FDTR']

spx_stats_base_rate = dict()
spx_stats_cpi = dict()
spx_spx_cpi_chg = dict()
spx_spx_base_chg = dict()

for j in [3,6,12]:
    # Calculate the % change in SPX over the following 3 months for each peak
    spx_pct_chg_base_rate = pd.Series([df['SPX'][i+j] / df['SPX'][i] - 1 for i in peaks_base])
    spx_pct_chg_cpi = pd.Series([df['SPX'][i+j] / df['SPX'][i] - 1 for i in peaks_cpi])

    # Remove any NaN values from the % change in SPX 
    spx_pct_chg_base_rate_no_nan = spx_pct_chg_base_rate.dropna()
    spx_pct_chg_cpi_no_nan = spx_pct_chg_cpi.dropna()

    # Calculate the requested statistics for each base rate peak   
    spx_stats_base_rate[str(j)+'m'] = spx_pct_chg_base_rate_no_nan.describe(percentiles=[0.25, 0.75])
    spx_stats_base_rate[str(j)+'m']['% Positive'] =  round((spx_pct_chg_base_rate_no_nan > 0).mean() * 100, 0)
    spx_stats_base_rate[str(j)+'m']['% Negative'] = round((spx_pct_chg_base_rate_no_nan < 0).mean() * 100, 0)

    # Calculate the requested statistics for each CPI peak    
    spx_stats_cpi[str(j)+'m']  = spx_pct_chg_cpi_no_nan.describe(percentiles=[0.25, 0.75])
    spx_stats_cpi[str(j)+'m']['% Positive'] = round((spx_pct_chg_cpi_no_nan > 0).mean() * 100, 0)
    spx_stats_cpi[str(j)+'m']['% Negative'] = round((spx_pct_chg_cpi_no_nan < 0).mean() * 100, 0)

    # List the 3-month % changes in SPX     
    spx_spx_cpi_chg[str(j)+'m'] = pd.DataFrame({'3-month % change in SPX': spx_pct_chg_cpi_no_nan})
    spx_spx_base_chg[str(j)+'m'] = pd.DataFrame({'3-month % change in SPX': spx_pct_chg_base_rate_no_nan})

# Create a labeled and tabular output for the statistics
output_base_rate = pd.DataFrame({'Statistics for peak base rate': spx_stats_base_rate})
output_cpi = pd.DataFrame({'Statistics for peak CPI': spx_stats_cpi})

# Print the output
print(pd.concat([output_base_rate, output_cpi], axis=1))


output_base_rate = pd.DataFrame(spx_stats_base_rate)
output_base_rate.columns=['3m_base','6m_base','12m_base']

output_cpi = pd.DataFrame(spx_stats_cpi)
output_cpi.columns=['3m_cpi','6m_cpi','12m_cpi']




from scipy.signal import find_peaks
x = d2['FDTR']
peaks_base, _ = find_peaks(x, height=0, distance = 12)
df.iloc[peaks_base]['FDTR']


x2 = d2['CPI']
peaks_cpi, _ = find_peaks(x2, height=5, distance = 18)
df.iloc[peaks_cpi]['CPI']

# Define a function to calculate the statistics for a given time period
def calc_stats(spx_pct_chg):
    return {
        'Min': spx_pct_chg.min(),
        'Max': spx_pct_chg.max(),
        '1st Q': spx_pct_chg.quantile(0.25),
        'Median': spx_pct_chg.median(),
        '3rd Q': spx_pct_chg.quantile(0.75),
        '% Positive': (spx_pct_chg > 0).mean(),
        '% Negative': (spx_pct_chg < 0).mean()
    }

# Create empty dictionaries to hold results for each period
spx_stats_3m = {'Min': [], 'Max': [], '1st Q': [], 'Median': [], '3rd Q': [], '% Positive': [], '% Negative': []}
spx_stats_6m = {'Min': [], 'Max': [], '1st Q': [], 'Median': [], '3rd Q': [], '% Positive': [], '% Negative': []}
spx_stats_12m = {'Min': [], 'Max': [], '1st Q': [], 'Median': [], '3rd Q': [], '% Positive': [], '% Negative': []}

# Loop through each identified peak and accumulate SPX returns data for each timeframe
for peak_idx in peaks_cpi:
    spx_data = {'3m': [], '6m': [], '12m': []}

    for k, timeframe in enumerate([3, 6, 12]):
        spx_pct_chg = (df['SPX'][peak_idx + 1: peak_idx + timeframe + 1] / df['SPX'][peak_idx] - 1).dropna()
        spx_data[str(timeframe) + 'm'] = spx_pct_chg.tolist()

    # Calculate the requested statistics for each SPX return timeframe
        spx_stats_3m['Min'].append(min(spx_data['3m'])) 
        spx_stats_3m['Max'].append(max(spx_data['3m']))
        spx_stats_3m['1st Q'].append(pd.Series(spx_data['3m']).quantile(0.25))
        spx_stats_3m['Median'].append(pd.Series(spx_data['3m']).median())
        spx_stats_3m['3rd Q'].append(pd.Series(spx_data['3m']).quantile(0.75))
        spx_stats_3m['% Positive'].append((pd.Series(spx_data['3m']) > 0).mean())
        spx_stats_3m['% Negative'].append((pd.Series(spx_data['3m']) < 0).mean())
    
        spx_stats_6m['Min'].append(min(spx_data['6m']))
        spx_stats_6m['Max'].append(max(spx_data['6m'])) 
        spx_stats_6m['1st Q'].append(pd.Series(spx_data['6m']).quantile(0.25))
        spx_stats_6m['Median'].append(pd.Series(spx_data['6m']).median())
        spx_stats_6m['3rd Q'].append(pd.Series(spx_data['6m']).quantile(0.75))
        spx_stats_6m['% Positive'].append((pd.Series(spx_data['6m']) > 0).mean())
        spx_stats_6m['% Negative'].append((pd.Series(spx_data['6m']) < 0).mean())

        spx_stats_12m['Min'].append(min(spx_data['12m']))
        spx_stats_12m['Max'].append(max(spx_data['12m']))
        spx_stats_12m['1st Q'].append(pd.Series(spx_data['12m']).quantile(0.25))
        spx_stats_12m['Median'].append(pd.Series(spx_data['12m']).median())
        spx_stats_12m['3rd Q'].append(pd.Series(spx_data['12m']).quantile(0.75))
        spx_stats_12m['% Positive'].append((pd.Series(spx_data['12m']) > 0).mean())
        spx_stats_12m['% Negative'].append((pd.Series(spx_data['12m']) < 0).mean())

spx_table = pd.DataFrame({
    'Period': ['3m', '6m', '12m'],
    'Min': [min(spx_stats_3m['Min']), min(spx_stats_6m['Min']), min(spx_stats_12m['Min'])],
    'Max': [max(spx_stats_3m['Max']), max(spx_stats_6m['Max']), max(spx_stats_12m['Max'])],
    '1st Q': [pd.Series(spx_stats_3m['1st Q']).mean(), pd.Series(spx_stats_6m['1st Q']).mean(), pd.Series(spx_stats_12m['1st Q']).mean()],
    'Median': [pd.Series(spx_stats_3m['Median']).mean(), pd.Series(spx_stats_6m['Median']).mean(), pd.Series(spx_stats_12m['Median']).mean()],
    '3rd Q': [pd.Series(spx_stats_3m['3rd Q']).mean(), pd.Series(spx_stats_6m['3rd Q']).mean(), pd.Series(spx_stats_12m['3rd Q']).mean()],
    '% Positive': [pd.Series(spx_stats_3m['% Positive']).mean(), pd.Series(spx_stats_6m['% Positive']).mean(), pd.Series(spx_stats_12m['% Positive']).mean()],
    '% Negative': [pd.Series(spx_stats_3m['% Negative']).mean(), pd.Series(spx_stats_6m['% Negative']).mean(), pd.Series(spx_stats_12m['% Negative']).mean()]
})

# Format the output table
spx_table['Min'] = spx_table['Min'].apply('{:.2f}%'.format)
spx_table['Max'] = spx_table['Max'].apply('{:.2f}%'.format)
spx_table['1st Q'] = spx_table['1st Q'].apply('{:.2f}%'.format)
spx_table['Median'] = spx_table['Median'].apply('{:.2f}%'.format)
spx_table['3rd Q'] = spx_table['3rd Q'].apply('{:.2f}%'.format)
spx_table['% Positive'] = spx_table['% Positive'].apply('{:.2f}%'.format)
spx_table['% Negative'] = spx_table['% Negative'].apply('{:.2f}%'.format)

# Print the output table
print(spx_table)

























                                                                              