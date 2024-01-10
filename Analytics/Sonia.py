# ###### GBP OIS SONIA

import pandas as pd
import numpy as np
import tia
from tia.bbg import LocalTerminal as LT
import pdblp

con = pdblp.BCon(debug=False, port=8194, timeout=5000)
con.start()

### Get bbg tickers
cb_tickers = pd.Series(['GPSF'+str(i)+'A ICPL Curncy' for i in range(1,11) ])

### Get Meeting Dates and set index

x = con.bulkref('UKBRBASE Index','ECO_FUTURE_RELEASE_DATE_LIST')['value']

y = pd.Series([ datetime.date(int(x[i][0:4]),int(x[i][5:7]),int(x[i][8:10])) for i in range(len(x)) ])
y = pd.DataFrame(y[y > (datetime.datetime.now()+pd.DateOffset(days=+1))], columns = ['Meets'])

y1 = y['Meets'].append( pd.Series( [ np.datetime64(y[-1:]['Meets'].values[0])+np.timedelta64(50*i,'D') for i in range(1, len(cb_tickers)-len(y)+1 )] ) )
y2 = pd.DataFrame(y1)

cb_index = pd.Series( [y2.iloc[i,][0].strftime('%b') +'-'+ y2.iloc[i,][0].strftime('%y') for i in range(len((y2))) ] )

y2.reset_index(inplace=True)
xx = pd.DataFrame(cb_index)
xx.reset_index(inplace=True)
xx.iloc[:,1]
y2['Dates'] = xx.iloc[:,1]
y2.set_index('Dates', inplace=True)
y2.drop(columns= ['index'], inplace = True)

y2

##### input data
ois_in = pd.DataFrame(index=cb_index)
cb_tickers.index = cb_index
ois_in['Tickers'] = cb_tickers

### Get Rates 
a = LT.get_reference_data(ois_in['Tickers'], "PX_LAST").as_frame()['PX_LAST']
ois_in = ois_in.join(a,on='Tickers')
ois_in.rename(columns = {'PX_LAST':'Sonia'}, inplace=True)


### Get Alt-Rates

base = LT.get_reference_data('UKBRBASE Index', "PX_LAST").as_frame()['PX_LAST'][0]
sonia_basis = 0.05
rate_sim1 = pd.DataFrame([base-(sonia_basis+(0.00))+(1*0.15),      #sep18
             base-(sonia_basis+(0.00))+(1*0.15),      #nov18
             base-(sonia_basis+(0.00))+(1*0.15),      #dec18
             base-(sonia_basis+(-0.15))+(1*0.25),      #jan19
             base-(sonia_basis+(-0.15))+(1*0.25),      #mar19
             base-(sonia_basis+(-0.15))+(1*0.25),      #may19
             base-(sonia_basis+(-0.15))+(1*0.25),      #jun19
             base-(sonia_basis+(-0.15))+(2*0.25),      #jul19
             base-(sonia_basis+(-0.15))+(2*0.25),      #sep19
             base-(sonia_basis+(-0.15))+(2*0.25)     ], index = cb_index) #mar20

rate_sim2 = rate_sim1[0] - [.15,.15,.15,.25,.25,.25,.25,.25,.25,.25]
ois_in['Sim1_NH'] = rate_sim2
ois_in['Sim1_H']  = rate_sim1

#ois_in['#Hikes'] = pd.Series.round(((ois_in['Rate'] - (base-sonia_basis)))/.25,2)

num_hikes = []
ois_chg = list(ois_in['Sonia'] - (base-sonia_basis))
for i in np.arange(len(ois_chg)):
    if ois_chg[i] < 0.15:
        num_hikes  = num_hikes + [ois_chg[i] / 0.15]
    else:
       num_hikes  = num_hikes + [1 + ((ois_chg[i] - 0.15) / 0.25)]
    
ois_in['#Hikes'] = np.round(num_hikes,2)


