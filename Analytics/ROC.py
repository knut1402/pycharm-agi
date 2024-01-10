###### ROC testing

### USD
### List of instr
t1 = ['NAPMPMI Index', 'NAPMNMI Index', 'CHPMINDX Index', 'COMHISMN Index','OUTFGAF Index', 'OUMFNOF Index','RCHSINDX Index', 'EMPRGBCI Index', 'KCLSSACI Index', 'DFEDGBA Index',
      'CONSSENT Index', 'CONCCONF Index', 'SBOITOTL Index', 'USHBMIDX Index', 'RSTAXAGM Index', 'CGNOXAI% Index', 'JOLTTOTL Index', 'NHSPSTOT Index', 'NHSPATOT Index', 'ETSLTOTL Index']

t1 = ['OEUSKLAC Index', 'IP Index', 'USTBEXP Index', 'USTBIMP Index', 'RSTAXABG Index', 'OEUSDHAO Index', 'OEUSLCAC Index', 'NFP T Index', 'NFP P Index', 'USWHTOT Index', 'AWE TOTL Index', 
      'JOLTTOTL Index', 'EMDINP1M Index', 'PCE CONC Index', 'RPCEDGDS Index', 'PCE SRVC Index', 'PIDSDCWT Index', 'RSTATOTL Index', 'MBAVPRCH Index', 'SAARTOTL Index', 'CPTICHNG Index', 
      'TMNOTOT Index', 'CGNOXAIR Index', 'DGNOTOT Index', 'RAILTRAF Index', 'CNSTTOTA Index', 'NAPMPMI Index', 'NAPMNMI Index', 'CHPMINDX Index', 'COMHISMN Index','OUTFGAF Index', 
      'OUMFNOF Index','RCHSINDX Index', 'EMPRGBCI Index', 'KCLSSACI Index', 'DFEDGBA Index', 'CONSSENT Index', 'CONCCONF Index', 'SBOITOTL Index', 'USHBMIDX Index', 'NHSPSTOT Index', 
      'NHSPATOT Index', 'ETSLTOTL Index']

l1 = ['OECD Lead Ind', 'Ind Prod', 'Exports', 'Imports', 'Retail Sales', 'OECD Mfg Conf', 'OECD Cons Conf', 'NFP Total', 'NFP Private', 'AWE: Priv Prod', 'AWE: Total', 
      'JOLTS', 'BLS Employ Diff', 'PCE', 'Real PCE: Goods', 'Real PCE: Serv', 'Pers Disp Inc', 'Adj Retail & Food', 'MBA', 'Autos Sales', 'Cap Util', 
      'Mfg: New Orders', 'Capital Goods: New Orders', 'Durable Goods: New Orders', 'Freight Carloads', 'Construct. Spending', 'ISM Mfg', 'ISM Serv', 'Chicago PMI', 'ISM: New Orders', 'Philly Fed',
      'Philly FeD: New Orders', 'Richmond Fed', 'Empire', 'Kansas City Fed', 'Dallas Fed', 'UoM', 'Conf Board', 'NFIB', 'NAHB', 'New Homes', 
      'Building Permits', 'Exising Homes']


t1 = ['OEUSKLAC Index', 'IP  YOY Index', 'USTBEXPY Index', 'USTBIMPY Index', 'RSTAABG% Index','NAPMPMI Index', 'NAPMNMI Index','OEUSDHAO Index', 'OEUSLCAC Index', 'NFP TYOY Index', 'NFP PYOY Index',
      'USWHTOT Index', 'USWEYOY Index', 'JOLTTOTL Index', 'EMDINP1M Index', 'PCE CHY% Index', 'RPCEDGDS Index', 'PCE SRVC Index', 'PIDSCWT% Index', 'RSTAYOY Index', 'MBAVPRCH Index',
      'SAARTOTL Index', 'CPTICHNG Index', 'TMNOYOY Index', 'CGNOXAIR Index', 'DGNOTOT Index', 'RAILTRAF Index', 'CNSTTYOY Index']
l1 = ['OECD Lead Ind', 'Ind Prod', 'Exports', 'Imports', 'Retail Sales**', 'ISM Mfg', 'ISM Serv', 'OECD Mfg Conf**', 'OECD Cons Conf**', 'NFP Total', 'NFP Private',
      'AWE: Priv Prod**', 'AWE: Total', 'JOLTS**', 'BLS Employ Diff', 'PCE', 'Real PCE: Goods**', 'Real PCE: Serv**', 'Pers Disp Inc', 'Adj Retail & Food', 'MBA**',
      'Autos Sales**', 'Cap Util**', 'Mfg: New Orders', 'Capital Goods: New Orders**', 'Durable Goods: New Orders**', 'Freight Carloads***', 'Const Spending']

