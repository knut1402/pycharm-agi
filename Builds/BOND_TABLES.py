##### BOND TABLES 

import os
import pandas as pd
import numpy as np
import datetime
#import tia
#from tia.bbg import LocalTerminal as LT
import pdblp
import runpy
import QuantLib as ql
import matplotlib as mpl
import matplotlib.pyplot as plt
from tabulate import tabulate

con = pdblp.BCon(debug=False, port=8194, timeout=50000)
con.start()

from Conventions import FUT_CT,FUT_CT_Q, ccy
from INFL_CARRY import linker_carry_calc
from INF_ZC_BUILD import infl_zc_swap_build, Infl_ZC_Pricer
from Utilities import *

#### building linker monitor
def linker_table(a, bond_db, repo_rate, b = 0, chg=-1, country_filter = '', index_filter = '', fixing_curve = 'BARX', fwd_date=''):

#    a = 'ESTER_DC'
#    b = 0
#    chg= -1
#    bond_db = euro_linker_db
#    country_filter = ''
#    index_filter = ''
#    repo_rate = -0.5
#    fixing_curve = 'BARX'
#    fwd_date = ''

    bond_db = bond_db.reset_index(drop=True)
    if country_filter != '':
        bond_db = bond_db[bond_db['country'] == country_filter]
        bond_db = bond_db.reset_index(drop=True)
    if index_filter != '':
        bond_db = bond_db[bond_db['index'] == index_filter]
        bond_db = bond_db.reset_index(drop=True)

    today = ql.Date(datetime.datetime.now().day,datetime.datetime.now().month,datetime.datetime.now().year)

    ### handling dates
    c = ccy(a,today)
    
    if isinstance(b,int) == True:
        ref_date = c.cal.advance(today,b,ql.Days)
    else:
        ref_date = ql.Date(int(b.split('-')[0]),int(b.split('-')[1]),int(b.split('-')[2]))
    
    if isinstance(chg,int) == True:
        ref_date_1 = c.cal.advance(ref_date,chg,ql.Days)
    else:
        ref_date_1 = ql.Date(int(chg.split('-')[0]),int(chg.split('-')[1]),int(chg.split('-')[2]))
        
    ql.Settings.instance().evaluationDate = ref_date
    
    if ref_date.dayOfMonth() < 10:
        d0 = str(0)+str(ref_date.dayOfMonth())
    else:
        d0 = str(ref_date.dayOfMonth())
    if ref_date_1.dayOfMonth() < 10:
        d1 = str(0)+str(ref_date_1.dayOfMonth())
    else:
        d1 = str(ref_date_1.dayOfMonth())
        
    if ref_date.month() < 10:
        m0 = str(0)+str(ref_date.month())
    else:
        m0 = str(ref_date.month())
    if ref_date_1.month() < 10:
        m1 = str(0)+str(ref_date_1.month())
    else:
        m1 = str(ref_date_1.month())
        
    bbg_t = str(ref_date.year())+m0+d0
    bbg_t_1 = str(ref_date_1.year())+m1+d1

    linker_monitor = pd.DataFrame()
    linker_monitor['linker_isin'] = bond_db['linker_isin']
    linker_monitor['compar_isin'] = bond_db['compar_isin']
    linker_monitor['Linker'] = bond_db['linker']
    linker_monitor['Nominal'] = bond_db['nominal']
    
    #### Add maturity field    
    d_mat = con.ref(bond_db['linker_isin'].tolist(),['MATURITY'])
    d_mat = d_mat.drop(columns = ['field'])
    linker_monitor['Maturity'] = [d_mat[d_mat['ticker'] == bond_db['linker_isin'][i]]['value'].tolist()[0] for i in np.arange(len(bond_db))]
    
    
    l2 = [('linker_isin','PX_LAST', 'Px'),
      ('linker_isin','YLD_YTM_MID', 'Yield'),
      ('compar_isin','YLD_YTM_MID', 'Nom_Yld')]

    for e2,f2,g2 in l2:
        d2 = con.bdh(bond_db[e2].tolist(),[f2],bbg_t,bbg_t, longdata=True)
        d2 = d2.drop(columns = ['field'])
        linker_monitor[g2] = [d2[d2['ticker'] == bond_db[e2][i]]['value'].tolist()[0] for i in np.arange(len(bond_db))]
    
    l3 = [('linker_isin','YLD_YTM_MID', 'Yld_1'),
      ('compar_isin','YLD_YTM_MID', 'Nom_Yld_1')]

    for e3,f3,g3 in l3:
        d3 = con.bdh(bond_db[e3].tolist(),[f3],bbg_t_1,bbg_t_1, longdata=True)
        d3 = d3.drop(columns = ['date','field'])
        d3.columns = [e3, g3]
        linker_monitor[g3] = [d3[d3[e3] == bond_db[e3][i]][g3].tolist()[0] for i in np.arange(len(bond_db))]

    ##### Add carry calculator
    df_carry, f_dates = linker_carry_calc(linker_monitor['linker_isin'].tolist(), 'HICPxT', repo_rate = repo_rate, fixing_curve = fixing_curve, fwd_date = fwd_date)
    f_dates = ['Carry'] + f_dates
    df1 = pd.DataFrame(df_carry.items())

    for i in np.arange(len(f_dates)):
        linker_monitor[f_dates[i]] = [ df1[1][j][i] for j in np.arange(len(df1)) ] 


    linker_monitor['Δ_adj'] = 100*(linker_monitor['Yield'] - linker_monitor['Yld_1'])-linker_monitor['Carry']
    linker_monitor['Δ_Nom'] = 100*(linker_monitor['Nom_Yld'] - linker_monitor['Nom_Yld_1'])
    linker_monitor['BEI'] = 100*(linker_monitor['Nom_Yld'] - linker_monitor['Yield'])+linker_monitor['Carry']
    linker_monitor['Δ_BEI_adj'] = linker_monitor['Δ_Nom'] - linker_monitor['Δ_adj']
    
    linker_monitor['Yield'] = linker_monitor['Yield'].round(3)
    linker_monitor['Δ_adj'] = linker_monitor['Δ_adj'].round(1)
    linker_monitor['BEI'] = linker_monitor['BEI'].round(1)
    linker_monitor['Nom_Yld'] = linker_monitor['Nom_Yld'].round(3)
    linker_monitor['Δ_Nom'] = linker_monitor['Δ_Nom'].round(1)
    linker_monitor['Δ_BEI_adj'] = linker_monitor['Δ_BEI_adj'].round(1)
    for i in f_dates:
        linker_monitor[i] = linker_monitor[i].round(1)   
    
    linker_monitor = linker_monitor[['Linker', 'Maturity', 'Px', 'Yield', 'Δ_adj', 'BEI', 'Δ_BEI_adj', 'Nom_Yld','Δ_Nom', 'Nominal'] + f_dates]
    
    return linker_monitor






