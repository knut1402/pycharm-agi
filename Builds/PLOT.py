##### PLOTS !! 

import os
import pandas as pd
import numpy as np
import math
import datetime
#import tia
#from tia.bbg import LocalTerminal as LT
import pdblp
import runpy
import QuantLib as ql
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns
from tabulate import tabulate
from sklearn.preprocessing import minmax_scale
import pickle

from Utilities import *
from Conventions import FUT_CT,FUT_CT_Q, ccy, ccy_infl
from OIS_DC_BUILD import ois_dc_build
from SWAP_BUILD import swap_build
from SWAP_PRICER import Swap_Pricer
from SWAP_TABLE import swap_table, curve_hmap

con = pdblp.BCon(debug=False, port=8194, timeout=50000)
con.start()

########################################################################################################################################################################################################################################
#-- Plotting Swaps Curves

def plt_curve(c1, h1=[0], max_tenor=30, bar_chg = 0, sprd = 0, name = ''):
    #### build curves
#    c1 = ['USD_3M','GBP_6M']
#    h1 = [0,-1]
#    bar_chg = 1
#    sprd = 0
#    max_tenor = 30
#    name = ''
    n = len(c1)

    today = ql.Date(datetime.datetime.now().day,datetime.datetime.now().month,datetime.datetime.now().year)
    crv_list = {}
    
    
    for k in np.arange(n):
        c2 = ccy(c1[k], today)
        if c2.ois_trigger == 0:
            crv_list[c1[k]] = [swap_build(c1[k], i) for i in h1]
        else: 
            crv_list[c1[k]] = [ois_dc_build(c1[k], i) for i in h1]
    
    crv = flat_lst(list(crv_list.values()))
    
    #### plotting
    mpl.rcParams['axes.facecolor'] = 'white'
    plt.rcParams['axes.labelpad'] = 400.00
    if bar_chg == 0:
        grid_h = [2.5]+[1]*(sprd)
        fig, axs = plt.subplots(sprd+1, 1, figsize=(12, 7),  gridspec_kw={'height_ratios': grid_h, 'hspace':0})
    else:
        if ((n < 2) & (len(h1) > 2)):
            grid_h = [2.5]+[1]*(bar_chg+sprd)
            fig, axs = plt.subplots(bar_chg+sprd+1, 1, figsize=(14, 10),  gridspec_kw={'height_ratios': grid_h, 'hspace':0})
        elif ((n > 1) & (len(h1) < 3)):
            grid_h = [2.5]+[1]*(bar_chg+sprd)
            fig, axs = plt.subplots(bar_chg+sprd+1, 1, figsize=(14, 10),  gridspec_kw={'height_ratios': grid_h, 'hspace':0})
        else:
            if ((n > 2) or ((n == 2) & sprd == 0)):
                grid_h = [2.5]+[1]*(len(h1)-1+sprd)
                fig, axs = plt.subplots(len(h1)+sprd, 1, figsize=(14, 10),  gridspec_kw={'height_ratios': grid_h, 'hspace':0})
            else:
                grid_h = [2.5]+[1]*(bar_chg+sprd)
                fig, axs = plt.subplots(bar_chg+sprd+1, 1, figsize=(14, 10),  gridspec_kw={'height_ratios': grid_h, 'hspace':0})

    #### checking subplot dimensions
    len(fig.axes)
    plt.title(name)
    
    rates_diff = {}
    for i in np.arange(len(crv)):
        if crv[i].ois_trigger == 1:
            d2 = crv[0].ref_date
            d3 = d2 + ql.Period(max_tenor,ql.Years)
            dates_in = [ ql.Date(serial) for serial in range(d2.serialNumber(),d3.serialNumber()+1) ]
            yr_axis = [(dates_in[i]-dates_in[0])/365.25 for i in range(len(dates_in)) ] 
            dates = [ql_to_datetime(dates_in[i]) for i in range(len(dates_in))]
            rates_c = [100*crv[i].curve.forwardRate(d, crv[i].cal.advance(d,1,ql.Days), ql.Actual365Fixed(), ql.Simple).rate() for d in dates_in]
            
        else:
            yr_axis = np.arange(max_tenor)
            rates_c = []
            j = 0
            while j < max_tenor:
                rates_c.append(Swap_Pricer([[crv[i],j,1]]).rate[0])
                j+=1
            
            
            if (i%len(h1)) == 0:
                rates_diff[c1[int(np.floor(i/len(h1)))]] = [rates_c]
            else:
                diff = 100*(np.array(rates_diff[c1[int(np.floor(i/len(h1)))]])[0] - np.array(rates_c))
                rates_diff[c1[int(np.floor(i/len(h1)))]].append(diff.tolist())
        
        if ((bar_chg == 0) & (sprd == 0)):
            axs.grid(True, 'major', 'both', linestyle = ':')
            axs.plot( yr_axis+1 , rates_c , lw = 0.5, marker = '.', label = crv[i].fixing+': '+str(h1[i%len(h1)]) )
            axs.legend(prop={"size":9}, bbox_to_anchor=(1, 1), loc='upper left')
        elif((bar_chg == 0) & (sprd == 1)):
            axs[0].grid(True, 'major', 'both', linestyle = ':')
            axs[0].plot( yr_axis+1 , rates_c , lw = 0.5, marker = '.', label = crv[i].fixing+': '+str(h1[i%len(h1)]) )
            axs[0].legend(prop={"size":9}, bbox_to_anchor=(1, 1), loc='upper left')
            
        
        else:
            axs[0].grid(True, 'major', 'both', linestyle = ':')
            axs[0].plot( yr_axis+1 , rates_c , lw = 0.5, marker = '.', label = crv[i].fixing+': '+str(h1[i%len(h1)]))
            axs[0].xaxis.tick_top()
            axs[0].legend(prop={"size":9}, bbox_to_anchor=(1, 1), loc='upper left')
    
    if sprd == 1:
            rates_sprd = {}
            for i in np.arange(1,n):
                sprd_1 = 100*(np.array(rates_diff[c1[0]][0]) - np.array(rates_diff[c1[i]][0]))
                rates_sprd[c1[0]+' - '+c1[i]] = [sprd_1.tolist()]
                if len(h1) > 1:
                    for j in np.arange(1,len(h1)):
                        diff_sprd = 1*(np.array(rates_diff[c1[0]][j]) - np.array(rates_diff[c1[i]][j]))
                        rates_sprd[c1[0]+' - '+c1[i]].append(diff_sprd.tolist())
            
            axs[1].grid(True, 'major', 'both', linestyle = ':')
            plt.setp(axs[1], xlim=axs[0].get_xlim())
            for j in rates_sprd.keys():
                axs[1].plot( yr_axis+1 , rates_sprd[j][0] , lw = 0.5, marker = '.', label = str(j) )
                axs[1].legend(prop={"size":9}, bbox_to_anchor=(1, 1), loc='upper left')
    
    if ((bar_chg == 1) & (sprd == 1)):
        bar_dict = rates_sprd
        bar_scaler = n-1
        num_plot = (n-1)*(len(h1)-1)
    elif bar_chg == 1:
        rates_chg = {}
        for qq in np.arange(len(c1)):
            for i,k in enumerate(h1[1:]):
                rates_chg[c1[qq]] = [[k]*30]
                j=1
                while j < len(h1):
                    rates_chg[c1[qq]].append(rates_diff[c1[qq]][j])
                    j+=1
                
                bar_dict = rates_chg
                bar_scaler = n
                num_plot = (n)*(len(h1)-1)
        
    bar_yr_axis = yr_axis
    if bar_chg != 0:
        j=1+sprd
        for i in np.arange(n):
            if ((j == 1) or (j < len(fig.axes)-1)):
                if ((len(fig.axes) > 3) or (len(h1) > 2)):
                    j = i+1+sprd
                    bar_yr_axis = yr_axis
                axs[j].grid(True, 'major', 'both', linestyle = ':')
                plt.setp(axs[j], xlim=axs[0].get_xlim())
                width = 0.1
                m = 1
                while m < len(h1):
                    axs[j].bar(bar_yr_axis+1, bar_dict[ list(bar_dict.keys())[i]][m] , width, label= str(list(bar_dict.keys())[i])+': '+str(h1[m]))
                    m+=1
                    bar_yr_axis = bar_yr_axis+width+0.1
                axs[j].legend(prop={"size":9}, bbox_to_anchor=(1, 1), loc='upper left')
        
    return


