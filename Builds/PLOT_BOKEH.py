
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
#from datetime import datetime, timedelta, time

from Utilities import *
from Conventions import FUT_CT,FUT_CT_Q, ccy, ccy_infl
from OIS_DC_BUILD import ois_dc_build
from SWAP_BUILD import swap_build
from SWAP_PRICER import Swap_Pricer, Swap_curve_fwd, quick_swap
from SWAP_TABLE import swap_table, swap_table2, curve_hmap
from INF_ZC_BUILD import infl_zc_swap_build, Infl_ZC_Pricer, inf_swap_table
from BOND_CURVES import bond_curve_build
from VOL_BUILD import build_vol_surf, build_vol_spline, bond_fut_opt_strat, get_sim_option_px, build_stir_vol_surf, stir_opt_strat
from BOND_TABLES import linker_table
from INFL_CARRY import linker_carry_calc

con = pdblp.BCon(debug=False, port=8194, timeout=50000)
con.start()


# bokeh imports
from bokeh.plotting import figure, show
from bokeh.models import HoverTool, BoxZoomTool, ResetTool, Legend, DatetimeTickFormatter
from bokeh.models import ColumnDataSource
from bokeh.layouts import row, column
from bokeh.palettes import Category10, brewer, Category20


def plt_ois_curve_bokeh(c1, h1=[0], max_tenor=30, bar_chg = 0, sprd = 0, name = '',fwd_tenor = '1y',int_tenor = '1y', built_curve=0, tail = 1, curve_fill = "", label_curve_name = 1, p_dim = [1000,400]):
    #### build curves
