######

import sklearn
from sklearn import datasets
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import RepeatedKFold
from sklearn.model_selection import RandomizedSearchCV, GridSearchCV
from sklearn.model_selection import StratifiedKFold


t1 = ['JOLTTOTL Index',  'QUITFERS Index', 'OUTFNEF Index', 'KCLSNSAE Index','CONSUEXR Index', 'DFEDEMP# Index', 'EMPRNEMP Index', 
      'CONCLBDF Index', '.ATWGSWST U Index',  'NAPMEMPL Index', 'NAPMNEMP Index', 'NFP TCH Index']     
##### Atlanta Fed Wage switcher vs stayer: .ATWGSWST U Index = WGTRSWCH Index - WGTRSTAY Index 

df2 = pd.DataFrame()
d2 = {}
t2 = []
for i in np.arange(len(t1)):
    t2 = t2 + [con.ref(t1[i] , 'NAME')['value'][0]] 

for i in np.arange(len(t1)):
    df1 = con.bdh(t1[i] , 'PX_LAST', '20040101', '20230203', longdata = True)
    df1.index = df1['date']    
    df2[t1[i]] = df1['value']

##### adding continuing claims
df3 = con.bdh('INJCSP Index' , 'PX_LAST', '20040101', '20230203', longdata = True)
df3.index = df3['date']
df3 = df3.resample('M').first()
df3['INJCSP Index'] = df3['value']
df3 = df3['INJCSP Index']

df4 = df2.merge(df3, how='outer', left_index=True, right_index=True)
df4 = df4.dropna()
t2 = t1[:-1]+['INJCSP Index']+[t1[-1]]
df4 = df4[t2]

####### without claims
#t2=t1
#df4 = df2
#df4 = df4.dropna()

#df4[:50]
#df2[-10:]
##### remove outliers
df4 = df4[(df4[t1[-1]] < 1000) & (df4[t1[-1]] > -1000)]
##### get x_train, x_test, y_train, y_test
df5 = [con.ref(t2[i] , 'PX_LAST')['value'][0] for i in np.arange(len(t2))]

x_train = df4[t2[:-1]][:-1]
y_train = df4[t2[-1]].shift(-1)[:-1]

x_test = df4[t2[:-1]][-50:]
y_test = df4[t2[-1]][-50:]

x_test2 = df5[:-1]

##### random forest 
clf = RandomForestRegressor(n_estimators = 2500, max_features=5, oob_score = True, random_state=0)
clf.fit(x_train, y_train)

clf.get_params()
clf.score(x_train, y_train)
clf.oob_score_

np.mean((y_train - clf.oob_prediction_)**2)

y_hat = clf.predict(np.array(x_test))
np.mean((y_test - y_hat)**2)

plt.figure(figsize=[14,10])
plt.scatter(y_hat, y_test)
xpoints = ypoints = plt.xlim()
plt.plot(xpoints, ypoints, linestyle='-', color='k', lw=2, scalex=False, scaley=False)

y_hat2 = clf.predict(np.array(x_test2).reshape(1,-1))


##### boosting
### hyperparameter tuning
for i in np.array([0.001,0.005,0.01,0.05,0.1]):
#for i in np.arange(0.2,0.8,0.1):
    model = XGBRegressor(n_estimators=5000, max_depth = 3, learning_rate=0.005, subsample = i)
    cv = RepeatedKFold(n_splits = 10, n_repeats =3, random_state =1)
    scores = cross_val_score(model, x_train, y_train, scoring = 'neg_mean_squared_error', cv = cv)
    print (i ,np.mean(-scores))


params = {
        'min_child_weight': [1, 5, 10],
        'gamma': [0.5, 1, 1.5, 2, 5],
        'subsample': [0.2, 0.4, 0.6, 0.8, 1.0],
        'colsample_bytree': [0.6, 0.8, 1.0],
        'max_depth': [3, 4, 5, 6],
        'learning_rate' : [0.001,0.005,0.01,0.05,0.1]
        }

folds = 3
param_comb = 10
skf = StratifiedKFold(n_splits=folds, shuffle = True, random_state = 1001)

random_search = RandomizedSearchCV(model, param_distributions=params, n_iter=param_comb, scoring='neg_mean_squared_error', n_jobs=2, cv=skf.split(x_train,y_train), verbose=3, random_state=1001 )

# Here we go
random_search.fit(x_train, y_train)


print('\n All results:')
print(random_search.cv_results_)
print('\n Best estimator:')
print(random_search.best_estimator_)
print('\n Best normalized gini score for %d-fold search with %d parameter combinations:' % (folds, param_comb))
print(random_search.best_score_ * 2 - 1)
print('\n Best hyperparameters:')
print(random_search.best_params_)
results = pd.DataFrame(random_search.cv_results_)
results.to_csv('xgb-random-grid-search-results-01.csv', index=False)



model2 = random_search.best_estimator_
model2.fit(x_train, y_train)
y_hat = model2.predict(x_test)
np.mean((y_test - y_hat)**2)