#plt_curve(['SONIA_DC'], h1=[0], max_tenor=30, bar_chg = 0, sprd = 0, name = '') 

######################### TESTING
# 1 CCY
#plt_curve(['SONIA_DC'], h1=[0], max_tenor=50, bar_chg = 0, sprd = 0, name = '')
#plt_curve(['GBP_6M'], h1=[0], max_tenor=50, bar_chg = 0, sprd = 0, name = '')
#plt_curve(['USD_3M'], h1=[0,-1], max_tenor=30, bar_chg = 1, sprd = 0, name = '')   
#plt_curve(['USD_3M'], h1=[0,-1,-30], max_tenor=30, bar_chg = 0, sprd = 0, name = '')
#plt_curve(['USD_3M'], h1=[0,-1,-30], max_tenor=30, bar_chg = 1, sprd = 0, name = '') 


# 2 CCY
#plt_curve(['USD_3M','GBP_6M'], h1=[0], max_tenor=30, bar_chg = 0, sprd = 0, name = '')

#plt_curve(['USD_3M','GBP_6M'], h1=[0,-1], max_tenor=30, bar_chg = 0, sprd = 0, name = '')
#plt_curve(['USD_3M','EUR_6M'], h1=[0,-1], max_tenor=30, bar_chg = 1, sprd = 0, name = '') 
#plt_curve(['USD_3M','GBP_6M'], h1=[0,-1], max_tenor=30, bar_chg = 0, sprd = 1, name = '')
#plt_curve(['USD_3M','EUR_6M'], h1=[0,-1], max_tenor=30, bar_chg = 1, sprd = 1, name = '')

#plt_curve(['USD_3M','GBP_6M'], h1=[-1,-2,-30], max_tenor=30, bar_chg = 0, sprd = 0, name = '')
#plt_curve(['EUR_6M','GBP_6M'], h1=[-1,-2,-30], max_tenor=30, bar_chg = 1, sprd = 0, name = '')
#plt_curve(['USD_3M','GBP_6M'], h1=[0,-1,-10], max_tenor=30, bar_chg = 0, sprd = 1, name = '')
#plt_curve(['EUR_6M','GBP_6M'], h1=[0,-1,-10], max_tenor=30, bar_chg = 1, sprd = 1, name = '') 


# 3 CCY
#plt_curve(['USD_3M','GBP_6M','EUR_6M'], h1=[-1], max_tenor=30, bar_chg = 0, sprd = 0, name = '')

#plt_curve(['USD_3M','GBP_6M','EUR_6M'], h1=[-1,-2], max_tenor=30, bar_chg = 0, sprd = 0, name = '')
#plt_curve(['USD_3M','GBP_6M','EUR_6M'], h1=[0,-10], max_tenor=30, bar_chg = 1, sprd = 0, name = '')  
#plt_curve(['USD_3M','GBP_6M','EUR_6M'], h1=[-1,-2], max_tenor=30, bar_chg = 0, sprd = 1, name = '')
#plt_curve(['USD_3M','GBP_6M','EUR_6M'], h1=[-1,-5], max_tenor=30, bar_chg = 1, sprd = 1, name = '')  ### label for chg

#plt_curve(['USD_3M','GBP_6M','EUR_6M'], h1=[0,-1,-30], max_tenor=30, bar_chg = 0, sprd = 0, name = '')
#plt_curve(['USD_3M','GBP_6M','EUR_6M'], h1=[0,-1,-30], max_tenor=30, bar_chg = 1, sprd = 0, name = '')
#plt_curve(['USD_3M','GBP_6M','EUR_6M'], h1=[0,-1,-30], max_tenor=30, bar_chg = 0, sprd = 1, name = '')
#plt_curve(['USD_3M','GBP_6M','EUR_6M'], h1=[0,-1,-30], max_tenor=30, bar_chg = 1, sprd = 1, name = '')

#plt_curve(['USD_3M','EUR_6M'], h1=[-1,-2, -30], max_tenor=30, bar_chg = 1, sprd = 1, name = '') 




########################################################################################################################################################################################################################################
#-- Plotting Inflation Curve

def plt_inf_curve(c1, h1=[0], max_tenor=30, bar_chg = 0, sprd = 0, name = ''):
#    c1 = ['HICPxT', 'UKRPI', 'USCPI']
#    h1 = [-1]
#    bar_chg = 0
#    sprd = 1
#    max_tenor = 30
#    name = ''
    
    n_ccy = len(c1)
    n_chg = len(h1)

    today = ql.Date(datetime.datetime.now().day,datetime.datetime.now().month,datetime.datetime.now().year)
    crv_list = {}
    
    for k in np.arange(n_ccy):
        c2 = ccy_infl(c1[k], today)
        crv_list[c1[k]] = [infl_zc_swap_build( c1[k] ,i ,base_month_offset=0) for i in h1]
    
    crv = flat_lst(list(crv_list.values()))
    
    ###### define number of subplots and number of objects !!!!! 
    if ((bar_chg == 0 ) & (sprd == 0)):
        n_plots = 1
        n_obj = {'curve': [n_ccy*n_chg]}
    elif ((bar_chg == 1 ) & (sprd == 0)):
        if (n_chg < 3):
            n_plots = 2
            n_obj = {'curve':[n_ccy*n_chg], 'chg':[n_ccy]}

        elif ((n_ccy == 1) & (n_chg > 3)):
            n_plots = 2
            n_obj = {'curve': [n_ccy*n_chg], 'chg': [n_chg-1]}
        else:
            n_plots = 1 + n_ccy
            n_obj = {'curve': [n_ccy*n_chg], 'chg' : [n_chg-1]*n_ccy }

    elif ((bar_chg == 0 ) & (sprd == 1)):
        n_plots = 2
        n_obj = {'curve ': [n_ccy*n_chg], 'chg': [n_ccy-1] }

    else:
        if (n_chg < 3):
            n_plots = 3
            n_obj = {'curve': [n_ccy*n_chg], 'sprd': [n_ccy-1], 'chg': [n_ccy-1] }
        elif ((n_ccy == 2) & (n_chg > 3)):
            n_plots = 3
            n_obj = { 'curve': [n_ccy*n_chg], 'sprd': [n_ccy-1], 'chg': [n_chg-1] }
        else:
            n_plots = 1 + n_ccy
            n_obj = { 'curve': [n_ccy*n_chg], 'sprd' : [n_ccy-1],  'chg' : [n_chg-1]*(n_ccy-1) }

    ### Define figure
    mpl.rcParams['axes.facecolor'] = 'white'
    plt.rcParams['axes.labelpad'] = 200.00
    grid_h = [2.5]+[1]*(n_plots-1)
    fig, axs = plt.subplots(n_plots, 1, figsize=(10, 8),  gridspec_kw={'height_ratios': grid_h, 'hspace':0})