print(tabulate(ois_in[['Tickers','Sonia','#Hikes']], headers='keys', tablefmt='fancy_grid'))


#Set
ois_in['Start'] = y2.iloc[:,0]
ois_in['End'] = list(y2.iloc[:,0].shift(-1))[:-1] + list(y2.iloc[-1] + datetime.timedelta(days=50))


####################################################################################################################################################### Via Futures

f
a1
a2
manual = 0
som_me=-0.0025
som_qe=-0.0025
som_ye=-0.025
eom_me=-0.0025
eom_qe=-0.0025
eom_ye=-0.025
s='MID'

    """ Author = RS 
        a1, a2      : Fed rates + changes in-month
        manual == 1 : comparison to pre-month unchanged
        s           : FF fut bid/mid/ask
        px          : priced based on rate a1+a2
        px_unch     : price based on a1 or a1-25bps if manual == 1
        px's are net of ioer basis
        defaults: ioer = 7bps; 
                  me = qe = 1bp
                  ye = 10bps              """
    
f = 'H2'
a1 = 0.25
a2 = 0.50
sonia_basis = 0.05
    
v1 = con.ref("SFI"+str(f)+" Comdty", 'INT_RATE_FUT_START_DT')['value'][0]
v2 = con.ref("SFI"+str(f)+" Comdty", 'INT_RATE_FUT_END_DT')['value'][0]

r1 = ql.Date(v1.day,v1.month,v1.year)
r2 = ql.Date(v2.day,v2.month,v2.year)

e1 = pd.DataFrame([r1 + i] for i in range (0,r2-r1))

e1['R1'] = pd.Series([a1-sonia_basis]*(r2-r1))        
e1['R2'] = pd.Series([a1+a2-sonia_basis]*(r2-r1))


################# find cb meet date and next biz day

####### Get MPC Dates and set index
e1['Rx'] = pd.Series( dtype = float)
e1['Rx_unch'] = pd.Series( dtype = float)
    
cb_tickers = pd.Series(['GPSF'+str(i)+'A ICPL Curncy' for i in range(1,11) ])

x = con.bulkref('UKBRBASE Index','ECO_FUTURE_RELEASE_DATE_LIST')['value']

y = pd.Series([ datetime.date(int(x[i][0:4]),int(x[i][5:7]),int(x[i][8:10])) for i in range(len(x)) ])
y = pd.DataFrame(y[y > (datetime.datetime.now()+pd.DateOffset(days=-1))], columns = ['Meets'])

y1 = y['Meets'].append( pd.Series( [ y[-1:]['Meets'].values[0]+np.timedelta64(50*i,'D') for i in range(1, len(cb_tickers)-len(y)+1 )] ) )
y2 = pd.DataFrame(y1[:-1])   ###### adjust to match the broker rates dates !!

cb_index = pd.Series( [y2.iloc[i,][0].strftime('%b') +'-'+ y2.iloc[i,][0].strftime('%y') for i in range(len((y2))) ] )

y2.reset_index(inplace=True)
xx = pd.DataFrame(fomc_index)
xx.reset_index(inplace=True)
xx.iloc[:,1]
y2['Dates'] = xx.iloc[:,1]
y2.set_index('Dates', inplace=True)
y2.drop(columns= ['index'], inplace = True)

  
y3 = y2 [ (pd.to_datetime(y2[0][0:].values).year == v2.year) == True ]
if sum((pd.to_datetime(y3[0][0:].values).month == v2.month) == True) == 0:
    v5 = r2-r1+1
    v4 = pd.Series()
    v4 = [v5-1]
    r3 = ql.Date(int(v4[0]),v2.month,v2.year)
