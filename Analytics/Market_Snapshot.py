##### Market snapshot 

start_date = '20231018'
end_date = '20240312'

inst = ['GT2 Govt','GT5 Govt','GT10 Govt','GT30 Govt', 'G0025 1Y1Y BLC2 Curncy', 'G0025 2Y1Y BLC2 Curncy', 'G0025 3Y1Y BLC2 Curncy', 'G0025 2Y2Y BLC2 Curncy','G0025 5Y5Y BLC2 Curncy' ,'G0025 10Y10Y BLC2 Curncy',
        'USOSFR2 Curncy', 'USOSFR5 Curncy', 'USOSFR10 Curncy', 'USOSFR30 Curncy','SD0490FS 1Y1Y BLC Curncy', 'SD0490FS 2Y1Y BLC Curncy', 'SD0490FS 3Y1Y BLC Curncy', 'SD0490FS 2Y2Y BLC Curncy', 'SD0490FS 5Y5Y BLC Curncy', 'SD0490FS 10Y10Y BLC Curncy',
        'GTDEM2Y Govt','GTDEM5Y Govt','GTDEM10Y Govt','GTDEM30Y Govt', 'G0016 1Y1Y BLC2 Curncy', 'G0016 2Y1Y BLC2 Curncy', 'G0016 3Y1Y BLC2 Curncy', 'G0016 2Y2Y BLC2 Curncy','G0016 5Y5Y BLC2 Curncy' ,'G0016 10Y10Y BLC2 Curncy',
        'EESWE2 Curncy', 'EESWE5 Curncy', 'EESWE10 Curncy', 'EESWE30 Curncy','S0514FS 1Y1Y BLC Curncy', 'S0514FS 2Y1Y BLC Curncy', 'S0514FS 3Y1Y BLC Curncy', 'S0514FS 2Y2Y BLC Curncy', 'S0514FS 5Y5Y BLC Curncy', 'S0514FS 10Y10Y BLC Curncy',
        'GTFRF2Y Govt','GTFRF5Y Govt','GTFRF10Y Govt','GTFRF30Y Govt', 'G0014 1Y1Y BLC2 Curncy', 'G0014 2Y1Y BLC2 Curncy', 'G0014 3Y1Y BLC2 Curncy', 'G0014 2Y2Y BLC2 Curncy','G0014 5Y5Y BLC2 Curncy' ,'G0014 10Y10Y BLC2 Curncy',
        'GTITL2Y Govt','GTITL5Y Govt','GTITL10Y Govt','GTITL30Y Govt', 'G0040 1Y1Y BLC2 Curncy', 'G0040 2Y1Y BLC2 Curncy', 'G0040 3Y1Y BLC2 Curncy', 'G0040 2Y2Y BLC2 Curncy','G0040 5Y5Y BLC2 Curncy' ,'G0040 10Y10Y BLC2 Curncy',
        'GTESP2Y Govt','GTESP5Y Govt','GTESP10Y Govt','GTESP30Y Govt', 'G0061 1Y1Y BLC2 Curncy', 'G0061 2Y1Y BLC2 Curncy', 'G0061 3Y1Y BLC2 Curncy', 'G0061 2Y2Y BLC2 Curncy','G0061 5Y5Y BLC2 Curncy' ,'G0061 10Y10Y BLC2 Curncy',
        'GTGBP2Y Govt','GTGBP5Y Govt','GTGBP10Y Govt','GTGBP30Y Govt', 'G0022 1Y1Y BLC2 Curncy', 'G0022 2Y1Y BLC2 Curncy', 'G0022 3Y1Y BLC2 Curncy', 'G0022 2Y2Y BLC2 Curncy','G0022 5Y5Y BLC2 Curncy' ,'G0022 10Y10Y BLC2 Curncy',
        'BPSWS2 Curncy', 'BPSWS5 Curncy', 'BPSWS10 Curncy', 'BPSWS30 Curncy','S0141FS 1Y1Y BLC Curncy', 'S0141FS 2Y1Y BLC Curncy', 'S0141FS 3Y1Y BLC Curncy', 'S0141FS 2Y2Y BLC Curncy', 'S0141FS 5Y5Y BLC Curncy', 'S0141FS 10Y10Y BLC Curncy',
        'GTCAD2Y Govt','GTCAD5Y Govt','GTCAD10Y Govt','GTCAD30Y Govt', 'G0007 1Y1Y BLC2 Curncy', 'G0007 2Y1Y BLC2 Curncy', 'G0007 3Y1Y BLC2 Curncy', 'G0007 2Y2Y BLC2 Curncy','G0007 5Y5Y BLC2 Curncy' ,'G0007 10Y10Y BLC2 Curncy',
        'CDSW2 Curncy', 'CDSW5 Curncy', 'CDSW10 Curncy', 'CDSW30 Curncy','S0147FS 1Y1Y BLC Curncy', 'S0147FS 2Y1Y BLC Curncy', 'S0147FS 3Y1Y BLC Curncy', 'S0147FS 2Y2Y BLC Curncy', 'S0147FS 5Y5Y BLC Curncy', 'S0147FS 10Y10Y BLC Curncy',
        'GTAUD2Y Govt','GTAUD5Y Govt','GTAUD10Y Govt','GTAUD30Y Govt', 'G0001 1Y1Y BLC2 Curncy', 'G0001 2Y1Y BLC2 Curncy', 'G0001 3Y1Y BLC2 Curncy', 'G0001 2Y2Y BLC2 Curncy','G0001 5Y5Y BLC2 Curncy' ,'G0001 10Y10Y BLC2 Curncy',
        'ADSWAP2Q Curncy', 'ADSWAP5 Curncy', 'ADSWAP10 Curncy', 'ADSWAP30 Curncy','SD0302FS 1Y1Y BLC Curncy', 'SD0302FS 2Y1Y BLC Curncy', 'SD0302FS 3Y1Y BLC Curncy', 'SD0302FS 2Y2Y BLC Curncy', 'SD0302FS 5Y5Y BLC Curncy', 'SD0302FS 10Y10Y BLC Curncy',
        'GTNZD2Y Govt','GTNZD5Y Govt','GTNZD10Y Govt','GTNZD30Y Govt', 'G0049 1Y1Y BLC2 Curncy', 'G0049 2Y1Y BLC2 Curncy', 'G0049 3Y1Y BLC2 Curncy', 'G0049 2Y2Y BLC2 Curncy','G0049 5Y5Y BLC2 Curncy' ,'G0049 10Y10Y BLC2 Curncy',
        'NDSWAP2 Curncy', 'NDSWAP5 Curncy', 'NDSWAP10 Curncy', 'NDSWAP30 Curncy' ,'SD0015FS 1Y1Y BLC Curncy', 'SD0015FS 2Y1Y BLC Curncy', 'SD0015FS 3Y1Y BLC Curncy', 'SD0015FS 2Y2Y BLC Curncy', 'SD0015FS 5Y5Y BLC Curncy', 'SD0015FS 10Y10Y BLC Curncy',
        'GTSEK2Y Govt','GTSEK5Y Govt','GTSEK10Y Govt','GTSEK50Y Govt', 'G0021 1Y1Y BLC2 Curncy', 'G0021 2Y1Y BLC2 Curncy', 'G0021 3Y1Y BLC2 Curncy', 'G0021 2Y2Y BLC2 Curncy','G0021 5Y5Y BLC2 Curncy' ,'G0021 10Y10Y BLC2 Curncy',
        'SKSW2 Curncy', 'SKSW5 Curncy', 'SKSW10 Curncy', 'SKSW30 Curncy','SD0020FS 1Y1Y BLC Curncy', 'SD0020FS 2Y1Y BLC Curncy', 'SD0020FS 3Y1Y BLC Curncy', 'SD0020FS 2Y2Y BLC Curncy', 'SD0020FS 5Y5Y BLC Curncy', 'SD0020FS 10Y10Y BLC Curncy',
        'GTNOK2Y Govt','GTNOK5Y Govt','GTNOK10Y Govt', 'GTNOK10Y Govt', 'G0078 1Y1Y BLC2 Curncy', 'G0078 2Y1Y BLC2 Curncy', 'G0078 3Y1Y BLC2 Curncy', 'G0078 2Y2Y BLC2 Curncy','G0078 5Y5Y BLC2 Curncy' ,'G0078 10Y10Y BLC2 Curncy',
        'NKSW2 Curncy', 'NKSW5 Curncy', 'NKSW10 Curncy', 'NKSW30 Curncy','S0313FS 1Y1Y BLC Curncy', 'S0313FS 2Y1Y BLC Curncy', 'S0313FS 3Y1Y BLC Curncy', 'S0313FS 2Y2Y BLC Curncy', 'S0313FS 5Y5Y BLC Curncy', 'S0313FS 10Y10Y BLC Curncy',
        'GTCHF2Y Govt','GTCHF5Y Govt','GTCHF10Y Govt', 'GTCHF30Y Govt', 'G0082 1Y1Y BLC2 Curncy', 'G0082 2Y1Y BLC2 Curncy', 'G0082 3Y1Y BLC2 Curncy', 'G0082 2Y2Y BLC2 Curncy','G0082 5Y5Y BLC2 Curncy' ,'G0082 10Y10Y BLC2 Curncy',
        'SFSNT2 Curncy', 'SFSNT5 Curncy', 'SFSNT10 Curncy', 'SFSNT30 Curncy','S0234FS 1Y1Y BLC Curncy', 'S0234FS 2Y1Y BLC Curncy', 'S0234FS 3Y1Y BLC Curncy', 'S0234FS 2Y2Y BLC Curncy', 'S0234FS 5Y5Y BLC Curncy', 'S0234FS 10Y10Y BLC Curncy',
        'JYSO2 Curncy', 'JYSO5 Curncy', 'JYSO10 Curncy', 'JYSO30 Curncy','S0195FS 1Y1Y BLC Curncy', 'S0195FS 2Y1Y BLC Curncy', 'S0195FS 3Y1Y BLC Curncy', 'S0195FS 2Y2Y BLC Curncy', 'S0195FS 5Y5Y BLC Curncy', 'S0195FS 10Y10Y BLC Curncy']