#    len(fig.axes)


    ### Get ALL Data
    inf_bases_dict = dict([(key, []) for key in c1])
    for i in np.arange(len(crv)):
        infl_base = crv[i].base_month
        inf_bases_dict[c1[int(np.floor(i/len(h1)))]].append(infl_base)
    
    rates = dict([(key, []) for key in c1])
    for i in np.arange(len(crv)):
        yr_axis = np.arange(max_tenor)
        rates_c = []
        j = 0
        while j < max_tenor:
            start_sw = inf_bases_dict[list(inf_bases_dict.keys())[int(np.floor(i/len(h1)))]][0] +  ql.Period(str(j)+"Y")
            rates_c.append(Infl_ZC_Pricer(crv[i], start_sw, 1, lag = 0).zc_rate)
            j+=1
        rates[c1[int(np.floor(i/len(h1)))]].append(rates_c)
            
    rates_change = dict([(key, []) for key in c1])
    for j in rates.keys():
        k = 1
        while k < n_chg:
            rates_diff = 100*( np.array(rates[j][0]) - np.array(rates[j][k]))
            rates_change[j].append(rates_diff.tolist())
            k+=1
    bar_dict = rates_change
    
    if sprd == 1:
        c2 = [c1[0]+' - '+c1[i] for i in np.arange(1,n_ccy)]
        spreads = dict([(key, []) for key in c2])
        for i,j in enumerate(spreads.keys()):
            spreads[j] = 100*(np.array(rates[list(rates.keys())[0]]) - np.array(rates[list(rates.keys())[i+1]]))
        
        spreads_change = dict([(key, []) for key in c2])
        for j in spreads.keys():
            k = 1
            while k < n_chg:
                sprd_chg = 1*( np.array(spreads[j][0]) - np.array(spreads[j][k]))
                spreads_change[j].append(sprd_chg.tolist())
                k+=1
        bar_dict = spreads_change
    
        ### Plot Curve
    if ((bar_chg == 0) & (sprd == 0)):
        axs.grid(True, 'major', 'both', linestyle = ':')
        for i in rates.keys():
            [axs.plot( yr_axis+1 , rates[i][j] , lw = 0.5, marker = '.', label = i+': '+str(h1[j])+': '+str(inf_bases_dict[i][0])) for j in np.arange(n_chg) ]
        axs.legend(prop={"size":9}, bbox_to_anchor=(0.72, 1), loc='upper left')
    else:
        axs[0].grid(True, 'major', 'both', linestyle = ':')
        for i in rates.keys():
            [axs[0].plot( yr_axis+1 , rates[i][j] , lw = 0.5, marker = '.', label = i+': '+str(h1[j])+': '+str(inf_bases_dict[i][0])) for j in np.arange(n_chg) ]
        axs[0].legend(prop={"size":9}, bbox_to_anchor=(0.72, 1), loc='upper left')
        
        
        ### Plot Sprd
    if sprd == 1:
        axs[1].grid(True, 'major', 'both', linestyle = ':')
        plt.setp(axs[1], xlim=axs[0].get_xlim())
        for j in spreads.keys():
            axs[1].plot( yr_axis+1 , spreads[j][0] , lw = 0.5, marker = '.', label = str(j) )
            axs[1].legend(prop={"size":9}, bbox_to_anchor=(0.8, 0.3), loc='upper left')
                
        
        ### Plot Chg
    if sprd == 1:
        start_sub_chg = 2
    else: 
        start_sub_chg = 1
    
    if bar_chg == 1:
        n_sub_chg = len(n_obj['chg'])
        if n_sub_chg == 1:
            axs[start_sub_chg].grid(True, 'major', 'both', linestyle = ':')
            plt.setp(axs[start_sub_chg], xlim=axs[0].get_xlim())
            width = 0.15
            bar_yr_axis = yr_axis
            for i in bar_dict.keys():
                for j in np.arange(len(bar_dict[i])):
                    axs[start_sub_chg].bar(bar_yr_axis+1, bar_dict[i][j] , width, label=i+': '+str(h1[j+1]) )
                    bar_yr_axis = bar_yr_axis+width+0.1
                axs[start_sub_chg].legend(prop={"size":9}, bbox_to_anchor=(1, 1), loc='upper left')
        else:
            for j in np.arange(n_sub_chg):
                axs[j+start_sub_chg].grid(True, 'major', 'both', linestyle = ':')
                plt.setp(axs[j+start_sub_chg], xlim=axs[0].get_xlim())
                width = 0.15
                bar_yr_axis = yr_axis
                for i in np.arange(len(bar_dict[ list(bar_dict.keys())[j]  ])):
                    axs[j+start_sub_chg].bar(bar_yr_axis+1, bar_dict[list(bar_dict.keys())[j]][i] , width, label= list(bar_dict.keys())[j]+': '+str(h1[i+1]) )
                    bar_yr_axis = bar_yr_axis+width+0.1
                axs[j+start_sub_chg].legend(prop={"size":9}, bbox_to_anchor=(1, 1), loc='upper left')

    plt.show()
    plt.title(name)
    return


#str(inf_bases_dict['UKRPI'][0])
#plt_inf_curve(['HICPxT'], h1=[0,-30], max_tenor=30, bar_chg = 0, sprd = 0, name = '')
#plt_inf_curve(['UKRPI'], h1=[0,-30], max_tenor=30, bar_chg = 1, sprd = 0, name = '')
#plt_inf_curve(['HICPxT','UKRPI'], h1=[0,-1], max_tenor=30, bar_chg = 1, sprd = 0, name = '')



########################################################################################################################################################################################################################################
#-- Options PayOffs and Decay
def plt_opt_strat(st, add_delta = [0] , payoff_increm_calc = 100, strat_pv_increm = 0.25):
    mpl.rcParams.update(mpl.rcParamsDefault)