#    c1 = ['SOFR_DC']
#    h1 = [0,'15-03-2019']
#    h1 = [0, -1, -5]
#    bar_chg = 1
#    sprd = 1
#    max_tenor = 30
#    tail = 1
#    fwd_tenor = '1y'
#    int_tenor = '1y'
#    name = 'Fwd Tenors: '+fwd_tenor
#    curve_fill = ''
#    label_curve_name = 1
#    built_curve = 0

    n_ccy = len(c1)
    n_chg = len(h1)

    today = ql.Date(datetime.datetime.now().day, datetime.datetime.now().month, datetime.datetime.now().year)
    if built_curve == 0:
        crv_list = {}
        for k in np.arange(n_ccy):
            c2 = ccy(c1[k], today)
            if c2.ois_trigger == 0:
                crv_list[c1[k]] = [swap_build(c1[k], i) for i in h1]
            else:
                crv_list[c1[k]] = [ois_dc_build(c1[k], b=h1[i]) for i in np.arange(len(h1))]

        crv = flat_lst(list(crv_list.values()))
    else:
        crv = built_curve

    h2 = [crv[i].trade_date for i in np.arange(len(crv))]

    if fwd_tenor[-1] == 'd':
        fwd_tenor2 = ql.Days
    elif fwd_tenor[-1] == 'm':
        fwd_tenor2 = ql.Months
    else:
        fwd_tenor2 = ql.Years

    if ((bar_chg == 0) & (sprd == 0)):
        n_plots = 1
        n_obj = {'curve': [n_ccy * n_chg]}
    elif ((bar_chg == 1) & (sprd == 0)):
        if (n_chg < 3):
            n_plots = 2
            n_obj = {'curve': [n_ccy * n_chg], 'chg': [n_ccy]}

        elif ((n_ccy == 1) & (n_chg > 3)):
            n_plots = 2
            n_obj = {'curve': [n_ccy * n_chg], 'chg': [n_chg - 1]}
        else:
            n_plots = 1 + n_ccy
            n_obj = {'curve': [n_ccy * n_chg], 'chg': [n_chg - 1] * n_ccy}

    elif ((bar_chg == 0) & (sprd == 1)):
        n_plots = 2
        n_obj = {'curve ': [n_ccy * n_chg], 'chg': [n_ccy - 1]}

    else:
        if (n_chg < 3):
            n_plots = 3
            n_obj = {'curve': [n_ccy * n_chg], 'sprd': [n_ccy - 1], 'chg': [n_ccy - 1]}
        elif ((n_ccy == 2) & (n_chg > 3)):
            n_plots = 3
            n_obj = {'curve': [n_ccy * n_chg], 'sprd': [n_ccy - 1], 'chg': [n_chg - 1]}
        else:
            n_plots = 1 + n_ccy
            n_obj = {'curve': [n_ccy * n_chg], 'sprd': [n_ccy - 1], 'chg': [n_chg - 1] * (n_ccy - 1)}

    #### Set Layout?

    #### Get ALL Data
    rates = dict([(key, []) for key in c1])
    for i in np.arange(len(crv)):
        if crv[i].ois_trigger == 1:
            d2 = crv[i].ref_date
            ql.Settings.instance().evaluationDate = crv[i].trade_date
            d3 = d2 + ql.Period(max_tenor, ql.Years)
            #       dates_in = [ ql.Date(serial) for serial in range(d2.serialNumber(),d3.serialNumber()+1) ]   #### dates for plotting !!
            #       yr_axis = [(dates_in[i]-dates_in[0])/365.25 for i in range(len(dates_in)) ]
            dates_in2 = ql.MakeSchedule(d2, d3, ql.Period(int_tenor))  #### dates for pricing !!
            yr_axis = [(dates_in2[i] - dates_in2[0]) / 365.25 for i in range(len(dates_in2))]
            rates_c = [100 * crv[i].curve.forwardRate(d, crv[i].cal.advance(d, int(fwd_tenor[0]), fwd_tenor2),
                                                      ql.Actual365Fixed(), ql.Simple).rate() for d in dates_in2]
            rates[c1[int(np.floor(i / len(h1)))]].append(rates_c)

        else:
            yr_axis = np.arange(max_tenor)
            rates_c = []
            j = 0
            while j < max_tenor:
                rates_c.append(Swap_Pricer([[crv[i], j, tail]]).rate[0])
                j += 1
            rates[c1[int(np.floor(i / len(h1)))]].append(rates_c)

    rates_change = dict([(key, []) for key in c1])
    for j in rates.keys():
        k = 1
        while k < n_chg:
            rates_diff = 100 * (np.array(rates[j][0]) - np.array(rates[j][k]))
            rates_change[j].append(rates_diff.tolist())
            k += 1
    bar_dict = rates_change

    if sprd == 1:
        c2 = [c1[0] + ' - ' + c1[i] for i in np.arange(1, n_ccy)]
        spreads = dict([(key, []) for key in c2])
        for i, j in enumerate(spreads.keys()):
            spreads[j] = 100 * (np.array(rates[list(rates.keys())[0]]) - np.array(rates[list(rates.keys())[i + 1]]))

        spreads_change = dict([(key, []) for key in c2])
        for j in spreads.keys():
            k = 1
            while k < n_chg:
                sprd_chg = 1 * (np.array(spreads[j][0]) - np.array(spreads[j][k]))
                spreads_change[j].append(sprd_chg.tolist())
                k += 1
        bar_dict = spreads_change

    ## Plot curve
    s_plot = []
    yr_axis2 = np.array(yr_axis)
    s1 = figure(width=p_dim[0], height=p_dim[1], tools = ["pan","hover","wheel_zoom","box_zoom","save","reset","help"], toolbar_location='left')
    s1.xgrid.visible = False
    s1.ygrid.visible = False
    s1.add_layout(Legend(), 'right')

    for i in rates.keys():
        [s1.line(yr_axis2, rates[i][j],
                 legend_label = [str(ccy(i,today).curncy)+': '+str(h2[j]), i+': '+str(h2[j])][label_curve_name],
                 line_width = 2,
                 color =  Category20[20][ 2*(list(rates.keys()).index(i)+ (j* (len(list(rates.keys())) == 1))) ], alpha = (1.0-(0.4*j)),
                 muted_color = Category20[20][ 2*(list(rates.keys()).index(i)+ (j* (len(list(rates.keys())) == 1))) ], muted_alpha=0.2) for j in np.arange(n_chg)]
