###### boosting lab

import sklearn
from sklearn import datasets
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import RepeatedKFold


boston = datasets.load_boston()
boston

X = boston.data
y = boston.target

X.shape
y.shape

x_train, x_test, y_train, y_test = train_test_split(X, y, train_size = 0.5)

x_train.shape
x_test.shape

#### no_of_trees = number of estimators
clf = RandomForestRegressor(n_estimators = 500, max_features=13, oob_score = True, random_state=0)
clf.fit(x_train, y_train)

clf.get_params()
clf.score(x_train, y_train)
clf.oob_score_

np.mean((y_train - clf.oob_prediction_)**2)

y_hat = clf.predict(x_test)
np.mean((y_test - y_hat)**2)

plt.figure(figsize=[8,6])
plt.scatter(y_hat, y_test)
xpoints = ypoints = plt.xlim()
plt.plot(xpoints, ypoints, linestyle='-', color='k', lw=2, scalex=False, scaley=False)


##### changing number of features to be considered
### randomForest() uses p/3 (or log2 p) variables when building a random forest of regression trees, and p**0.5 variables when building a random forest of classication trees. 
clf = RandomForestRegressor(n_estimators = 1000, max_features=6, oob_score = True, random_state=0)
clf.fit(x_train, y_train)

clf.get_params()
clf.score(x_train, y_train)
clf.oob_score_

np.mean((y_train - clf.oob_prediction_)**2)

y_hat = clf.predict(x_test)
np.mean((y_test - y_hat)**2)

plt.figure(figsize=[14,10])
plt.scatter(y_hat, y_test)
xpoints = ypoints = plt.xlim()
plt.plot(xpoints, ypoints, linestyle='-', color='k', lw=2, scalex=False, scaley=False)


###### Boosting! 
model = XGBRegressor(n_estimators=5000, max_depth = 4, learning_rate=0.0050, subsample = 0.3)

cv = RepeatedKFold(n_splits = 10, n_repeats =3, random_state =1)
scores = cross_val_score(model, x_train, y_train, scoring = 'neg_mean_squared_error', cv = cv)
np.mean(-scores)

model.fit(x_train, y_train)
y_hat = model.predict(x_test)
np.mean((y_test - y_hat)**2)

plt.figure(figsize=[8,6])
plt.scatter(y_hat, y_test)
xpoints = ypoints = plt.xlim()
plt.plot(xpoints, ypoints, linestyle='-', color='k', lw=2, scalex=False, scaley=False)

model.feature_importances_