inst = ['GTGBP2Y Govt','GTGBP5Y Govt','GTGBP10Y Govt','GTGBP30Y Govt', 'G0022 1Y1Y BLC2 Curncy', 'G0022 2Y1Y BLC2 Curncy', 'G0022 3Y1Y BLC2 Curncy', 'G0022 2Y2Y BLC2 Curncy','G0022 5Y5Y BLC2 Curncy' ,'G0022 10Y10Y BLC2 Curncy',
        'BPSWS2 Curncy', 'BPSWS5 Curncy', 'BPSWS10 Curncy', 'BPSWS30 Curncy','S0141FS 1Y1Y BLC Curncy', 'S0141FS 2Y1Y BLC Curncy', 'S0141FS 3Y1Y BLC Curncy', 'S0141FS 2Y2Y BLC Curncy', 'S0141FS 5Y5Y BLC Curncy', 'S0141FS 10Y10Y BLC Curncy',
        'GT2 Govt','GT5 Govt','GT10 Govt','GT30 Govt', 'G0025 1Y1Y BLC2 Curncy', 'G0025 2Y1Y BLC2 Curncy', 'G0025 3Y1Y BLC2 Curncy', 'G0025 2Y2Y BLC2 Curncy','G0025 5Y5Y BLC2 Curncy' ,'G0025 10Y10Y BLC2 Curncy',
        'GTDEM2Y Govt','GTDEM5Y Govt','GTDEM10Y Govt','GTDEM30Y Govt', 'G0016 1Y1Y BLC2 Curncy', 'G0016 2Y1Y BLC2 Curncy', 'G0016 3Y1Y BLC2 Curncy', 'G0016 2Y2Y BLC2 Curncy','G0016 5Y5Y BLC2 Curncy' ,'G0016 10Y10Y BLC2 Curncy',
        'GTFRF2Y Govt','GTFRF5Y Govt','GTFRF10Y Govt','GTFRF30Y Govt', 'G0014 1Y1Y BLC2 Curncy', 'G0014 2Y1Y BLC2 Curncy', 'G0014 3Y1Y BLC2 Curncy', 'G0014 2Y2Y BLC2 Curncy','G0014 5Y5Y BLC2 Curncy' ,'G0014 10Y10Y BLC2 Curncy',
        'GTITL2Y Govt','GTITL5Y Govt','GTITL10Y Govt','GTITL30Y Govt', 'G0040 1Y1Y BLC2 Curncy', 'G0040 2Y1Y BLC2 Curncy', 'G0040 3Y1Y BLC2 Curncy', 'G0040 2Y2Y BLC2 Curncy','G0040 5Y5Y BLC2 Curncy' ,'G0040 10Y10Y BLC2 Curncy',
        'GTESP2Y Govt','GTESP5Y Govt','GTESP10Y Govt','GTESP30Y Govt', 'G0061 1Y1Y BLC2 Curncy', 'G0061 2Y1Y BLC2 Curncy', 'G0061 3Y1Y BLC2 Curncy', 'G0061 2Y2Y BLC2 Curncy','G0061 5Y5Y BLC2 Curncy' ,'G0061 10Y10Y BLC2 Curncy']