#       [s1.circle(yr_axis2, rates[i][j], size=0.5, fill_color= Category20[20][2*list(rates.keys()).index(i)]) for j in np.arange(n_chg)]
#       print(Category20[20][2*list(rates.keys()).index(i)])
        if len(curve_fill) > 0:
            for j in np.arange(len(curve_fill)):
                x_0 = np.where([(yr_axis2 > curve_fill[j][0])])[1][0]
                x_1 = np.where([(yr_axis2 < curve_fill[j][1])])[1][-1]
                s1.varea(x=yr_axis2[x_0:x_1+1], y1=[0]*len(yr_axis2[x_0:x_1+1]), y2=rates[i][0][x_0:x_1+1], color="green", alpha=0.7)

    s1.legend.label_text_font = "calibri"
    s1.legend.label_text_font_size = "7pt"
    s1.legend.glyph_height = 5
    s1.legend.label_height = 5
    s1.legend.spacing = 1
    s1.legend.click_policy = "mute"
    s1.xaxis.axis_label = 'Rate'
    s1.yaxis.axis_label = 'Tenor'
    s_plot.append(s1)

    ## Plot Sprd
    if sprd == 1:
        s2 = figure(width=p_dim[0], height=p_dim[1]-100, tools = ["pan","hover","wheel_zoom","box_zoom","save","reset","help"], toolbar_location='left')
        s2.xgrid.grid_line_dash = 'dotted'
        s2.ygrid.grid_line_dash = 'dotted'
        s2.add_layout(Legend(), 'right')
        for j in spreads.keys():
            s2.line( yr_axis , spreads[j][0],
                     line_width = 2,
                     legend_label = str(j),
                     color = Category20[20][2*list(bar_dict.keys()).index(j)], alpha = 1.0,
                     muted_color = Category20[20][2*list(bar_dict.keys()).index(j)], muted_alpha=0.2)
        s2.legend.label_text_font = "calibri"
        s2.legend.label_text_font_size = "7pt"
        s2.legend.glyph_height = 5
        s2.legend.label_height = 5
        s2.legend.spacing = 1
        s2.legend.click_policy = "mute"
        s2.xaxis.axis_label = 'Spread'
        s2.yaxis.axis_label = 'Tenor'
        s_plot.append(s2)


    ## Plot Chg
    if sprd == 1:
        start_sub_chg = 2
    else:
        start_sub_chg = 1

    if bar_chg == 1:
        n_sub_chg = len(n_obj['chg'])
        if n_sub_chg == 1:
            s3 = figure(width=p_dim[0], height=p_dim[1]-100, tools = ["pan","hover","wheel_zoom","box_zoom","save","reset","help"], toolbar_location='left')
            s3.xgrid.grid_line_dash = 'dotted'
            s3.ygrid.grid_line_dash = 'dotted'
            s3.add_layout(Legend(), 'right')
            width = 0.15
            bar_yr_axis = yr_axis
            for i in bar_dict.keys():
                for j in np.arange(len(bar_dict[i])):
                    s3.vbar(x=np.array(bar_yr_axis), top=bar_dict[i][j],
                            legend_label=i+': '+str(h1[j+1]),
                            width=width,
                            color = Category20[20][ 2*(list(bar_dict.keys()).index(i)+ (j* (len(list(bar_dict.keys())) == 1))) ], alpha = (1.0-(0.4*j)),
                            muted_color = Category20[20][ 2*(list(bar_dict.keys()).index(i)+ (j* (len(list(bar_dict.keys())) == 1))) ], muted_alpha=0.2)
                    bar_yr_axis = np.array(bar_yr_axis)+width+0.1
            s3.legend.label_text_font = "calibri"
            s3.legend.label_text_font_size = "7pt"
            s3.legend.glyph_height = 5
            s3.legend.label_height = 5
            s3.legend.spacing = 1
            s3.legend.click_policy = "mute"
            s3.xaxis.axis_label = 'Chg'
            s3.yaxis.axis_label = 'Tenor'
            s_plot.append(s3)
        else:
            for j in np.arange(n_sub_chg):
                s4 = figure(width=p_dim[0], height=p_dim[1]-100, tools = ["pan","hover","wheel_zoom","box_zoom","save","reset","help"], toolbar_location='left')
                s4.xgrid.grid_line_dash = 'dotted'
                s4.ygrid.grid_line_dash = 'dotted'
                s4.add_layout(Legend(), 'right')
                width = 0.15
                bar_yr_axis = yr_axis
                for i in np.arange(len(bar_dict[ list(bar_dict.keys())[j]  ])):
                    s4.vbar(x=np.array(bar_yr_axis)+1, top=bar_dict[list(bar_dict.keys())[j]][i],
                            legend_label= list(bar_dict.keys())[j]+': '+str(h1[i+1]),
                            width=width,
                            color = Category20[20][(j+(2*i)+1)],alpha = 1.0,
                            muted_color = Category20[20][(j+(2*i)+1)], muted_alpha=0.2)
                    bar_yr_axis = np.array(bar_yr_axis)+width+0.1
                    s4.legend.label_text_font_size = "7pt"
                    s4.legend.glyph_height = 5
                    s4.legend.label_height = 5
                    s4.legend.label_text_font_size = "9pt"
                    s4.legend.spacing = 1
                    s4.legend.click_policy = "mute"
                    s_plot.append(s4)

