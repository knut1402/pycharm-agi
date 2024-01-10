#### Get 1m Historical rates as proxy for base rates

today = ql.Date(datetime.datetime.now().day,datetime.datetime.now().month,datetime.datetime.now().year)
d1 = '15-09-2021'     #### start date
d2 = ''               #### end date if required
curves = ['SOFR_DC','ESTER_DC', 'SONIA_DC']
mat = ['1m1d']

### Get fwd rates component
fwd_st = 2
fwd_st_unit = ql.Years
fwd_tn = mat[0][2:]

toggle = 'Std'  ######### std / x-curve
inst_type = 'Fwd'    ##### par / fwd / cash
plot_type = 'Outright'#### outright / spread / fly

change_flag = 0
invert_flag = 0

c1 = [ccy(curves[i], today) for i in np.arange(len(curves))]
curve_code = [c1[i].bbg_curve.split()[0][-3:] for i in np.arange(len(c1))]

if isinstance(d1,str) == True:
    try:
        start = ql.Date(int(d1.split('-')[0]),int(d1.split('-')[1]),int(d1.split('-')[2]))
    except:
        if d1[-1] in ('D','d'):
            unit = ql.Days
        elif d1[-1] in ('W','w'):
            unit = ql.Weeks
        elif d1[-1] in ('M','m'):
            unit = ql.Months
        elif d1[-1] in ('Y','y'):
            unit = ql.Years
        start = c1[0].cal.advance(today,int(d1[0:-1]),unit)
else:
    start = c1[0].cal.advance(today,d1,ql.Days)

if isinstance(d2,str) == True:
    if len(d2) == 0:
        end = today
    else:
        try:
            end = ql.Date(int(d2.split('-')[0]),int(d2.split('-')[1]),int(d2.split('-')[2]))
        except:
            if d2[-1] in ('D','d'):
                unit = ql.Days
            elif d2[-1] in ('W','w'):
                unit = ql.Weeks
            elif d2[-1] in ('M','m'):
                unit = ql.Months
            elif d2[-1] in ('Y','y'):
                unit = ql.Years
            end = c1[0].cal.advance(today,int(d2[0:-1]),unit)
else:
    end = c1[0].cal.advance(today,d2,ql.Days)

start_date =  bbg_date_str(start, ql_date = 1)
end_date =  bbg_date_str(end, ql_date = 1)

if inst_type == 'Par':
    str_att1 = 'Z '
    str_att2 = ' BLC2 Curncy'
elif inst_type == 'Fwd':
    str_att1 = 'FS '
    str_att2 = ' BLC Curncy'
elif inst_type == 'Cash':
    str_att1 = 'FC '
    str_att2 = ' BLC Curncy'

ticker_list = [['S0'+curve_code[j]+str_att1+mat[i]+str_att2 for i in np.arange(len(mat))] for j in np.arange(len(curve_code)) ]
ticker_list = flat_lst(ticker_list)
x2 = con.bdh(ticker_list , 'PX_LAST', start_date, end_date)
x2 = x2[ [ticker_list[i] for i in np.arange(len(ticker_list))] ]


### Get fwds dates
date_list = [x2.index[-1] + datetime.timedelta(days=x) for x in range(750)]

### Curve builds
sofr_live =  ois_dc_build('SOFR_DC',b=0)
sofr_fwd = [ Swap_Pricer( [[sofr_live, ql_to_datetime(datetime_to_ql(date_list[i]) + ql.Period(fwd_st,fwd_st_unit)).strftime('%d-%m-%Y') ,fwd_tn]] ).rate
             for i in np.arange(4,len(date_list)) ]

ester_live =  ois_dc_build('ESTER_DC',b=0)
ester_fwd = [ Swap_Pricer( [[ester_live , ql_to_datetime(datetime_to_ql(date_list[i]) + ql.Period(fwd_st,fwd_st_unit)).strftime('%d-%m-%Y') ,fwd_tn]] ).rate
              for i in np.arange(4,len(date_list)) ]

sonia_live =  ois_dc_build('SONIA_DC',b=0)
sonia_fwd = [ Swap_Pricer( [[sonia_live , ql_to_datetime(datetime_to_ql(date_list[i]) + ql.Period(fwd_st,fwd_st_unit)).strftime('%d-%m-%Y') ,fwd_tn]] ).rate
              for i in np.arange(4,len(date_list)) ]

### Concatenating data
usd1 = x2[x2.columns[0][0]]
usd1.columns = ['sofr']
usd2 = pd.DataFrame(sofr_fwd, index = date_list[4:])
usd2.columns = ['sofr']
df = pd.concat([usd1, usd2])

eur1 = x2[x2.columns[1][0]]
eur1.columns = ['ester']
eur2 = pd.DataFrame(ester_fwd, index = date_list[4:])
eur2.columns = ['ester']
df2 = pd.concat([eur1, eur2])

gbp1 = x2[x2.columns[2][0]]
gbp1.columns = ['sonia']
gbp2 = pd.DataFrame(sonia_fwd, index = date_list[4:])
gbp2.columns = ['sonia']
df3 = pd.concat([gbp1, gbp2])

df['ester'] = list(df2['ester'])
df['sonia'] = list(df3['sonia'])

### Sort out tick labels
x3 = np.array(df.index.strftime("%b-%y"))
t1=list(df.index[0:428:30])+list(df.index[458:-1:42])
t2=list(x3[0:428:30])+list(x3[458:-1:42])

#### Plot hist rates + fwds
plt.plot(df)
#plt.axvline(x=x2.index[-1], color = 'black')
plt.title('Fwd rates', fontsize=10)
plt.legend( ['USD','EUR','GBP'])
plt.xticks( t1, t2, rotation=90)
plt.grid( which='major', color='#999999', linestyle='-', alpha=0.2)
plt.tight_layout()
plt.show()

#### Plot changes in hist rates + fwds
plt.plot(df.diff().cumsum())
plt.axvline(x=x2.index[-1], color = 'black')
plt.title('Change in Fwd Rates since 15-Sep-2021', fontsize=10)
plt.legend( ['USD','EUR','GBP'])
plt.xticks( t1, t2, rotation=90)
plt.grid( which='major', color='#999999', linestyle='-', alpha=0.2)
plt.tight_layout()
plt.show()


df[400:450]