def get_snap(inst, d1, d2):
    df1 = con.bdh(inst , 'PX_LAST', d1, d2, longdata = True)
    #### 5d changes
    df_5 = df1['value'].diff(5)
    #### 20d changes
    df_20 = df1['value'].diff(20)
    ### ytd 
    df_ytd = df1['value'][-1:] - list(df1[df1['date']  == '2024-01-03']['value'])[0]
    a = [list( np.round(df1['value'][-1:],2)), list( np.round(100*df_5[-1:],1)), [np.round(zscore(df_5[5:])[-1:],2)],
         list( np.round(100*df_20[-1:],1)), [np.round(zscore(df_20[20:])[-1:],2)], list( np.round(100*df_ytd[-1:],0))]

    return a


c1 = ['UST', 'SOFR', 'GE', 'ESTER', 'FR', 'IT', 'SP', 'UKT', 'SONIA', 'CA', 'CDOR', 'AU', 'AUD_6M', 'NZ', 'NZD_3M', 'SW', 'STIBOR', 'NO', 'NIBOR', 'CH', 'SARON', 'TONAR' ]
c2 = ['2Y', '5Y', '10Y', '30Y', '1Y1Y', '2Y1Y', '3Y1Y', '2Y2Y', '5Y5Y', '10Y10Y' ]