#    layout = column(*s_plot)
    return s_plot


def ecfc_plot(a, b, c, contrib1 = 'GS', off = 'IMF'):
#    a = 'GDP'
#    b = 'US'
#    c = '2024'
#    contrib1 = 'GS'
#    off = 'FED'

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
    df1['date'] = [df1['date'][i].date() for i in np.arange(len(df1))]
    df2 = con.bdh("EC"+e+b+" "+c[-2:]+" "+off+" Index", 'PX_LAST',start, t_stg, longdata=True)

    d1 = [ql_to_datetime(cal.advance(today, ql.Period( int(-10-i), ql.Days))) for i in np.arange(240)]
    m1 = [df1[(df1['date'] > d1[i]) & (df1['date'] < ql_to_datetime(cal.advance(today, ql.Period( int(0-i), ql.Days)))) ]['value'].mean()  for i in np.arange(len(d1))]

    c1 = df1['ticker'].unique()

    s1 = figure(width=600, height=300, tools = ["pan","wheel_zoom","box_zoom","save","reset","help"], toolbar_location='left', x_axis_type='datetime')
    s1.xaxis.formatter=DatetimeTickFormatter(days="%d-%b-%y", months="%d-%b-%y")
    s1.add_tools(HoverTool(tooltips=[('date', '$x{%b-%y}'), ('y', '$y')],
                           formatters={'$x': 'datetime'}))
    s1.xgrid.visible = False
    s1.ygrid.visible = False
    s1.add_layout(Legend(), 'right')

    for i in np.arange(len(c1)):
        if c1[i].split()[2] == contrib1:
            c2 = 'red'
            c3 = contrib1+": "+str(df1[df1['ticker'] == "EC"+e+b+" "+c[-2:]+" "+contrib1+" Index"].iloc[-1]['value'])
        else:
            c2 = 'silver'
            c3 = ''
        a1 = df1[df1['ticker'] == c1[i]]
        s1.line(a1['date'], a1['value'], legend_label=c3, color=c2, alpha=1.0, muted_alpha = 0.25)

        s1.legend.label_text_font = "calibri"
        s1.legend.label_text_font_size = "9pt"
        s1.legend.spacing = 1
        s1.legend.click_policy = "mute"
        s1.xaxis.axis_label = 'Value'
        s1.yaxis.axis_label = 'Date'

    s1.line(df2['date'], df2['value'], color = 'forestgreen', legend_label = off+": "+str(df2['value'][len(df2)-1]), alpha=1.0)
    s1.line( np.array(d1), np.array(m1), color = 'blue', legend_label = 'Avg: '+str(np.round(m1[0],2)), alpha=1.0)
    s1.title.text = b+" "+a+" forecast: "+c
    s1.title.text_font = "calibri"
    s1.title.text_font_size = '10pt'
    s1.title.align = 'left'

    return s1



