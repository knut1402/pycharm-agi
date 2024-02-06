#### Macro42 
#### Growth Agent

########## From Spreadsheet
data = pd.ExcelFile("./DataLake/eco_master.xlsx")
data_df = pd.read_excel(data,"EcoData")

data_df[:20]

############# Run analysis

us = get_data(data_df, 'US', '20000101', end=-1, cat1='Activity', cat2='all', change=6, roc =3, zs_period = 20)
ez = get_data(data_df, 'EZ', '20000101', end=-1, cat1='Activity', cat2='all', change=6, roc =3, zs_period = 20)
uk = get_data(data_df, 'UK', '20000101', end=-1, cat1='Activity', cat2='all', change=6, roc =3, zs_period = 20)

us.raw
us.zs_pct

#### optional save to csv
us.zs_pct.to_excel("usdata_zs.xlsx")


import matplotlib
matplotlib.get_backend()
plt.interactive(False)
data_heatmap([uk.df_pct], n=5 , inst = ['GT10 govt'], minmax=True, fsize = [5,7])

plt.show()

data_heatmap([us.zs_pct], n=3 , minmax=True, fsize = [50,20])
data_heatmap([ez.zs_pct], n=5 , minmax=True, fsize = [50,50])
data_heatmap([uk.zs_pct], n=4 , minmax=True, fsize = [50,50])
plt.show()

data_heatmap([us.zs_pct], n=4 , inst = ['GT10 Govt'], minmax=True, fsize = [50,50])

data_heatmap([us.zs_raw], n=5 , fsize = [10,27])
data_heatmap([us.zs_pct_roc], n=5 , fsize = [15,30])


run_gmm(us.zs_pct, 6, ['GT10 Govt', 'USFS055 Curncy'], zs_excl = us.zs_excl, feat_plot = 0, is_zs =True)
run_gmm(us.zs_pct_roc, 6, ['GT10 Govt', 'USFS055 Curncy'], zs_excl = us.zs_excl, feat_plot = ['ISM Mfg', 'Retail Sales'], is_zs =True)


ez1 = get_data(data_df, 'EZ', '20000101', end=-1, cat1='Activity', cat2='all', change=6, roc =3, zs_period = 3)
data_heatmap([ez1.zs_pct_roc], n=5 , inst = [], minmax=True, fsize = [20,26])
run_gmm(ez1.zs_pct, 6, ['GT10 Govt'], zs_excl = ez1.zs_excl, feat_plot = 0, is_zs =True)
ez1.nantab[:40]

ge1 = get_data(data_df, 'GE', '20000101', end=-1, cat1='all', cat2='all', change=6, roc =3, zs_period = 2)
data_heatmap([ge1.zs_pct], n=5 , inst = ['GT10 govt'], minmax=True, fsize = [18,22])
run_gmm(ge1.zs_pct, 6, ['GTDEM5Y Govt'], zs_excl = ge1.zs_excl, feat_plot = ['IP','HICP: Core'], is_zs =True)

uk1 = get_data(data_df, 'UK', '20000101', end=-1, cat1='Activity', cat2='all', change=6, roc =3, zs_period = 2)
data_heatmap([uk1.zs_pct_roc], n=5 , inst = ['GBPUSD Curncy'], minmax=True, fsize = [15,30])
run_gmm(uk1.zs_pct, 6, ['GTGBP5Y Govt'], zs_excl = uk1.zs_excl, feat_plot = ['IP','CPI: Core'], is_zs =True)

uk1.raw
uk1.zs_pct

uk1.raw['CPI: Core']
uk1.nantab.sort_values('#')[-50:]

for i in uk1.zs_pct_roc.columns:
    print(i, uk1.zs_pct_roc[i].isna().sum())

 raw, df_pct, df_chg, df_roc, df_pct_roc, zs_raw, zs_pct, zs_chg, zs_roc, zs_pct_roc
 
 
 
 
 
 
#### AUD
au = get_data(data_df, 'AU', '20000101', end=-1, cat1='all', cat2='all', change=6, roc = 3, zs_period = 24)
au.raw
au.zs_pct


data_heatmap([au.zs_pct], n=6 , minmax=True, fsize = [15,10])
data_heatmap([au.zs_pct_roc], n=3 , minmax=True, fsize = [15,10])
data_heatmap([au.zs_chg], n=3 , minmax=True, fsize = [15,10])
 
 
 
 
 
 
 
 
 
####################### run an SVM model on Growth Agent
#### Check for NaNs
for i in l1:
    print(i, df1[i].isna().sum())

df_g =  df1.drop(['Freight Carloads***'], axis=1).dropna()

y_label = []
for i in np.arange(len(df_g)):
    if df_g['OECD Lead Ind'][i] > 100:
        y_label.append(1)
    else:
        y_label.append(0)

X = df_g.drop(['OECD Lead Ind'], axis = 1)


from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