else:
    y4 = y3 [ (pd.to_datetime(y3[0][0:].values).month == v2) == True ]
    v4 = pd.to_datetime(y4[0][0:].values).day 

    r3 = ql.Date(int(v4[0]),v2,v3)
    v5 = ql.UnitedStates().advance(r3,1,ql.Days).dayOfMonth()
    
    
    if v5 < v4[0]:
        v5 = v4[0]+1
    
    e1['Rx'][0:(v5-1)] = e1['R1'][0:(v5-1)]
    e1['Rx'][(v5-1):] = e1['R2'][(v5-1):]
    e1['Rx_unch'] = e1['R1']
    #e1

#e1['Rx'].isnull().sum()

############## SoM BEING A holiday or weekend

    if v2 == 1:
        som_adj = som_ye              ## ff_ye
    elif (v2-1) % 3 and v2 != 1:
        som_adj = som_qe              ## ff_qe
    else:
        som_adj = som_me              ## ff_me


    if ql.UnitedStates().isHoliday(e1.iloc[0,0]) == True:
        if ql.UnitedStates().isHoliday(e1.iloc[1,0]) == True:
            if ql.UnitedStates().isHoliday(e1.iloc[2,0]) == True:
                if ql.UnitedStates().isHoliday(e1.iloc[3,0]) == True:
                    if ql.UnitedStates().isHoliday(e1.iloc[4,0]) == True:
                        e1['Rx'][0:5] = e1['R1'][0:5]+som_adj
                        e1['Rx_unch'][0:5] = e1['R1'][0:5]+som_adj
                    else:
                        e1['Rx'][0:4] = e1['R1'][0:4]+som_adj
                        e1['Rx_unch'][0:4] = e1['R1'][0:4]+som_adj
                else:
                    e1['Rx'][0:3] = e1['R1'][0:3]+som_adj
                    e1['Rx_unch'][0:3] = e1['R1'][0:3]+som_adj
            else:
                e1['Rx'][0:2] = e1['R1'][0:2]+som_adj
                e1['Rx_unch'][0:2] = e1['R1'][0:2]+som_adj
        else:
            e1['Rx'][0:1] = e1['R1'][0:1]+som_adj
            e1['Rx_unch'][0:1] = e1['R1'][0:1]+som_adj
                    
############### EOM Jumps

    v6 = ql.UnitedStates().endOfMonth(r1).dayOfMonth()

    if v2 == 12:
        eom_adj = eom_ye             # ff_ye
    elif ( v2 % 3) and v2 != 12:
        eom_adj = eom_qe             # ff_qe
    else:
        eom_adj = eom_me             # ff_me 


    v7 = ql.UnitedStates().advance(r3,1,ql.Days).dayOfMonth()
    
 ###### adjustment for in-month hike for hike being on EOM    
    if v7 < v4[0]:
        e1['Rx'][(v6-1):] = e1['R1'][(v6-1):] + eom_adj
    else:
        e1['Rx'][(v6-1):] = e1['R2'][(v6-1):] + eom_adj
    
    e1['Rx_unch'][(v6-1):] = e1['R1'][(v6-1):] + eom_adj

############### Manual adj for comparison with pre-month hike
    if manual == 1:
        e1['Rx_unch'] = e1['Rx_unch']-.25
        a3 = a1-0.25
    else:
        a3 = a1
    

############### Outputs
  
    rate = round(100-e1['Rx'].mean(),5)
    rate_unch = round(100-e1['Rx_unch'].mean(),5)
    
    #px = LT.get_reference_data("FF"+str(f)+" Comdty", "PX_"+str(s)).as_frame()["PX_"+str(s)][0]
    px = con.ref("FF"+str(f)+" Comdty", "PX_"+str(s))['value'][0]
    
    prob = round((100*(rate_unch - px)) / (rate_unch - rate),3) 

    class FF_Prob: 
        def __init__(self):
            self.fut = f
            self.px_unch = (rate_unch, a1)
            self.px = (rate, a1+a2)
            self.prob = (prob, px)
            self.table = e1
        
    return FF_Prob()