#    st = bond_fut_opt_strat(['RXH2'],['P','P'],[170.5,169.5],[1,-1], s_range = [-1,1], increm = 0.5, chain_len = [6,6])
#    add_delta = [0]

    spot_idx = st.strat.loc[st.strat['ATM_K'] == 0].index[0]
    if st.currency == 'USD':
        px_label = px_dec_to_opt_frac(st.strat_px)
    else:
        px_label = str(np.round(st.strat_px,3))
#    plt.rcParams['axes.labelpad'] = 4.00
    fig = plt.figure(figsize=[8,6])
    #fig.subplots_adjust(top=0.8)
    ax1 = fig.add_subplot(211)
    ax1.set_ylabel('strat_px')
    ax1.set_title(st.strat_name+'       px:'+px_label+'       delta:'+str(np.round(st.strat['strat_delta'][spot_idx],1)))
    
    x_spot = st.strat['fut_px'][spot_idx]
    #### payoff at expiry
    x1 = np.linspace(min(st.strat['fut_px']),max(st.strat['fut_px']), num = payoff_increm_calc)
    if len(add_delta) > 1:
        d_payoff1 = fut_payoff(x1, [st.fut], add_delta)
        y1 = opt_payoff(x1, st.opt_dets, st.strat_px) + d_payoff1
    else:
        y1 = opt_payoff(x1, st.opt_dets, st.strat_px)
    
    #### strategy px
    x2 = st.strat['fut_px']
    y2 = st.strat['strat_px']

    sc1 = ax1.plot(x1, y1, lw=0.5, color = 'k')
    sc2 = ax1.plot(x2, y2, marker = 'x', markersize = 5, lw=0.5)
    sc_spot = ax1.axvline(x_spot, lw=0.5, color = 'y')
    sc_be = ax1.axhline(0, lw=0.5, color = 'k')

    ax1.tick_params(axis='both', which='major', labelsize=9)
    new_labels = [str(st.strat['fut_px'][i])+'\n\n'+str(np.round(st.strat['ATM_K'][i],1))+'\n\n'+str(np.round(st.strat['strat_delta'][i],1)) for i in np.arange(len(st.strat))]
    new_labels.pop(spot_idx )
    ax1.set_xticks(x2[x2.index != spot_idx].tolist())
    ax1.set_xticklabels(new_labels)

    payoff_ticks = np.arange(round_nearest(min(min(y2),min(y1)),strat_pv_increm), round_nearest(max(max(y2),max(y1))+strat_pv_increm,strat_pv_increm), strat_pv_increm)
    ax1.set_yticks(payoff_ticks)
    if st.currency == 'USD':
        ax1.set_yticklabels([px_dec_to_opt_frac(payoff_ticks[i]) for i in np.arange(len(payoff_ticks))])
    else:
        ax1.set_yticklabels([payoff_ticks[i] for i in np.arange(len(payoff_ticks))])
        

    ### delta sub_plot
    ax2 = fig.add_subplot(212)
    ax2.set_ylabel('strat_delta')
    plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=None, hspace=0.25)

    x3 = st.strat['fut_px']
    y3 = st.strat['strat_delta']/100

    sc3 = ax2.plot(x3, y3, marker = 'x', markersize = 5, lw=0.5, color = 'g')
    sc_spot_2 = ax2.axvline(x_spot, lw=0.5, color = 'y')
    
    if len(add_delta) > 1:
        sc3 = ax2.plot(x3, y3+add_delta[0] , marker = 'x', markersize = 5, lw=0.5, color = 'k', ls ='dashed')
        st.strat['strat_delta_updt'] = y3+add_delta[0]

    #plt.show()
    plt.tight_layout()
    return fig

############################### FOR STIR Options
#-- STIR Options
def plt_stir_opt_strat(st, add_delta = [0] , payoff_increm_calc = 100, strat_pv_increm = 0.05):
    mpl.rcParams.update(mpl.rcParamsDefault)
#    st = stir_opt_strat(['0EJ2'], opt_t = ['P','P','P'], opt_s = [98.3125,98.1875, 98.125], opt_w = [1,-2, 1], s_range = [-0.125,0.125], increm = 0.125, s_name = 'strategy', chain_len = [8,8])
#    add_delta = [0]

    spot_idx = st.strat.loc[st.strat['ATM_K'] == 0].index[0]
    px_label = str(100*np.round(st.strat_px,4))
#    plt.rcParams['axes.labelpad'] = 4.00
    fig = plt.figure(figsize=[8,6])
    #fig.subplots_adjust(top=0.8)
    ax1 = fig.add_subplot(211)
    ax1.set_ylabel('strat_px')
    ax1.set_title(st.strat_name+'       px:'+px_label+'       delta:'+str(np.round(st.strat['strat_delta'][spot_idx],1)))
    
    x_spot = st.strat['fut_px'][spot_idx]
    #### payoff at expiry
    x1 = np.linspace(min(st.strat['fut_px']),max(st.strat['fut_px']), num = payoff_increm_calc)
    if len(add_delta) > 1:
        d_payoff1 = fut_payoff(x1, [st.fut], add_delta)
        y1 = opt_payoff(x1, st.opt_dets, st.strat_px) + d_payoff1
    else:
        y1 = opt_payoff(x1, st.opt_dets, st.strat_px)
    
    #### strategy px
    x2 = st.strat['fut_px']
    y2 = st.strat['strat_px']

    sc1 = ax1.plot(x1, y1, lw=0.5, color = 'k')
    sc2 = ax1.plot(x2, y2, marker = 'x', markersize = 5, lw=0.5)
    sc_spot = ax1.axvline(x_spot, lw=0.5, color = 'y')
    sc_be = ax1.axhline(0, lw=0.5, color = 'k')

    ax1.tick_params(axis='both', which='major', labelsize=9)
    new_labels = [str(st.strat['fut_px'][i])+'\n\n'+str(100*np.round(st.strat['ATM_K'][i],3))+'\n\n'+str(np.round(st.strat['strat_delta'][i],1)) for i in np.arange(len(st.strat))]
    new_labels.pop(spot_idx )
    ax1.set_xticks(x2[x2.index != spot_idx].tolist())
    ax1.set_xticklabels(new_labels)

    payoff_ticks = np.arange(round_nearest(min(min(y2),min(y1)),strat_pv_increm), round_nearest(max(max(y2),max(y1))+strat_pv_increm,strat_pv_increm), strat_pv_increm)
    ax1.set_yticks(payoff_ticks)
    ax1.set_yticklabels([ np.round(100*payoff_ticks[i],1) for i in np.arange(len(payoff_ticks))])
        
    ### delta sub_plot
    ax2 = fig.add_subplot(212)
    ax2.set_ylabel('strat_delta')
    plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=None, hspace=0.25)

    x3 = st.strat['fut_px']
    y3 = st.strat['strat_delta']/100

    sc3 = ax2.plot(x3, y3, marker = 'x', markersize = 5, lw=0.5, color = 'g')
    sc_spot_2 = ax2.axvline(x_spot, lw=0.5, color = 'y')
    
    if len(add_delta) > 1:
        sc3 = ax2.plot(x3, y3+add_delta[0] , marker = 'x', markersize = 5, lw=0.5, color = 'k', ls ='dashed')
        st.strat['strat_delta_updt'] = y3+add_delta[0]