#### Augmented Growth 
t1 = ['OEUSKLAC Index', 'IP Index', 'USTBEXP Index', 'USTBIMP Index', 'RSTAXABG Index', 'OEUSDHAO Index', 'OEUSLCAC Index', 'NFP T Index', 'NFP P Index', 'USWHTOT Index', 'AWE TOTL Index', 
      'JOLTTOTL Index', 'EMDINP1M Index', 'PCE CONC Index', 'RPCEDGDS Index', 'PCE SRVC Index', 'PIDSDCWT Index', 'RSTATOTL Index', 'MBAVPRCH Index', 'SAARTOTL Index', 'CPTICHNG Index', 
      'TMNOTOT Index', 'CGNOXAIR Index', 'DGNOTOT Index', 'RAILTRAF Index', 'CNSTTOTA Index', 'NAPMPMI Index', 'NAPMNMI Index', 'CHPMINDX Index', 'COMHISMN Index','OUTFGAF Index', 
      'OUMFNOF Index','RCHSINDX Index', 'EMPRGBCI Index', 'KCLSSACI Index', 'DFEDGBA Index', 'CONSSENT Index', 'CONCCONF Index', 'SBOITOTL Index', 'USHBMIDX Index', 'NHSPSTOT Index', 
      'NHSPATOT Index', 'ETSLTOTL Index']

l1 = ['OECD Lead Ind', 'Ind Prod**', 'Exports**', 'Imports**', 'Retail Sales**', 'OECD Mfg Conf**', 'OECD Cons Conf**', 'NFP Total**', 'NFP Private**', 'AWE: Priv Prod**', 'AWE: Total**', 
      'JOLTS**', 'BLS Employ Diff', 'PCE**', 'Real PCE: Goods**', 'Real PCE: Serv**', 'Pers Disp Inc**', 'Adj Retail & Food**', 'MBA**', 'Autos Sales**', 'Cap Util**', 
      'Mfg: New Orders**', 'Capital Goods: New Orders**', 'Durable Goods: New Orders**', 'Freight Carloads***', 'Construct. Spending**', 'ISM Mfg', 'ISM Serv', 'Chicago PMI', 'ISM: New Orders', 'Philly Fed',
      'Philly Fed: New Orders', 'Richmond Fed', 'Empire', 'Kansas City Fed', 'Dallas Fed', 'UoM', 'Conf Board', 'NFIB', 'NAHB', 'New Homes**', 
      'Building Permits**', 'Exising Homes']

#### Soft Data Focus
t1 = ['RSTAXABG Index', 'JOLTTOTL Index',  'MBAVPRCH Index', 'SAARTOTL Index', 'NAPMPMI Index', 'NAPMNMI Index', 'CHPMINDX Index', 'COMHISMN Index','OUTFGAF Index', 
      'OUMFNOF Index','RCHSINDX Index', 'EMPRGBCI Index', 'KCLSSACI Index', 'DFEDGBA Index', 'CONSSENT Index', 'CONCCONF Index', 'SBOITOTL Index', 'USHBMIDX Index', 'NHSPSTOT Index', 'NHSPATOT Index', 'ETSLTOTL Index']

l1 = ['Retail Sales', 'JOLTS', 'MBA', 'Autos Sales', 'ISM Mfg', 'ISM Serv', 'Chicago PMI', 'ISM: New Orders', 'Philly Fed',
      'Philly Fed: New Orders', 'Richmond Fed', 'Empire', 'Kansas City Fed', 'Dallas Fed', 'UoM', 'Conf Board', 'NFIB', 'NAHB', 'New Homes', 'Building Permits', 'Exising Homes']


#### Inflation Agent
t2 = ['CPI YOY Index', 'CPI XYOY Index', 'PPI YOY Index', 'FDIUFDYO Index', 'CRB CMDT Index', 'CRB FOOD Index','CRB RIND Index', 'CPRFFOOD Index','CPRPENER Index', 'CPRPCXFE Index', 'CPRHHHFO Index', 'CPRATOT Index',
      'CPIQTCMN Index', 'CPRMCMDY Index', 'CPIQRECN Index', 'CPIQECCN Index', 'CPRFAB Index', 'CPRPSXEN Index', 'CPRHSHLT Index', 'CPRHWSTC Index', 'CPRMSERV Index', 'CPRSTRAN Index',
      'CPIQRESN Index', 'CPIQECSN Index', 'PCE DEF Index', 'PCE CORE Index', 'SBOIPRIC Index', 'NAPMPRIC Index', 'NAPMNPRC Index']