plt.figure(figsize=[8,6])
plt.scatter(y_hat, y_test)
xpoints = ypoints = plt.xlim()
plt.plot(xpoints, ypoints, linestyle='-', color='k', lw=2, scalex=False, scaley=False)

df_importance2 = pd.DataFrame(model2.feature_importances_, index = t2[:-1])


y_hat2 = model2.predict(np.array(x_test2).reshape(1,-1))



#### select model
model = XGBRegressor(n_estimators=10000, max_depth = 4, learning_rate=0.01, subsample = 0.6)
model.fit(x_train, y_train)
y_hat = model.predict(x_test)
np.mean((y_test - y_hat)**2)

plt.figure(figsize=[8,6])
plt.scatter(y_hat, y_test)
xpoints = ypoints = plt.xlim()
plt.plot(xpoints, ypoints, linestyle='-', color='k', lw=2, scalex=False, scaley=False)

df_importance = pd.DataFrame(model.feature_importances_, index = t2[:-1])

y_hat2 = model.predict(np.array(x_test2).reshape(1,-1))


import networkx as nx

df = model._Booster.trees_to_dataframe()
df = df[:25]

s1= df[['ID','Split']].set_index('ID').to_dict()['Split']

# Create graph
G = nx.Graph()
# Add all the nodes
G.add_nodes_from(df.ID.tolist())
# Add the edges. This should be simpler in Pandas, but there seems to be a bug with df.apply(tuple, axis=1) at the moment.
yes_pairs = df[['ID', 'Yes']].dropna()
no_pairs = df[['ID', 'No']].dropna()
yes_edges = [tuple([i[0], i[1]]) for i in yes_pairs.values]
no_edges = [tuple([i[0], i[1]]) for i in no_pairs.values]
G.add_edges_from(yes_edges + no_edges)


nx.draw(G)
nx.draw_networkx(G)

nx.draw_networkx_nodes(G, pos=nx.spring_layout(G), nodelist=[4,5])



df = model._Booster.trees_to_dataframe()
G = nx.DiGraph()
G.add_nodes_from(df.ID.tolist())

yes_edges = df[['ID', 'Yes', 'Feature', 'Split']].dropna()
yes_edges['label'] = yes_edges.apply(lambda x: "({feature} > {value:.2f} or {feature} = 999999)".format(feature=x['Feature'], value=x['Split']), axis=1)

no_edges = df[['ID', 'No', 'Feature', 'Split']].dropna()
no_edges['label'] = no_edges.apply(lambda x: "({feature} < {value:.2f})".format(feature=x['Feature'], value=x['Split']), axis=1)

for v in yes_edges.values:
    G.add_edge(v[0],v[1], feature=v[2], expr=v[4])
    
for v in no_edges.values:
    G.add_edge(v[0],v[1], feature=v[2], expr=v[4])

leaf_node_values = {i[0]:i[1] for i in df[df.Feature=='Leaf'][['ID','Gain']].values}    
    
roots = []
leaves = []
for node in G.nodes :
    if G.in_degree(node) == 0 : # it's a root
        roots.append(node)
    elif G.out_degree(node) == 0 : # it's a leaf
        leaves.append(node)
        
paths = []
for root in roots :
    for leaf in leaves :
        for path in nx.all_simple_paths(G, root, leaf) :
            paths.append(path)
    
pred_conditions = []
for path in paths:
    parts = []
    for i in range(len(path)-1):
        parts.append(G[path[i]][path[i+1]]['expr'])
    pred_conditions.append("if " + " and ".join(parts) + " then {value:.4f}".format(value=leaf_node_values.get(path[-1])))






#################### trying to plot 
from xgboost import plot_tree
import graphviz

plot_tree(model, num_trees=2)
plt.show()


import os
import graphviz
os.environ["PATH"] += os.pathsep + 'C:\winapp\Anaconda\Library\bin\graphviz'
graph_data = "your  graph data"
fie_ext = 'png'
temp_img = 'temp_file'
temp_img_name = "".join([temp_img, '.'+fie_ext])
my_graph= graphviz.Source(graph_data)
my_graph.render(temp_img,format=fie_ext, view=False)


# dump it to a text file
model.get_booster().dump_model('xgb_model.txt', with_stats=True)
# read the contents of the file
with open('xgb_model.txt', 'r') as f:
    txt_model = f.read()
print(txt_model)



fig, ax = plt.subplots(figsize=(30, 30))
plot_tree(grid.best_estimator_, num_trees=4, ax=ax)
plt.show()







#### timer
def timer(start_time=None):
    if not start_time:
        start_time = datetime.now()
        return start_time
    elif start_time:
        thour, temp_sec = divmod((datetime.datetime.now() - start_time).total_seconds(), 3600)
        tmin, tsec = divmod(temp_sec, 60)
        print('\n Time taken: %i hours %i minutes and %s seconds.' % (thour, tmin, round(tsec, 2)))