#    plt.show()
    plt.tight_layout()
    return fig







########################################################################################################################################################################################################################################
################################################   RATES and CURVES HEATMAP 
############### Entire curve analysis
#-- Curve HeatMap
def curve_hm(g, b=0, offset = [-1], ois_flag = 0, z_offset = 0, z_roll = ['3M','6M']):
#    g = g_3
    h1 = curve_hmap(g, b=b, offset=offset, ois_flag = ois_flag)
    mpl.rcParams.update(mpl.rcParamsDefault)

    fig, axs = plt.subplots(2, 2, figsize=(12, 8))
    fig.subplots_adjust(hspace=0.5)
    ax1 = plt.subplot(2, 2, 1)
    ax1.set_title('Curve', fontdict={'fontsize':9})
    scaled_df = minmax_scale(h1.steep.transpose())
    sns.heatmap(scaled_df, cmap='Blues', linewidths=1, annot=h1.steep.transpose(), xticklabels=h1.steep.index, yticklabels=h1.steep.columns, fmt=".5g", cbar=False, ax=ax1)

    ax2 = plt.subplot(2, 2, 2)
    ax2.set_title('Chg: '+str(h1.offset[z_offset])+' /  '+str(h1.dates[z_offset+1]),  fontdict={'fontsize':9})
    df2 = h1.steep_chg[h1.offset[z_offset]].transpose()
    scaled_df2 = minmax_scale(df2)
    sns.heatmap(scaled_df2, cmap='Purples_r', linewidths=1, annot=df2, xticklabels=df2.columns, yticklabels=df2.index, fmt=".5g", cbar=False, ax=ax2)

    ax3 = plt.subplot(2, 2, 3)
    ax3.set_title('Roll: '+str(z_roll[0]), fontdict={'fontsize':9} )
    sns.heatmap(h1.roll[z_roll[0]].transpose(), cmap='coolwarm_r', linewidths=1, annot=True, fmt=".5g", cbar=False, ax=ax3)

    ax4 = plt.subplot(2, 2, 4)
    ax4.set_title('Roll: '+str(z_roll[1]), fontdict={'fontsize':9})
    sns.heatmap(h1.roll[z_roll[1]].transpose(), cmap='coolwarm_r', linewidths=1, annot=True, fmt=".5g", cbar=False, ax=ax4)
    
    plt.tight_layout()
    plt.show()
    return fig

#-- Rates HeatMap
#rates_hm(['EUR_6M','PLN_6M','HUF_6M','CZK_6M'], b=0, offset = [-1], ois_flag = 0, z_offset = 0)

def rates_hm(g, b=0, offset = [-1], ois_flag = 1, z_offset = 0):
#    g = ['SOFR_DC','ESTER_DC','SONIA_DC']
#    g= ['EUR_6M','PLN_6M','HUF_6M','CZK_6M']
    h1 = curve_hmap(g, b=b, offset=offset, ois_flag = ois_flag)
#    h1= a1
    mpl.rcParams.update(mpl.rcParamsDefault)

    fig, axs = plt.subplots(2, 2, figsize=(12, 8))
    ax1 = plt.subplot(2, 2, 1)
    ax1.set_title('Rates', fontdict={'fontsize':9})
    df_rates = h1.rates[:-1]
    for i in list(df_rates.index):
        if any(x == i for x in ['11Y', '13Y', '40Y']):
            df_rates = df_rates.drop([i])
 
    mask = df_rates.isnull()
    sns.heatmap(df_rates[::-1], cmap='coolwarm', linewidths=1, annot=True, fmt=".5g", cbar=False, mask = mask[::-1], ax=ax1)

    ax2 = plt.subplot(2, 2, 2)
    ax2.set_title('Chg: '+str(h1.offset[z_offset])+' /  '+str(h1.dates[z_offset+1]), fontdict={'fontsize':9})
    df_rates_chg = h1.rates_chg[h1.offset[z_offset]][:-1]
    for i in list(df_rates_chg.index):
        if any(x == i for x in ['11Y', '13Y', '40Y']):
            df_rates_chg = df_rates_chg.drop([i])
            
    mask = df_rates_chg.isnull()
    sns.heatmap(df_rates_chg[::-1], cmap='Purples_r', linewidths=1, annot=True, fmt=".5g", cbar=False, mask = mask[::-1], ax=ax2)

    ax3 = plt.subplot(2, 2, 3)
    ax3.set_title('Fwds', fontdict={'fontsize':9})
    sns.heatmap(h1.curves[::-1], cmap='coolwarm', linewidths=1, annot=True, fmt=".5g", cbar=False, ax=ax3)

    ax4 = plt.subplot(2, 2, 4)
    ax4.set_title('Chg: '+str(h1.offset[z_offset])+' /  '+str(h1.dates[z_offset+1]), fontdict={'fontsize':9})
    sns.heatmap(h1.chg[h1.offset[z_offset]][::-1], cmap='Purples_r', linewidths=1, annot=True, fmt=".5g", cbar=False, ax=ax4)
    
    plt.tight_layout()
    plt.show()
    return fig



################################################   AS INDIVIDUAL PLOTS ! 
###### rates
#df_rates = h1.rates[:-1]
#df_rates = df_rates.drop(['11Y'])
#mask = df_rates.isnull()
#plt.figure(figsize=(10,8))
#plt.title('Rates:   '+str(h1.dates[0]))
#sns.heatmap(df_rates[::-1], cmap='coolwarm', linewidths=1, annot=True, fmt=".5g", cbar=False, mask = mask[::-1])

#z=0
#df_rates_chg = h1.rates_chg[h1.offset[z]][:-1]
#df_rates_chg = df_rates_chg.drop(['11Y'])
#mask = df_rates_chg.isnull()
#plt.figure(figsize=(10,8))
#plt.title('Rates : '+str(h1.dates[0])+ '       Chg: '+str(h1.offset[z]) )
#sns.heatmap(df_rates_chg[::-1], cmap='Purples', linewidths=1, annot=True, fmt=".5g", cbar=False, mask = mask[::-1])


## curves
#plt.figure(figsize=(10,8))
#plt.title('Rates:   '+str(h1.dates[0]))
#sns.heatmap(h1.curves.transpose(), cmap='coolwarm', linewidths=1, annot=True, fmt=".5g", cbar=False)

## curvature
#scaled_df = minmax_scale(h1.steep.transpose())
#plt.figure(figsize=(10,8))
#plt.title('Rates:   '+str(h1.dates[0]))
#sns.heatmap(scaled_df, cmap='Blues', linewidths=1, annot=h1.steep.transpose(), xticklabels=h1.steep.index, yticklabels=h1.steep.columns, fmt=".5g", cbar=False)

## chgs - rates
#z = 0   #### which offset / dates changes to plot 
#plt.figure(figsize=(10,8))
#plt.title('Rates : '+str(h1.dates[0])+ '       Chg: '+str(h1.offset[z]) )
#sns.heatmap(h1.chg[h1.offset[z]].transpose(), cmap='coolwarm', linewidths=1, annot=True, fmt=".5g", cbar=False)