def plt_inf_curve_bokeh(c1, h1=[0], max_tenor=30, bar_chg = 0, sprd = 0, built_curve=0 ,name = '',p_dim=[700,350]):
#    c1 = ['UKRPI','HICPxT']
#    h1 = [0,-10]
#    bar_chg = 1
#    sprd = 1
#    max_tenor = 30
#    name = ''

    n_ccy = len(c1)
    n_chg = len(h1)

    os.chdir('C:\\Users\A00007579\PycharmProjects\pythonProject')
    today = ql.Date(datetime.datetime.now().day,datetime.datetime.now().month,datetime.datetime.now().year)

    if built_curve == 0:
        crv_list = {}
        for k in np.arange(n_ccy):
            c2 = ccy_infl(c1[k], today)
            crv_list[c1[k]] = [infl_zc_swap_build( c1[k] ,i ,base_month_offset=0) for i in h1]

        crv = flat_lst(list(crv_list.values()))
    else:
        crv = built_curve

    ref_dates = [crv[i].ref_date for i in np.arange(len(crv))]

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
    s_plot = []
    s1 = figure(width=p_dim[0], height=p_dim[1], tools = ["pan","hover","wheel_zoom","box_zoom","save","reset","help"], toolbar_location='left')
    s1.xgrid.visible = False
    s1.ygrid.visible = False
    s1.add_layout(Legend(), 'right')

    for i in rates.keys():
        [s1.line(yr_axis+1, rates[i][j],
                legend_label = i+': '+str(ref_dates[j]),
                line_width = 2,
                color =  Category20[20][ 2*(list(rates.keys()).index(i)+ (j* (len(list(rates.keys())) == 1))) ], alpha = (1.0-(0.4*j)),
                muted_color = Category20[20][ 2*(list(rates.keys()).index(i)+ (j* (len(list(rates.keys())) == 1))) ], muted_alpha=0.2) for j in np.arange(n_chg)]

    s1.legend.label_text_font = "calibri"
    s1.legend.label_text_font_size = "5pt"
    s1.legend.glyph_height = 5
    s1.legend.label_height = 5
    s1.legend.spacing = 1
    s1.legend.click_policy = "mute"
    s1.xaxis.axis_label = 'ZC_Rate'
    s1.yaxis.axis_label = 'Tenor'
    s_plot.append(s1)

    ### Plot Sprd
    if sprd == 1:
        s2 = figure(width=p_dim[0], height=p_dim[1]-150, tools = ["pan","hover","wheel_zoom","box_zoom","save","reset","help"], toolbar_location='left')
        s2.xgrid.grid_line_dash = 'dotted'
        s2.ygrid.grid_line_dash = 'dotted'
        s2.add_layout(Legend(), 'right')
        for j in spreads.keys():
            s2.line( yr_axis+1 , spreads[j][0],
                        line_width = 2,
                        legend_label = str(j),
                        color = Category20[20][2*list(bar_dict.keys()).index(j)], alpha = 1.0,
                        muted_color = Category20[20][2*list(bar_dict.keys()).index(j)], muted_alpha=0.2)
        s2.legend.label_text_font = "calibri"
        s2.legend.label_text_font_size = "9pt"
        s2.legend.spacing = 1
        s2.legend.click_policy = "mute"
        s2.xaxis.axis_label = 'Spread'
        s2.yaxis.axis_label = 'Tenor'
        s_plot.append(s2)

    ### Plot Chg
    if sprd == 1:
        start_sub_chg = 2
    else:
        start_sub_chg = 1

    if bar_chg == 1:
        n_sub_chg = len(n_obj['chg'])
        if n_sub_chg == 1:
            s3 = figure(width=p_dim[0], height=p_dim[1]-150, tools = ["pan","hover","wheel_zoom","box_zoom","save","reset","help"], toolbar_location='left')
            s3.xgrid.grid_line_dash = 'dotted'
            s3.ygrid.grid_line_dash = 'dotted'
            s3.add_layout(Legend(), 'right')
            width = 0.15
            bar_yr_axis = yr_axis
            for i in bar_dict.keys():
                for j in np.arange(len(bar_dict[i])):
                    s3.vbar(x=np.array(bar_yr_axis)+1, top=bar_dict[i][j],
                                legend_label = i+': '+str(h1[j+1]),
                                width = width,
                                color = Category20[20][ 2*(list(bar_dict.keys()).index(i)+ (j* (len(list(bar_dict.keys())) == 1))) ], alpha = (1.0-(0.4*j)),
                                muted_color = Category20[20][ 2*(list(bar_dict.keys()).index(i)+ (j* (len(list(bar_dict.keys())) == 1))) ], muted_alpha=0.2)
                    bar_yr_axis = bar_yr_axis+width+0.1
            s3.legend.label_text_font = "calibri"
            s3.legend.label_text_font_size = "9pt"
            s3.legend.spacing = 1
            s3.legend.click_policy = "mute"
            s3.xaxis.axis_label = 'Chg'
            s3.yaxis.axis_label = 'Tenor'
            s_plot.append(s3)

        else:
            for j in np.arange(n_sub_chg):
                s4 = figure(width=p_dim[0], height=p_dim[1], tools = ["pan","hover","wheel_zoom","box_zoom","save","reset","help"], toolbar_location='left')
                s4.xgrid.grid_line_dash = 'dotted'
                s4.ygrid.grid_line_dash = 'dotted'
                s4.add_layout(Legend(), 'right')
                width = 0.15
                bar_yr_axis = yr_axis
                for i in np.arange(len(bar_dict[ list(bar_dict.keys())[j]  ])):
                    s4.vbar(x=np.array(bar_yr_axis)+1, top=bar_dict[list(bar_dict.keys())[j]][i],
                                legend_label= list(bar_dict.keys())[j]+': '+str(h1[i+1]),
                                width = width,
                                color = Category20[20][(j+(2*i)+1)],alpha = 1.0,
                                muted_color = Category20[20][(j+(2*i)+1)], muted_alpha=0.2)
                    bar_yr_axis = bar_yr_axis+width+0.1
                    s4.legend.label_text_font = "calibri"
                    s4.legend.label_text_font_size = "9pt"
                    s4.legend.spacing = 1
                    s4.legend.click_policy = "mute"
                    s_plot.append(s4)


    return s_plot