l2 = ['CPI', 'Core CPI', 'PPI', 'PPI: Final Demand', 'CRB: All**', 'CRB: Food**', 'CRB: Raw**', 'CPI: Food**', 'CPI: Energy**', 'CPI: Comm ex Energy**', 'CPI: Household**', 'CPI: Apparel**',
      'CPI: Transport Comm**', 'CPI: Medical Comm**', 'CPI: Recreation Comm**', 'CPI: Education Comm**', 'CPI: Alcohol**', 'CPI: Consumer Serv**', 'CPI: Shelter**', 'CPI: Utilities**', 'CPI: Medical**', 'CPI: Transport**',
      'CPI: Recreation**', 'CPI: Education**', 'PCE**', 'Core PCE**', 'NFIB: Higher Prices', 'ISM Mfg: Prices', 'ISM Serv: Prices']


d2 = {}

t2 = []
t3 = []
for i in np.arange(len(t1)):
    t2 = t2 + [con.ref(t1[i] , 'NAME')['value'][0]] 

t2 = l1 + ['Average']

for i in np.arange(len(t1)):
    df1 = con.bdh(t1[i] , 'PX_LAST', '20000101', '20230115', longdata = True)
    df1.index = df1['date']
    
    #### Dealing with weekly data: MBA, Freight
    if t1[i] in ['MBAVPRCH Index', 'RAILTRAF Index']:
        df1 = df1.resample('M').last()
    
    ###### remove COVID period
#    df1 = df1[((df1.index < '2020-03-30') | (df1.index > '2021-12-15'))]
#    df1 = df1[(df1.index > '2012-03-15')]            ###### only post covid

    ##### projection 6m
    new_dates = pd.DatetimeIndex([df1.index[-1] + pd.offsets.MonthEnd(n=i) for i in range(1,7)])
    new_index = df1.index.union(new_dates).unique().sort_values()
    df1 = df1.reindex(new_index).ffill()
    #####

    df1['p1'] = df1['value'].diff(periods = 6)
    df1['ROC'] = df1['p1'].diff(periods = 3)
    df1['z-score'] = np.repeat(0.0, len(df1))
    df1['z-score'][10:] =  zscore(df1['ROC'][10:])
    
    t3 = t3 + [np.round(df1['p1'][-9]+df1['value'][-12],1)]
    d2[t1[i]] = df1


df2 = pd.DataFrame(columns= t1)
for i in np.arange(len(t1)):
    df2[t1[i]] = d2[t1[i]]['z-score'][-250:]

#for i in t1:
#    print(i, df2[i].isna().sum())

df2['Avg'] = df2.mean(axis=1)
#df2[-25:].index.strftime(('%b-%Y'))

nyrs = 5
scaled_df = minmax_scale(df2)
fig, axs = plt.subplots(1, 1, figsize=(20, 10))
ax1 = plt.subplot(1, 1, 1)
#ax1.set_title('Curve', fontdict={'fontsize':9})
sns.heatmap(scaled_df[(nyrs*-12):].T, cmap='vlag_r', linewidths=1.0, xticklabels=df2[(nyrs*-12):].index.strftime(('%b-%y')), yticklabels=t2, fmt=".5g", cbar=False, ax=ax1)
ax1.xaxis.set_tick_params(labelsize=9)
ax1.yaxis.set_tick_params(labelsize=8.5)

ax2 = ax1.twinx()
ax2.set_ylim(0, 1) 
ax2.get_yaxis().set_visible(False)
ax2.grid(True)
ax2.vlines(len(df2[(nyrs*-12):])-6, 0,1.0, color='k', linestyles='dashed')

ax3 = ax1.twinx()
ax3.set_ylim(0, len(t2)) 
ax3.set_yticks(np.arange(1.5,len(t3)+1.5,1))
ax3.set_yticklabels(t3[::-1])
ax3.yaxis.set_tick_params(labelsize=8)



nyrs = 9
scaled_df = minmax_scale(df2[['PCE CONC Index','IP Index']])
fig, axs = plt.subplots(1, 1, figsize=(20, 10))
ax1 = plt.subplot(1, 1, 1)
#ax1.set_title('Curve', fontdict={'fontsize':9})
sns.heatmap(scaled_df[(nyrs*-12):], cmap='vlag_r', linewidths=1.0, yticklabels=df2[(nyrs*-12):].index.strftime(('%b-%y')), xticklabels=['PCE', 'IP'], fmt=".5g", cbar=False, ax=ax1)
ax1.xaxis.set_tick_params(labelsize=9)
ax1.yaxis.set_tick_params(labelsize=5)