## chgs - curvature
#df2 = h1.steep_chg[h1.offset[z]].transpose()
#scaled_df2 = minmax_scale(df2)
#plt.figure(figsize=(10,8))
#plt.title('Curve : '+str(h1.dates[0])+ '       Chg: '+str(h1.offset[z]) )
#sns.heatmap(scaled_df2, cmap='Purples_r', linewidths=1, annot=df2, xticklabels=df2.columns, yticklabels=df2.index, fmt=".5g", cbar=False)

## rolls
#z_fwd = '6M'   ##### input fwd curve measuer
#plt.figure(figsize=(9,7))
#plt.title('Rolls : '+str(h1.dates[0])+ '       Fwd: '+str(z_fwd) )
#sns.heatmap(h1.roll[z_fwd].transpose(), cmap='coolwarm_r', linewidths=1, annot=True, fmt=".5g", cbar=False)


#plt_ois_curve(['SONIA_DC'], h1=[0], max_tenor=30, name = '',fwd_tenor = '1d',int_tenor = '3m')


######################## plotting ois curves!
#-- Plot OIS Curve
def plt_ois_curve(c1, h1=[0], max_tenor=30, bar_chg = 0, sprd = 0, name = '',fwd_tenor = '1y',int_tenor = '1y', tail = 1, curve_fill = ""):
    mpl.rcParams.update(mpl.rcParamsDefault)
    #### build curves
#    c1 = ['SOFR_DC']
#    h1 = [0,'15-03-2019']
#    h1 = [0, -30]
#    bar_chg = 0
#    sprd = 0
#    max_tenor = 10    
#    tail = 1
#    fwd_tenor = '1m'
#    int_tenor = '1d'
#    name = 'Fwd Tenors: '+fwd_tenor
#    curve_fill = ''

    n_ccy = len(c1)
    n_chg = len(h1)

    today = ql.Date(datetime.datetime.now().day,datetime.datetime.now().month,datetime.datetime.now().year)
    crv_list = {}
    
    
    for k in np.arange(n_ccy):
        c2 = ccy(c1[k], today)
        if c2.ois_trigger == 0:
            crv_list[c1[k]] = [swap_build(c1[k], i) for i in h1]
        else: 
            crv_list[c1[k]] = [ois_dc_build(c1[k], b=h1[i]) for i in np.arange(len(h1))]
        
    crv = flat_lst(list(crv_list.values()))
    h2 = [crv[i].trade_date for i in np.arange(len(crv))]
    
    
    if fwd_tenor[-1] == 'd':
        fwd_tenor2 = ql.Days
    elif fwd_tenor[-1] == 'm':
        fwd_tenor2 = ql.Months
    else:
        fwd_tenor2 = ql.Years
   
    
    ###### define number of subplots and number of objects !!!!! 
    if ((bar_chg == 0 ) & (sprd == 0)):
        n_plots = 1
        n_obj = {'curve': [n_ccy*n_chg]}
    elif ((bar_chg == 1 ) & (sprd == 0)):
        if (n_chg < 3):
            n_plots = 2
            n_obj = {'curve':[n_ccy*n_chg], 'chg':[n_ccy]}

        elif ((n_ccy == 1) & (n_chg > 3)):
            n_plots = 2
            n_obj = {'curve': [n_ccy*n_chg], 'chg': [n_chg-1]}
        else:
            n_plots = 1 + n_ccy
            n_obj = {'curve': [n_ccy*n_chg], 'chg' : [n_chg-1]*n_ccy }

    elif ((bar_chg == 0 ) & (sprd == 1)):
        n_plots = 2
        n_obj = {'curve ': [n_ccy*n_chg], 'chg': [n_ccy-1] }

    else:
        if (n_chg < 3):
            n_plots = 3
            n_obj = {'curve': [n_ccy*n_chg], 'sprd': [n_ccy-1], 'chg': [n_ccy-1] }
        elif ((n_ccy == 2) & (n_chg > 3)):
            n_plots = 3
            n_obj = { 'curve': [n_ccy*n_chg], 'sprd': [n_ccy-1], 'chg': [n_chg-1] }
        else:
            n_plots = 1 + n_ccy
            n_obj = { 'curve': [n_ccy*n_chg], 'sprd' : [n_ccy-1],  'chg' : [n_chg-1]*(n_ccy-1) }
    
    ### Define figure
    mpl.rcParams['axes.facecolor'] = 'white'
#    plt.rcParams['axes.labelpad'] = 400.00
    grid_h = [2.5]+[1]*(n_plots-1)
    fig, axs = plt.subplots(n_plots, 1, figsize=(6, 5),  gridspec_kw={'height_ratios': grid_h, 'hspace':0})
#    len(fig.axes)

    ### Get ALL Data
    rates = dict([(key, []) for key in c1])
    for i in np.arange(len(crv)):
        if crv[i].ois_trigger == 1:
            d2 = crv[i].ref_date
            d3 = d2 + ql.Period(max_tenor,ql.Years)
#            dates_in = [ ql.Date(serial) for serial in range(d2.serialNumber(),d3.serialNumber()+1) ]   #### dates for plotting !!
#            yr_axis = [(dates_in[i]-dates_in[0])/365.25 for i in range(len(dates_in)) ] 
            dates_in2 = ql.MakeSchedule(d2, d3, ql.Period(int_tenor))  #### dates for pricing !! 
            yr_axis = [(dates_in2[i]-dates_in2[0])/365.25 for i in range(len(dates_in2)) ]
            rates_c = [100*crv[i].curve.forwardRate(d, crv[i].cal.advance(d,int(fwd_tenor[0]),fwd_tenor2), ql.Actual365Fixed(), ql.Simple).rate() for d in dates_in2]
            rates[c1[int(np.floor(i/len(h1)))]].append(rates_c)

           
        else:
            yr_axis = np.arange(max_tenor)
            rates_c = []
            j = 0
            while j < max_tenor:
                rates_c.append(Swap_Pricer([[crv[i],j,tail]]).rate[0])
                j+=1
            rates[c1[int(np.floor(i/len(h1)))]].append(rates_c)
            
    rates_change = dict([(key, []) for key in c1])
    for j in rates.keys():
        k = 1
        while k < n_chg:
            rates_diff = 100*( np.array(rates[j][0]) - np.array(rates[j][k]))
            rates_change[j].append(rates_diff.tolist())
            k+=1
    bar_dict = rates_change
    
    if sprd == 1:
        c2 = [c1[0]+' - '+c1[i] for i in np.arange(1,n_ccy)]
        spreads = dict([(key, []) for key in c2])
        for i,j in enumerate(spreads.keys()):
            spreads[j] = 100*(np.array(rates[list(rates.keys())[0]]) - np.array(rates[list(rates.keys())[i+1]]))
        
        spreads_change = dict([(key, []) for key in c2])
        for j in spreads.keys():
            k = 1
            while k < n_chg:
                sprd_chg = 1*( np.array(spreads[j][0]) - np.array(spreads[j][k]))
                spreads_change[j].append(sprd_chg.tolist())
                k+=1
        bar_dict = spreads_change

    ####write in data
    #    r1 = pd.DataFrame(rates)
    #    r2 = pd.DataFrame()
    #    r2['SOFR'] = flat_lst(r1['SOFR_DC'].tolist())
    #    r2['ESTER'] = flat_lst(r1['ESTER_DC'].tolist())
    #    r2['SONIA'] = flat_lst(r1['SONIA_DC'].tolist())
    #    r2.index = [ ql_to_datetime(dates_in2[int(i)]) for i in np.arange(len(dates_in2))]
    #    r2.to_excel("ois_rates.xlsx")

        ### Plot Curve
    yr_axis2 = np.array(yr_axis)
    if ((bar_chg == 0) & (sprd == 0)):