def plot_tool_bbg(a, crv, p_dim=[550,275]):
#    a = [2,5,10]
#    crv = ois_dc_build('SOFR_DC', b=0)

    min_y = []
    max_y = []

    s1 = figure(width=p_dim[0], height=p_dim[1], tools = ["pan",'crosshair',"wheel_zoom","box_zoom","save","reset","help"], toolbar_location='right')
    s1.xgrid.visible = False
    s1.ygrid.visible = False
    s1.xaxis.formatter=DatetimeTickFormatter(days="%d-%b-%y", months="%d-%b-%y")
#    s1.add_tools(HoverTool(tooltips=[('date', '$x{%d.%b.%y}'), ('y', '$y')], formatters={'$x': 'datetime'}))

    for j in np.arange(len(a)):
        print(j)

        if len(a[j]) == 4:
            tk = []
            if a[j][0] == 0:
                tk.append(crv.bbgplot_tickers[0]+str(a[j][1])+' Curncy')
            else:
                tk.append(crv.bbgplot_tickers[1]+' '+str(a[j][0])+'Y'+str(a[j][1])+'Y'+ ' BLC Curncy')
            if a[j][3] != 0:
                if a[j][2] ==0:
                    tk.append(crv.bbgplot_tickers[0]+str(a[j][3]) + ' Curncy')
                else:
                    tk.append(crv.bbgplot_tickers[1] + ' ' + str(a[j][2]) + 'Y' + str(a[j][3]) + 'Y' + ' BLC Curncy')
            print(tk)

            x1 = con.bdh(tk , 'PX_LAST', '20210101', datetime.datetime.now().strftime('%Y%m%d'))
            x1 = x1.dropna()


            if len(tk) == 1:
                y = x1[(tk[0], 'PX_LAST')]
                lab1 = tk[0].split(' ')[len(tk[0].split(' '))//3]
            else:
                y = 100*(x1.iloc[:,1] - x1.iloc[:,0])
                lab1 = ' - '.join([tk[i].split(' ')[len(tk[i].split(' '))//3] for i in np.arange(len(tk))])

            ### mkt pricing
            t1 = crv.ref_date
            t2 = crv.cal.advance(t1, ql.Period('1Y'))
            schedule = ql.MakeSchedule(t1, t2, ql.Period('1W'))
            sch2 = [ datetime.datetime.combine(ql_to_datetime(schedule[int(i)]), datetime.time()) for i in np.arange(len(schedule))]

            if len(tk) == 1:
                fwd_curve = [Swap_Pricer([[crv, ql_to_datetime( crv.cal.advance(schedule[int(i)], ql.Period(str(a[j][0])+'Y'))  ).strftime('%d-%m-%Y')  ,a[j][1]]]).rate[0] for i in np.arange(len(schedule))]
            else:
                fwd_curve = [Swap_Pricer([[crv, ql_to_datetime(  crv.cal.advance(schedule[int(i)], ql.Period(str(a[j][0])+'Y'))   ).strftime('%d-%m-%Y'),a[j][1]],
                                          [crv, ql_to_datetime(  crv.cal.advance(schedule[int(i)], ql.Period(str(a[j][2])+'Y'))   ).strftime('%d-%m-%Y'),a[j][3]]]).spread for i in np.arange(len(schedule))]

            min_y.append(min(min(fwd_curve),min(y)))
            max_y.append(max(max(fwd_curve),max(y)))
            ratio = (max_y[0] - min_y[0]) / (max_y[j] - min_y[j])
            print('min_y: ', min_y, 'max_y: ', max_y, 'ratio: ', ratio)
            z = [ min_y[0]  + (y[k] - min_y[j])*ratio for k in np.arange(len(y))]
            fwd_curve_z = [ min_y[0]  + (fwd_curve[k] - min_y[j])*ratio for k in np.arange(len(fwd_curve))]

            s1.add_tools(HoverTool(tooltips=[('date', '$x{%d.%b.%y}'), ('y', '@ht')], formatters={'$x': 'datetime'}))

            s1.line('x', 'y', legend_label=lab1 , color=Category20[20][2*j], alpha=1.0, muted_alpha = 0.25, source = ColumnDataSource( data=dict(x= list(x1.index), y=z, ht=y)))
            s1.line('x', 'y', legend_label=lab1 , color=Category20[20][(2*j)+1], alpha=0.8, muted_alpha = 0.25, source = ColumnDataSource( data=dict(x= sch2, y=fwd_curve_z, ht=fwd_curve)))

        else:
            tk=[]
            for i in np.arange(len(a[j])):
                if a[j][i] != 0:
                    tk.append(crv.bbgplot_tickers[0]+str(a[j][i])+' Curncy')
            print(tk)

            x1 = con.bdh(tk, 'PX_LAST', '20210101', datetime.datetime.now().strftime('%Y%m%d'))
            x1 = x1.dropna()

            if len(tk) == 2:
                y = 100 * (x1.iloc[:, 1] - x1.iloc[:, 0])
            else:
                y = -100*(x1.iloc[:,2] + x1.iloc[:,0] - 2* x1.iloc[:,1])
            lab1 = '-'.join([str(a[j][i]) for i in np.arange(len(tk))])

            ### mkt pricing
            t1 = crv.ref_date
            t2 = crv.cal.advance(t1, ql.Period('1Y'))
            schedule = ql.MakeSchedule(t1, t2, ql.Period('1W'))
            sch2 = [datetime.datetime.combine(ql_to_datetime(schedule[int(i)]), datetime.time()) for i in
                    np.arange(len(schedule))]

            if len(tk) == 2:
                fwd_curve = [Swap_Pricer([[crv, ql_to_datetime( schedule[int(i)]).strftime('%d-%m-%Y'), a[j][0]],
                                          [crv, ql_to_datetime( schedule[int(i)]).strftime('%d-%m-%Y'), a[j][1]]]).spread for i in np.arange(len(schedule))]
            else:
                fwd_curve = [Swap_Pricer([[crv, ql_to_datetime(schedule[int(i)]).strftime('%d-%m-%Y'), a[j][0]],
                                          [crv, ql_to_datetime(schedule[int(i)]).strftime('%d-%m-%Y'), a[j][1]],
                                          [crv, ql_to_datetime(schedule[int(i)]).strftime('%d-%m-%Y'), a[j][2]]]).fly for i in np.arange(len(schedule))]


            min_y.append(min(min(fwd_curve),min(y)))
            max_y.append(max(max(fwd_curve),max(y)))
            ratio = (max_y[0] - min_y[0]) / (max_y[j] - min_y[j])
            print('min_y: ', min_y, 'max_y: ', max_y, 'ratio: ', ratio)
            z = [ min_y[0]  + (y[k] - min_y[j])*ratio for k in np.arange(len(y))]
            fwd_curve_z = [ min_y[0]  + (fwd_curve[k] - min_y[j])*ratio for k in np.arange(len(fwd_curve))]

            s1.add_tools(HoverTool(tooltips=[('date', '$x{%d.%b.%y}'), ('y', '@ht')], formatters={'$x': 'datetime'}))

            s1.line('x', 'y', legend_label=lab1, color=Category20[20][2*j], alpha=1.0, muted_alpha=0.25, source = ColumnDataSource( data=dict(x= list(x1.index), y=z, ht=y)  ))
            s1.line('x', 'y', legend_label=lab1, color=Category20[20][(2*j)+1], alpha=0.8, muted_alpha=0.25, source = ColumnDataSource( data=dict(x= sch2, y=fwd_curve_z, ht=fwd_curve)))


        s1.legend.label_text_font = "calibri"
        s1.legend.label_text_font_size = "9pt"
        s1.legend.location = 'top_left'
        s1.legend.click_policy = "mute"
        s1.legend.spacing = 1
        s1.yaxis.major_label_text_color = Category20[20][0]
        s1.yaxis.axis_line_color = Category20[20][0]
        s1.yaxis.major_tick_line_color = Category20[20][0]
        s1.yaxis.minor_tick_line_color = Category20[20][1]
#        s1.xaxis.axis_label = 'Date'
#        s1.yaxis.axis_label = 'Rate'

    return [s1]