sns.heatmap([df2['PCE CONC Index']],cmap='vlag_r')
df2['PCE CONC Index'][-50:]

####### Applying a Gaussian Mixture
from sklearn.mixture import GaussianMixture

X = df2[-225:-1]
#### remove NaN
t3 = t1[:10]+t1[11:24]+t1[25:]
X = X[t3]

#for i in t3:
#    print(i, X[i].isna().sum())

#### Hom many components? 
n_components = np.arange(1, 10)
models = [GaussianMixture(n, covariance_type='full', random_state=0).fit(X) for n in n_components]

plt.plot(n_components, [m.bic(X) for m in models], label='BIC')
plt.plot(n_components, [m.aic(X) for m in models], label='AIC')
plt.legend(loc='best')
plt.xlabel('n_components')

###
gmm = GaussianMixture(n_components=2, covariance_type='full').fit(X)
labels = gmm.predict(X)
plt.scatter(X.iloc[:, 38], X.iloc[:, 29], c=labels, s=40, cmap='viridis');

l1

colors = ['red','blue','green','pink']
colors2 = [colors[labels[i]] for i in np.arange(len(labels))]
plt.figure(figsize=[14,10])
plt.scatter(X.index, X[t1[38]], c= colors2)

















### AUD
t1 = ['AUBARSM Index', 'AUBAC Index', 'RPAUMED Index', 'MPMIAUMA Index','MPMIAUSA Index', 'AUCHIYOY Index', 'AUCHHOBY Index', 'WMCCCONS Index', 'WMCC12Y% Index', 'WMCCHSEI Index','NABSCOND Index', 
      'NABSCONF Index', 'NABSFORD Index', 'MECCTRIM Index', 'AURSTSA Index', 'OZCACRY% Index', 'AULFANTC Index', 'AULILGM% Index']
d2 = {}

t2 = []
t3 = []
for i in np.arange(len(t1)):
    t2 = t2 + [con.ref(t1[i] , 'NAME')['value'][0]] 

t2 = t2 + ['Average']

for i in np.arange(len(t1)):
    df1 = con.bdh(t1[i] , 'PX_LAST', '20000101', '20221230', longdata = True)
    df1.index = df1['date']
   
    ##### projection 6m
    new_dates = pd.DatetimeIndex([df1.index[-1] + pd.offsets.MonthEnd(n=i) for i in range(1,7)])
    new_index = df1.index.union(new_dates).unique().sort_values()
    df1 = df1.reindex(new_index).ffill()
    #####

    df1['p1'] = df1['value'].diff(periods = 6)
    df1['ROC'] = df1['p1'].diff(periods = 3)
    df1['z-score'] = np.repeat(0.0, len(df1))
    df1['z-score'][10:] =  zscore(df1['ROC'][10:])
    
    t3 = t3 + [np.round(df1['p1'][-9]+df1['value'][-12],1)]
    d2[t1[i]] = df1

df2 = pd.DataFrame(columns= t1)
for i in np.arange(len(t1)):
    df2[t1[i]] = d2[t1[i]]['z-score'][-250:]

df2['Avg'] = df2.mean(axis=1)

#df2[-25:].index.strftime(('%b-%Y'))

scaled_df = minmax_scale(df2)
fig, axs = plt.subplots(1, 1, figsize=(30, 12))
ax1 = plt.subplot(1, 1, 1)
#ax1.set_title('Curve', fontdict={'fontsize':9})
sns.heatmap(scaled_df[-100:].T, cmap='vlag_r', linewidths=1.0, xticklabels=df2[-100:].index.strftime(('%b-%y')), yticklabels=t2, fmt=".5g", cbar=False, ax=ax1)
ax1.xaxis.set_tick_params(labelsize=9)
ax1.yaxis.set_tick_params(labelsize=8.5)

ax2 = ax1.twinx()
ax2.set_ylim(0, 1) 
ax2.get_yaxis().set_visible(False)
ax2.grid(True)
ax2.vlines(len(df2[-100:])-6, 0,1.0, color='k', linestyles='dashed')

ax3 = ax1.twinx()
ax3.set_ylim(0, len(t2)) 
ax3.set_yticks(np.arange(1.5,len(t3)+1.5,1))
ax3.set_yticklabels(t3[::-1])
ax3.yaxis.set_tick_params(labelsize=8)


