#        axs.grid(True, 'major', 'both', linestyle = ':')
        for i in rates.keys():
            [axs.plot( yr_axis2 , rates[i][j] , lw = 0.5, marker = '.' ,ms = 2,  label = str(ccy(i,today).curncy)+': '+str(h2[j])) for j in np.arange(n_chg) ] #    prev = label = i+': '+str(h2[j]) 
#            axs.text(0.875,-0.15,"Maturity (Yrs)")
#            axs.text(-0.25,2.5,"Implied Overnight Rate (%)", rotation = 'vertical')
            if len(curve_fill) > 0:
                [axs.fill_between(yr_axis2 , rates[i][0], 0, where= (curve_fill[j][0] <yr_axis2) & (yr_axis2< curve_fill[j][1]), fc = "C"+str(j+2), alpha = 0.4  ) for j in np.arange(len(curve_fill)) ] 
        axs.legend(prop={"size":8}, loc='best')
    else:
#        axs[0].grid(True, 'major', 'both', linestyle = ':')
        for i in rates.keys():
            [axs[0].plot( np.array(yr_axis) , rates[i][j] , lw = 0.5, marker = '.',ms = 2, label = i+': '+str(h2[j]) ) for j in np.arange(n_chg) ]
        axs[0].legend(prop={"size":8}, loc='best')
        
    
    # str(ccy('SOFR_DC',today).curncy)   ##### change label from curve to currency
        

        ### Plot Sprd
    if sprd == 1:
        axs[1].grid(True, 'major', 'both', linestyle = ':')
        plt.setp(axs[1], xlim=axs[0].get_xlim())
        for j in spreads.keys():
            axs[1].plot( yr_axis , spreads[j][0] , lw = 0.5, marker = '.', label = str(j) )
            axs[1].legend(prop={"size":8},  loc='best')
                
        
        ### Plot Chg
    if sprd == 1:
        start_sub_chg = 2
    else: 
        start_sub_chg = 1
    
    if bar_chg == 1:
        n_sub_chg = len(n_obj['chg'])
        if n_sub_chg == 1:
            axs[start_sub_chg].grid(True, 'major', 'both', linestyle = ':')
            plt.setp(axs[start_sub_chg], xlim=axs[0].get_xlim())
            width = 0.15
            bar_yr_axis = yr_axis
            for i in bar_dict.keys():
                for j in np.arange(len(bar_dict[i])):
                    axs[start_sub_chg].bar(np.array(bar_yr_axis), bar_dict[i][j] , width, label=i+': '+str(h1[j+1]) )
                    bar_yr_axis = np.array(bar_yr_axis)+width+0.1
                axs[start_sub_chg].legend(prop={"size":8},  loc='best')
        else:
            for j in np.arange(n_sub_chg):
                axs[j+start_sub_chg].grid(True, 'major', 'both', linestyle = ':')
                plt.setp(axs[j+start_sub_chg], xlim=axs[0].get_xlim())
                width = 0.15
                bar_yr_axis = yr_axis
                for i in np.arange(len(bar_dict[ list(bar_dict.keys())[j]  ])):
                    axs[j+start_sub_chg].bar(np.array(bar_yr_axis)+1, bar_dict[list(bar_dict.keys())[j]][i] , width, label= list(bar_dict.keys())[j]+': '+str(h1[i+1]) )
                    bar_yr_axis = bar_yr_axis+width+0.1
                axs[j+start_sub_chg].legend(prop={"size":8},  loc='best')
                
    plt.title(name)
    plt.tight_layout()
    return fig

#-- Plot Vol surf
def plot_opt_vol_surf(v, opt_type = 'P', x_ax = 'delta' ):
    mpl.rcParams.update(mpl.rcParamsDefault)
    fig = plt.figure(figsize=[8,6])
    ax1 = fig.add_subplot(111)
    ax1.set_ylabel('bp vol')
    ax1.set_xlabel(x_ax)
    ax1.set_title(v[0].ticker[:4]+' '+opt_type)
    
    if opt_type == 'P':
        opt_type_conv = -1
    else:
        opt_type_conv = 1
    
    for s in v:
        df = s.tab
        df1 = df[df['opt_type']==opt_type_conv]
        df2 = df1[df1['strikes'] == s.center][['strikes','iv','delta']]
        ax1.plot(df1[x_ax],df1['iv'], marker='.',  label = s.ref_date)        
        ax1.annotate( str(s.center), xy=(df2[x_ax].tolist()[0], df2['iv'].tolist()[0]), fontsize = 8, horizontalalignment='center', verticalalignment='top')

    ax1.legend(prop={"size":9},  loc='best')
#    plt.tight_layout()
    return fig

#plot_opt_vol_surf(v, opt_type = 'C', x_ax = 'strikes' )


######################################### Bloomberg Plotting Utility Tool
#-- PlotTool

def plotool(d1,d2, curves, mat, toggle, inst_type, plot_type, change_flag, invert_flag ):
    mpl.rcParams.update(mpl.rcParamsDefault)

    today = ql.Date(datetime.datetime.now().day,datetime.datetime.now().month,datetime.datetime.now().year)
#    d1 = '03-01-2022'
#    d1 = -90
#    d2 = ''
#    curves = ['SOFR_DC','ESTER_DC','SONIA_DC','AUD_6M']
#    mat = ['5Y5Y']
    
#    toggle = 'Std'  ######### std / x-curve
#    inst_type = 'Fwd'    ##### par / fwd / cash
#    plot_type = 'Outright'#### outright / spread / fly
    
