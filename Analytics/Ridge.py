##### Ridge 
from sklearn.linear_model import RidgeCV

d1 = '20200101'
d2 = '20221211'


x1 = np.array(con.bdh('G0016 1M5Y BLC2 Curncy', 'PX_LAST', d1, d2, longdata = True)['value'])
x2 = np.array(con.bdh('G0016 1M10Y BLC2 Curncy', 'PX_LAST', d1, d2, longdata = True)['value'])
x3 = np.array(con.bdh('G0016 1M30Y BLC2 Curncy', 'PX_LAST', d1, d2, longdata = True)['value'])

#x4 = np.array(con.bdh('G0016 2Y2Y BLC2 Curncy', 'PX_LAST', d1, d2, longdata = True)['value'])
x5 = np.array(con.bdh('RXAISP Curncy', 'PX_LAST', d1, d2, longdata = True)['value'])
x6 = np.array(con.bdh('UBAISP Curncy', 'PX_LAST', d1, d2, longdata = True)['value'])

#x4 = np.array(con.bdh('USSN0F10 BBIR Curncy', 'PX_LAST', d1, d2, longdata = True)['value'])

x4= 1*(x5-x6)

y = 100*(x3-x2)

x = x4.reshape(len(x4),1)
y = y.reshape(len(y),1)

alphas = np.linspace(0.000001, 1, 200)
clf = RidgeCV(alphas).fit(x, y)

clf.alpha_
clf.score(x, y)

x1a = np.linspace(min(x), max(x), 200)
x1b = np.repeat(1, len(x1a))


y2 = [clf.predict( [ x1a[i] ] ) for i in np.arange(len(x1a))]
y3 = flat_lst(flat_lst(y2))


fig = plt.figure(figsize=[15,10])
plt.scatter(x[-10:],y[-10:], s=40, marker = 'x', c = 'red' )
plt.scatter(x[:-10],y[:-10], s=3, c = np.arange(len(x[:-10])), cmap ='cool')
plt.plot(x1a,y3, c = 'red')
plt.ylabel('Ger: 10s-30s')
plt.xlabel('Ger: 2y2y')
plt.title('2006-live')


cax = plt.axes([0.92, 0.58, 0.025, 0.3])
plt.colorbar(cax=cax)