clf = make_pipeline( StandardScaler(), SVC(C = 1.0, kernel = 'rbf', gamma = 'auto', probability = 1))
clf.fit(X, y_label)

clf.score(X, y_label)
y_pred  = pd.DataFrame(clf.predict(X), index = X.index)

y_pred[-50:]

X.index[ np.array(y_pred[0])  != y_label]


y_proba = clf.predict_proba(X)

plt.figure(figsize=[14,10])
plt.plot(df_g.index, y_proba[:,0])



fig, axs = plt.subplots(1, 1, figsize=(20, 10))
ax1 = plt.subplot(1, 1, 1)
ax1.plot(df_g.index, y_proba[:,1])
ax2 = ax1.twinx()
#ax2.set_ylim(0, 1) 
#ax2.get_yaxis().set_visible(False)
ax2.grid(True)
ax2.plot(df_g.index, df_g['OECD Lead Ind']-99.5,  c = 'red' )


colors = ['red','blue','green','pink']
colors2 = [colors[y_pred[i]] for i in np.arange(len(y_pred))]

plt.figure(figsize=[14,10])
plt.scatter(X.index, X[l1[1]], c= colors2)

































##################################### sundry
#### Get data
df1 = pd.DataFrame(columns=l1)
for i in np.arange(len(t1)):
        df2 = con.bdh(t1[i] , 'PX_LAST', '20000101', '20230125', longdata = True)
        df2.index = df2['date']
        df1[l1[i]] = df2['value']

#### Check for NaNs
for i in l1:
    print(i, df1[i].isna().sum())

#### Dealing with weekly data: MBA, Freight
for i in ['MBAVPRCH Index', 'RAILTRAF Index']:
    df3 = con.bdh(i , 'PX_LAST', '20000101', '20230115', longdata = True)
    df3.index = df3['date']
    df3 = df3.resample('M').last()
    df1[l1[t1.index(i)]] = df3['value']

#### Deal with YoY transform
t2 = [s for s in l1 if '**' in s]
for i in np.arange(len(t2)):
    df1[t2[i]] = np.round(100*df1[t2[i]].pct_change(periods=12),2)



#### Changes
df5 = pd.DataFrame(columns=l1)
df6 = pd.DataFrame(columns=l1)
for i in l1:
    df5[i] = df1[i].diff(periods = 6)
    df6[i] = df5[i].diff(periods = 3)



##### find z-scores 
l2 = l1[:-2]+[l1[-1]]
df4 = df1[l2]
df4 = df4.dropna()

for i in l2:
    df4[i] = zscore(df4[i])


### heatmaps
nyrs = 10
scaled_df = minmax_scale(df1)
#scaled_df[:,-(len(t1)-len(t2)):] = 1-scaled_df[:,-(len(t1)-len(t2)):]   ###### turning inflation direction
fig, axs = plt.subplots(1, 1, figsize=(18, 8))
ax1 = plt.subplot(1, 1, 1)
sns.heatmap(scaled_df[(nyrs*-12):].T, cmap='vlag_r', linewidths=1.0, xticklabels=df1[(nyrs*-12):].index.strftime(('%b-%y')), yticklabels=l1, fmt=".5g", cbar=False, ax=ax1)
ax1.xaxis.set_tick_params(labelsize=9)
ax1.yaxis.set_tick_params(labelsize=8.5)

#sns.heatmap([df1['OECD Lead Ind']],cmap='vlag_r')
#sns.heatmap([df4['OECD Lead Ind']],cmap='vlag_r')


##### Classification = GMM

df_ex_freight = df1.drop(['Freight Carloads***'], axis=1)
X = df_ex_freight.dropna()

gmm = GaussianMixture(n_components=4, covariance_type='full').fit(X)
labels = gmm.predict(X)
unique, counts = np.unique(labels, return_counts=True)
print(np.asarray((unique, counts)).T)

plt.scatter(X.iloc[:, 1], X.iloc[:, 11], c=labels, s=40, cmap='viridis');

#### Hom many components?
n_components = np.arange(1, 10)
models = [GaussianMixture(n, covariance_type='full', random_state=0).fit(X) for n in n_components]

plt.plot(n_components, [m.bic(X) for m in models], label='BIC')
plt.plot(n_components, [m.aic(X) for m in models], label='AIC')
plt.legend(loc='best')
plt.xlabel('n_components')

##### label plot of feature
colors = ['red','blue','green','pink']
colors2 = [colors[labels[i]] for i in np.arange(len(labels))]

plt.figure(figsize=[14,10])
plt.scatter(X.index, X[l1[1]], c= colors2)

##### label plot of UST 10s
t1 = con.bdh('GT10 Govt' , 'PX_LAST', '20000101', '20230125', longdata = True)
t1.index = t1['date']
t1 = t1.resample('M').last()
t1 = t1.loc[X.index]

plt.figure(figsize=[14,10])
plt.scatter(t1.index, t1['value'], c= colors2)