c1 = ['UKT', 'SONIA', 'UST', 'GE', 'FR', 'IT', 'SP']
c2 = ['2Y', '5Y', '10Y', '30Y', '1Y1Y', '2Y1Y', '3Y1Y', '2Y2Y', '5Y5Y', '10Y10Y' ]


n1 =  dict([(k1, dict([(k2, []) for k2 in c2]) ) for k1 in c1])

i=0
for k in n1.keys():
    for j in c2:
        print(inst[i])
        n1[k][j].append(inst[i])
        v1 = get_snap(inst[i], start_date, end_date) 
        n1[k][j] = n1[k][j] + v1
        i += 1

df1 = pd.DataFrame()
df2 = pd.DataFrame()
df3 = pd.DataFrame()
df4 = pd.DataFrame()

for i in c1:
    df1[i] = flat_lst([n1[i][j][1] for j in c2])
    df2[i] = flat_lst([n1[i][j][2] for j in c2])
    df3[i] = flat_lst([n1[i][j][4] for j in c2])
    df4[i] = flat_lst([n1[i][j][6] for j in c2])

df1.index = c2
df2.index = c2
df3.index = c2
df4.index = c2



fig, axs = plt.subplots(2, 2, figsize=(20, 16))
fig.subplots_adjust(hspace=0.25)
ax1 = plt.subplot(2, 2, 1)
ax1.set_title('Rate', fontdict={'fontsize':9})
sns.heatmap(df1.transpose(), cmap='Blues', linewidths=1, annot=df1.transpose(), xticklabels=df1.index, yticklabels=df1.columns, fmt=".5g", cbar=False, ax=ax1)
ax2 = plt.subplot(2, 2, 2)
ax2.set_title('5D-Chg', fontdict={'fontsize':9})
sns.heatmap(df2.transpose(), cmap='vlag_r', linewidths=1, annot=df2.transpose(), xticklabels=df2.index, yticklabels=df2.columns, fmt=".5g", cbar=False, ax=ax2)
ax3 = plt.subplot(2, 2, 3)
ax3.set_title('20D-Chg', fontdict={'fontsize':9})
sns.heatmap(df3.transpose(), cmap= 'vlag_r', linewidths=1, annot=df3.transpose(), xticklabels=df1.index, yticklabels=df1.columns, fmt=".5g", cbar=False, ax=ax3)
ax4 = plt.subplot(2, 2, 4)
ax4.set_title('1Y-Chg', fontdict={'fontsize':9})
sns.heatmap(df4.transpose(), cmap= 'vlag_r', linewidths=1, annot=df4.transpose(), xticklabels=df1.index, yticklabels=df1.columns, fmt=".5g", cbar=False, ax=ax4)
plt.show()


