#    change_flag = 0
#    invert_flag = 0
    
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

    if (toggle == 'Std') & (plot_type == 'Outright'):
        for i in np.arange(len(x2.columns)):
            print( int(np.floor(i/len(mat))) , i%len(mat) )
            x2.rename(columns={ x2.columns[i][0]: curves[  int(np.floor(i/len(mat)))   ]+':'+mat[ i%len(mat) ] }, inplace=True)
            x1 = x2
            plt_leg = [x1.columns[i][0]+'...........'+str( np.round(x1[x1.columns[i]][-1],3) ) for i in np.arange(len(x1.columns))]

    if (toggle == 'Std') & (plot_type == 'Spread'):
        x1 = pd.concat([ pd.Series( 100*(x2[x2.columns[ (i*len(mat))+1 ]]-x2[x2.columns[ i*len(mat) ]]), name = curves[i]+':'+mat[0]+'_'+mat[1] ) for i in np.arange(len(curves)) ], axis = 1)
        plt_leg = [x1.columns[i]+'...........'+str( np.round(x1[x1.columns[i]][-1],3) ) for i in np.arange(len(x1.columns))]

    if (toggle == 'Std') & (plot_type == 'Fly'):
        x1 = pd.concat([ pd.Series( -100*(x2[x2.columns[ (i*len(mat))+2 ]]+x2[x2.columns[ i*len(mat) ]]-2*x2[x2.columns[ (i*len(mat))+1]] ), name = curves[i]+':'+mat[0]+'_'+mat[1]+'_'+mat[2] ) for i in np.arange(len(curves)) ], axis = 1)
        plt_leg = [x1.columns[i]+'...........'+str( np.round(x1[x1.columns[i]][-1],3) ) for i in np.arange(len(x1.columns))]

    if (toggle == 'X-Curve') & (plot_type == 'Outright'):
        x1 = pd.concat([ pd.Series( 100*(x2[x2.columns[ i+len(mat) ]]-x2[x2.columns[ i%len(mat) ]]), name = curves[ int(np.floor(i/len(mat)))+1  ]+' / '+curves[0]+':'+mat[i%len(mat)] ) for i in np.arange(len(mat)*(len(curves)-1)) ], axis = 1)
        plt_leg = [x1.columns[i]+'...........'+str( np.round(x1[x1.columns[i]][-1],3) ) for i in np.arange(len(x1.columns))]
    
    if (toggle == 'X-Curve') & (plot_type == 'Spread'):
        x1 = pd.concat([ pd.Series( 100*( ((x2[x2.columns[1]]-x2[x2.columns[0]])) -  (x2[x2.columns[ (i+1)*len(mat)+1 ]]    -    x2[x2.columns[ (i+1)*len(mat) ]])   ), name = curves[ i+1  ]+' / '+curves[0]+':'+mat[0]+'_'+mat[1] ) for i in np.arange((len(mat)-1)*(len(curves)-1)) ], axis = 1)
        plt_leg = [x1.columns[i]+'...........'+str( np.round(x1[x1.columns[i]][-1],3) ) for i in np.arange(len(x1.columns))]
    
    if (toggle == 'X-Curve') & (plot_type == 'Fly'):
        x1 = pd.concat([ pd.Series( 100*( ((x2[x2.columns[2]]+x2[x2.columns[0]]-2*x2[x2.columns[1]])) -  (  x2[x2.columns[ (i+1)*len(mat) ]]+x2[x2.columns[ (i+1)*len(mat)+2 ]] -2*(x2[x2.columns[ (i+1)*len(mat)+1 ]]) ) ), name = curves[ i+1  ]+' / '+curves[0]+':'+mat[0]+'_'+mat[1]+'_'+mat[2] ) for i in np.arange((len(mat)-2)*(len(curves)-1)) ], axis = 1)
        plt_leg = [x1.columns[i]+'...........'+str( np.round(x1[x1.columns[i]][-1],3) ) for i in np.arange(len(x1.columns))]
    
    x3 = np.array(x1.index.strftime("%b-%y"))  #### x-ais (date) ticks labels change
    
    fig = plt.figure(figsize=[8,6])

    if invert_flag == 1:
        x1 = x1*-1
    
    if change_flag == 0:
        plt.plot(x1)
        plt.legend( plt_leg, bbox_to_anchor=(0,1.02,1, 0.2), loc="lower right", borderaxespad=0) 
        plt.xticks( x1.index[::-20], x3[::-20], rotation=90)
        plt.grid(b=True, which='major', color='#999999', linestyle='-', alpha=0.2)
        plt.tight_layout()
    else:
        plt.plot(x1.diff().cumsum())
        plt.legend(  plt_leg, bbox_to_anchor=(0,1.02,1, 0.2), loc="lower right", borderaxespad=0) 
        plt.xticks( x1.index[::-20], x3[::-20], rotation=90)
        plt.grid(b=True, which='major', color='#999999', linestyle='-', alpha=0.2)
        plt.tight_layout()
    
    
    return fig






#-- Eco Plot
def ecfc_plot(a, b, c, contrib1 = 'GS', off = 'IMF'):
    mpl.rcParams.update(mpl.rcParamsDefault)
#    a = 'CPI'
#    b = 'EU'
#    c = '2023'
#    contrib1 = 'BAR'
#    off = 'ECB'
    
    contrib = ['BAR', 'BOA', 'BNP', 'CE', 'CIT', 'CAG', 'CSU', 'DNS', 'FTC', 'GS', 'HSB', 'IG', 'JPM', 'MS', 'NTX', 'NS', 'NDA', 'PMA', 'UBS', 'WF', 'SCB' ]   
    today = ql.Date(datetime.datetime.now().day,datetime.datetime.now().month,datetime.datetime.now().year)
    t_stg = bbg_date_str(today)
    cal = ql.TARGET()
    start = bbg_date_str(cal.advance(today, ql.Period( -1, ql.Years)))
    
    if a == 'GDP':
        e = 'GD'
    elif a == 'CPI':
        e = 'PI'
    elif a == 'PCE':
        e = 'PC'
    elif a == 'Core-PCE':
        e = 'CC'
    elif a == 'UNEMP':
        e = 'UP'
    elif a == 'FISC':
        e = 'BB'

    g1 = ["EC"+e+b+" "+c[-2:]+" "+i+" Index" for i in contrib]

    df1 = con.bdh(g1, 'PX_LAST',start, t_stg, longdata=True)
    df2 = con.bdh("EC"+e+b+" "+c[-2:]+" "+off+" Index", 'PX_LAST',start, t_stg, longdata=True)

    d1 = [ql_to_datetime(cal.advance(today, ql.Period( int(-10-i), ql.Days))) for i in np.arange(240)]
    m1 = [df1[(df1['date'] > d1[i]) & (df1['date'] < ql_to_datetime(cal.advance(today, ql.Period( int(0-i), ql.Days)))) ]['value'].mean()  for i in np.arange(len(d1))]

    c1 = df1['ticker'].unique()
    fig = plt.figure(figsize=[6.5,4.75])
    for i in np.arange(len(c1)):
        if c1[i].split()[2] == contrib1:
            c2 = 'darkorange'
            c3 = contrib1+": "+str(df1[df1['ticker'] == "EC"+e+b+" "+c[-2:]+" "+contrib1+" Index"].iloc[-1]['value'])
        else:
            c2 = 'silver'
            c3 = ''
        a1 = df1[df1['ticker'] == c1[i]]
        plt.plot(a1['date'], a1['value'], c = c2, label = c3)
    plt.plot(df2['date'], df2['value'], c = 'forestgreen', label = off+": "+str(df2['value'][len(df2)-1]))
    plt.plot(d1, m1, c = 'dodgerblue', label = 'Avg: '+str(np.round(m1[0],2)))
    plt.xticks(rotation = 45);
    plt.legend()
    plt.title(b+" "+a+" forecast: "+c)
    plt.tight_layout()
    
    return fig





























