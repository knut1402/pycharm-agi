
import os
import pandas as pd
import numpy as np
import math
from scipy import stats
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
from OIS_DC_BUILD import ois_dc_build, get_wirp_hist, get_wirp
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
from bokeh.models import HoverTool, BoxZoomTool, ResetTool, Legend, DatetimeTickFormatter, LinearAxis, LinearColorMapper
from bokeh.models import ColumnDataSource, TabPanel, Tabs, LabelSet, Span, Range1d, FactorRange, CustomJS, TapTool
from bokeh.events import Tap
from bokeh.io import curdoc
from bokeh.layouts import row, column, gridplot, layout
from bokeh.palettes import Category10, brewer, Category20, Bright6
from bokeh.transform import factor_cmap
from bokeh.models.renderers import GlyphRenderer
from itertools import accumulate
from bokeh.colors import RGB
from matplotlib import cm

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
#    s1.add_layout(Legend(), 'right')

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
    s1.legend.background_fill_alpha = 0.0
    s1.legend.click_policy = "mute"
    s1.xaxis.axis_label = 'Rate'
    s1.yaxis.axis_label = 'Tenor'
    s_plot.append(s1)

    ## Plot Sprd
    if sprd == 1:
        s2 = figure(width=p_dim[0], height=p_dim[1]-100, tools = ["pan","hover","wheel_zoom","box_zoom","save","reset","help"], toolbar_location='left')
        s2.xgrid.grid_line_dash = 'dotted'
        s2.ygrid.grid_line_dash = 'dotted'
#        s2.add_layout(Legend(), 'right')
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
        s2.legend.background_fill_alpha = 0.0
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
#            s3.add_layout(Legend(), 'right')
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
            s3.legend.background_fill_alpha = 0.0
            s3.legend.click_policy = "mute"
            s3.xaxis.axis_label = 'Chg'
            s3.yaxis.axis_label = 'Tenor'
            s_plot.append(s3)
        else:
            for j in np.arange(n_sub_chg):
                s4 = figure(width=p_dim[0], height=p_dim[1]-100, tools = ["pan","hover","wheel_zoom","box_zoom","save","reset","help"], toolbar_location='left')
                s4.xgrid.grid_line_dash = 'dotted'
                s4.ygrid.grid_line_dash = 'dotted'
#                s4.add_layout(Legend(), 'right')
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
                    s4.legend.background_fill_alpha = 0.0
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
        s1.legend.background_fill_alpha = 0.0
        s1.legend.click_policy = "mute"
        s1.xaxis.axis_label = 'Date'
        s1.yaxis.axis_label = 'Value'

    s1.line(df2['date'], df2['value'], color = 'forestgreen', legend_label = off+": "+str(df2['value'][len(df2)-1]), alpha=1.0)
    s1.line( np.array(d1), np.array(m1), color = 'blue', legend_label = 'Avg: '+str(np.round(m1[0],2)), alpha=1.0)
    s1.title.text = b+" "+a+" forecast: "+c
    s1.title.text_font = "calibri"
    s1.title.text_font_size = '10pt'
    s1.title.align = 'left'

    return s1


def plt_inf_curve_bokeh(c1, h1=[0], max_tenor=30, bar_chg = 0, sprd = 0, built_curve=0 ,name = '',p_dim=[700,350]):
#    c1 = ['HICPxT']
#    h1 = [-1,'04-01-2024']
#    bar_chg = 1
#    sprd = 0
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

    zc_late = dict([(key, dict([(key2, []) for key2 in ['par_nodes','par_zc']]) ) for key in c1])
    for i in np.arange(0,len(crv),len(h1)):
        zc_all_mat = crv[0].rates['maturity'].str[:-1].tolist()
        zc_late[c1[i]]['par_nodes'] = zc_all_mat[:zc_all_mat.index(str(max_tenor))+1]
        zc_late[c1[i]]['par_zc'] = crv[0].rates['px'].tolist()[:zc_all_mat.index(str(max_tenor))+1]

    rates = dict([(key, []) for key in c1])
    for i in np.arange(len(crv)):
        yr_axis = np.arange(max_tenor)
        rates_c = []
        j = 0
        while j < max_tenor:
            start_sw = inf_bases_dict[list(inf_bases_dict.keys())[int(np.floor(i/len(h1)))]][0] +  ql.Period(str(j)+"Y")
#            print(i,j,start_sw)
            rates_c.append(Infl_ZC_Pricer(crv[i], start_sw, 1, lag = 0,  use_mkt_fixing=1).zc_rate)
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
#    s1.add_layout(Legend(), 'right')

    for i in rates.keys():
        [s1.line(yr_axis+1, rates[i][j],
                legend_label = i+': '+str(ref_dates[j])+': '+ ql_to_datetime(inf_bases_dict[i][0]).strftime('%b-%y'),
                line_width = 2,
                color =  Category20[20][ 2*(list(rates.keys()).index(i)+ (j* (len(list(rates.keys())) == 1))) ], alpha = (1.0-(0.4*j)),
                muted_color = Category20[20][ 2*(list(rates.keys()).index(i)+ (j* (len(list(rates.keys())) == 1))) ], muted_alpha=0.2) for j in np.arange(n_chg)]

    for i in zc_late.keys():
        s1.circle(  list(map(int, zc_late[c1[0]]['par_nodes'])), zc_late[c1[0]]['par_zc'],
                 color=Category20[20][2 * (list(zc_late.keys()).index(i) )],
                 alpha=0.7,
                 muted_alpha=0.2)

    s1.legend.label_text_font = "calibri"
    s1.legend.label_text_font_size = "7pt"
    s1.legend.glyph_height = 5
    s1.legend.label_height = 5
    s1.legend.spacing = 1
    s1.legend.background_fill_alpha = 0.0
    s1.legend.click_policy = "mute"
    s1.xaxis.axis_label = 'ZC_Rate'
    s1.yaxis.axis_label = 'Tenor'
    s_plot.append(s1)

    ### Plot Sprd
    if sprd == 1:
        s2 = figure(width=p_dim[0], height=p_dim[1]-100, tools = ["pan","hover","wheel_zoom","box_zoom","save","reset","help"], toolbar_location='left')
        s2.xgrid.grid_line_dash = 'dotted'
        s2.ygrid.grid_line_dash = 'dotted'
#        s2.add_layout(Legend(), 'right')
        for j in spreads.keys():
            s2.line( yr_axis+1 , spreads[j][0],
                        line_width = 2,
                        legend_label = str(j),
                        color = Category20[20][2*list(bar_dict.keys()).index(j)], alpha = 1.0,
                        muted_color = Category20[20][2*list(bar_dict.keys()).index(j)], muted_alpha=0.2)
        s2.legend.label_text_font = "calibri"
        s2.legend.label_text_font_size = "7pt"
        s2.legend.spacing = 1
        s2.legend.background_fill_alpha = 0.0
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
            s3 = figure(width=p_dim[0], height=p_dim[1]-100, tools = ["pan","hover","wheel_zoom","box_zoom","save","reset","help"], toolbar_location='left')
            s3.xgrid.grid_line_dash = 'dotted'
            s3.ygrid.grid_line_dash = 'dotted'
#            s3.add_layout(Legend(), 'right')
            width = 0.15
            bar_yr_axis = yr_axis
            for i in bar_dict.keys():
                for j in np.arange(len(bar_dict[i])):
                    s3.vbar(x=np.array(bar_yr_axis)+1, top=bar_dict[i][j],
                                legend_label = i+': '+str(h1[j+1])+': '+ ql_to_datetime(inf_bases_dict[i][0]).strftime('%b-%y'),
                                width = width,
                                color = Category20[20][ 2*(list(bar_dict.keys()).index(i)+ (j* (len(list(bar_dict.keys())) == 1))) ], alpha = (1.0-(0.4*j)),
                                muted_color = Category20[20][ 2*(list(bar_dict.keys()).index(i)+ (j* (len(list(bar_dict.keys())) == 1))) ], muted_alpha=0.2)
                    bar_yr_axis = bar_yr_axis+width+0.1
            s3.legend.label_text_font = "calibri"
            s3.legend.label_text_font_size = "7pt"
            s3.legend.spacing = 1
            s3.legend.background_fill_alpha = 0.0
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
                    s4.legend.background_fill_alpha = 0.0
                    s4.legend.click_policy = "mute"
                    s_plot.append(s4)


    return s_plot



def plot_tool_bbg(a, crv, st_date, p_dim=[550,275]):
#    a = [2,5,10]
#    crv = ois_dc_build('SOFR_DC', b=0)
    st_date = st_date.strftime('%Y%m%d')
    print('st_date:', st_date)

    min_y = []
    max_y = []
    v_reg = []
    fwd_reg = []
    lab_reg = []

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

            x1 = con.bdh(tk , 'PX_LAST', st_date, datetime.datetime.now().strftime('%Y%m%d'))
            x1 = x1.dropna()


            if len(tk) == 1:
                y = x1[(tk[0], 'PX_LAST')]
                lab1 = tk[0].split(' ')[len(tk[0].split(' '))//3]
            else:
                y = 100*(x1.iloc[:,1] - x1.iloc[:,0])
                lab1 = ' - '.join([tk[i].split(' ')[len(tk[i].split(' '))//3] for i in np.arange(len(tk))])

            v_reg.append(y)
            lab_reg.append(lab1)

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
            fwd_reg.append(fwd_curve)

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

            x1 = con.bdh(tk, 'PX_LAST', st_date, datetime.datetime.now().strftime('%Y%m%d'))
            x1 = x1.dropna()

            if len(tk) == 2:
                y = 100 * (x1.iloc[:, 1] - x1.iloc[:, 0])
            else:
                y = -100*(x1.iloc[:,2] + x1.iloc[:,0] - 2* x1.iloc[:,1])
            lab1 = '-'.join([str(a[j][i]) for i in np.arange(len(tk))])

            v_reg.append(y)
            lab_reg.append(lab1)

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
            fwd_reg.append(fwd_curve)


            min_y.append(min(min(fwd_curve),min(y)))
            max_y.append(max(max(fwd_curve),max(y)))
            ratio = (max_y[0] - min_y[0]) / (max_y[j] - min_y[j])
            print('min_y: ', min_y, 'max_y: ', max_y, 'ratio: ', ratio)
            z = [ min_y[0]  + (y[k] - min_y[j])*ratio for k in np.arange(len(y))]
            fwd_curve_z = [ min_y[0]  + (fwd_curve[k] - min_y[j])*ratio for k in np.arange(len(fwd_curve))]

            s1.add_tools(HoverTool(tooltips=[('date', '$x{%d.%b.%y}'), ('y', '@ht')], formatters={'$x': 'datetime'}))

            s1.line('x', 'y', legend_label=lab1, color=Category20[20][2*j], alpha=1.0, muted_alpha=0.25, source = ColumnDataSource( data=dict(x= list(x1.index), y=z, ht=y)  ))
            s1.line('x', 'y', legend_label=lab1, color=Category20[20][(2*j)+1], alpha=0.8, muted_alpha=0.25, source = ColumnDataSource( data=dict(x= sch2, y=fwd_curve_z, ht=fwd_curve)))

        tabs = Tabs(tabs=[TabPanel(child=s1)])
        s1.legend.label_text_font = "calibri"
        s1.legend.label_text_font_size = "9pt"
        s1.legend.location = 'top_left'
        s1.legend.click_policy = "mute"
        s1.legend.spacing = 1
        s1.legend.background_fill_alpha = 0.0
        s1.yaxis.major_label_text_color = Category20[20][0]
        s1.yaxis.axis_line_color = Category20[20][0]
        s1.yaxis.major_tick_line_color = Category20[20][0]
        s1.yaxis.minor_tick_line_color = Category20[20][1]
#        s1.xaxis.axis_label = 'Date'
#        s1.yaxis.axis_label = 'Rate'
    if len(a) == 2:
#        print('v_reg:', v_reg)
#        print('len_v_reg ===', len(v_reg))
        df_x1 = pd.DataFrame(v_reg[0])
        df_x2 = pd.DataFrame(v_reg[1])
        df_reg = pd.merge(df_x1, df_x2, left_index=True, right_index=True)
        df_reg = df_reg.dropna()

        x = df_reg.iloc[:, 0]
        y = df_reg.iloc[:, 1]
        #        print('x_reg', x)
        #        print('y_reg', y)

        tab1 = TabPanel(child=s1, title="plot")

        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        y_reg_fit = intercept + (slope * x)
        residuals = y - y_reg_fit
        residuals_fwds = fwd_reg[1] - intercept - (slope * np.array(fwd_reg[0]))

        s2 = figure(width=p_dim[0], height=p_dim[1], tools=["pan", 'crosshair', "wheel_zoom", "box_zoom", "save", "reset", "help"],
                    toolbar_location='right')
        s2.add_tools(HoverTool(tooltips=[('x', '$x'), ('y', '$y')]))
        s2.xgrid.visible = False
        s2.ygrid.visible = False
        s2_alphas = np.linspace(0.1, 1.0, len(df_reg))
        s2_source = ColumnDataSource(data=dict(x=x, y=y, s2_alphas=s2_alphas))
        s2.circle('x', 'y', size=5, alpha='s2_alphas', color="navy", source=s2_source)
        s2.circle(fwd_reg[0], fwd_reg[1], size=5, alpha=0.9, color="darkseagreen")
        s2.line(x, y_reg_fit, color="red")
        s2.xaxis.axis_label = lab_reg[0]
        s2.yaxis.axis_label = lab_reg[1]
        tab2 = TabPanel(child=s2, title="regression")

        s3 = figure(width=p_dim[0], height=p_dim[1], tools=["pan", 'crosshair', "wheel_zoom", "box_zoom", "save", "reset", "help"],
                    toolbar_location='right')
        s3.xgrid.visible = False
        s3.ygrid.visible = False
        s3.xaxis.formatter = DatetimeTickFormatter(days="%d-%b-%y", months="%d-%b-%y")
        s3.circle(df_reg.index, residuals, size=2)
        s3.circle(sch2, residuals_fwds, size=2, color = 'darkseagreen', alpha=0.3)
        s3.line([min(df_reg.index), max(sch2)], [0, 0], color="lightsteelblue", line_width=1)  # Zero line for reference
        tab3 = TabPanel(child=s3, title="residuals")

        tabs = Tabs(tabs=[tab1, tab2, tab3])
#        show(tabs)

    return [tabs]


### removing certain plots from bokeh charts
def remove_glyphs(figure, glyph_name_list):
    renderers = figure.select(dict(type=GlyphRenderer))
    for r in renderers:
        if r.name in glyph_name_list:
            col = r.glyph.y
            r.data_source.data[col] = [np.nan] * len(r.data_source.data[col])


def plot_simple_wirp(dt1, gen=0):
#    dt1 =  get_wirp( [['SOFR_DC'], [datetime.date(2024, 2, 12), datetime.date(2024, 2, 9)]] )

    crv = list(dt1[0].keys())[0]
    fixings = dt1[1]

    today = ql.Date(datetime.datetime.now().day, datetime.datetime.now().month, datetime.datetime.now().year)

    meet_hist = ccy(crv ,today).ois_meet_hist
    month     = [dt1[0][crv][i]['meet_date'].tolist() for i in np.arange(2)]
    step      = [np.around(dt1[0][crv][i]['step'],1).tolist() for i in np.arange(2)]
    cum       = [np.around(dt1[0][crv][i]['cum'],0).tolist() for i in np.arange(2)]
    fwd_base  = [dt1[0][crv][i]['cb'].tolist() for i in np.arange(2)]

    cut_off = month[1].index(month[0][0])
    if cut_off != 0:
        month_chg =  [month[m][:cut_off]+month[0] for m in np.arange(1,2)]    ##### augmented list of months
        step_chg  =  [np.round(100*([tup[1] for item in month_chg[0] for tup in fixings[crv] if tup[0] == item] - np.array(fwd_base[1][:cut_off])),1).tolist() +
                      (np.array(step[0][:-cut_off])-np.array(step[m][cut_off:])).tolist() +
                      cut_off*[0] for m in np.arange(1,2)]
        cum_chg   =  [list(accumulate(step_chg[0]))]
    else:
        month_chg = [month[0]]
        step_chg  = [(np.array(step[0]) - np.array(step[1])).tolist()]
        cum_chg   = [(np.array(cum[0]) - np.array(cum[1])).tolist()]

    itr = len(step_chg[0]) - len(step[0])
    _month = month_chg[0]
    _step  = itr * [0] + step[0]
    _cum   = itr * [0] + cum[0]
    _fwd_base = [fixings[crv][i][1] for i in np.arange(len(fixings[crv]))][:cut_off] + fwd_base[0]

    s1_source = ColumnDataSource(data=dict(x=_month, y=_step, z=_cum, k=_fwd_base, x2=month_chg[0], y2=step_chg[0], z2=cum_chg[0]))

    s1 = figure(x_range=_month, width=550, height=400, tools=["pan", "tap", "wheel_zoom", "box_zoom", "save", "reset", "help"], toolbar_location='right')
    s1.xgrid.visible = False
    s1.ygrid.visible = False
    s1.vbar(x='x', top='y', width=0.7, source=s1_source, color='lightsteelblue')
    s1.circle(x='x2', y='y2', size=8, source=s1_source, color='firebrick', alpha=0.7)
    zero_line = Span(location=0, dimension='width', line_color='darkseagreen', line_width=1)
    s1.renderers.extend([zero_line])
    labels_1 = LabelSet(x='x', y='y', text='y', level='glyph', text_align='center', y_offset=-16, source=s1_source, text_font_size='10px', text_color='midnightblue')
    labels_1a = LabelSet(x='x2', y='y2', text='y2', level='glyph', text_align='center', y_offset=-16, source=s1_source, text_font_size='8px', text_color='firebrick')
    s1.add_layout((labels_1))
    s1.add_layout((labels_1a))
    s1.xaxis.major_label_orientation = math.pi / 4
    s1.y_range = Range1d(min(min(_step), min(step_chg[0])) - 5, max(max(_step), max(step_chg[0])) + 5)

    s2 = figure(x_range=_month, width=550, height=400, tools=["pan", "tap", "hover", "wheel_zoom", "box_zoom", "save", "reset", "help"], toolbar_location='right')
    s2.xgrid.visible = False
    s2.ygrid.visible = False
    s2.vbar(x='x', top='z', width=0.7, source=s1_source, color='lightsteelblue')
    s2.circle(x='x2', y='z2', size=10, source=s1_source, color='firebrick', alpha=0.7)
    zero_line = Span(location=0, dimension='width', line_color='darkseagreen', line_width=1)
    s2.renderers.extend([zero_line])
    labels_1 = LabelSet(x='x', y='z', text='z', level='glyph', text_align='center', y_offset=3, source=s1_source, text_font_size='9px', text_color='midnightblue')
    labels_2 = LabelSet(x='x', y='z', text='k', level='glyph', text_align='center', y_offset=-10, source=s1_source, text_font_size='9px', text_color='firebrick')
    labels_1b = LabelSet(x='x2', y='z2', text='z2', level='glyph', text_align='center', y_offset=-16, source=s1_source, text_font_size='8px', text_color='blueviolet')
    s2.add_layout((labels_1))
    s2.add_layout((labels_1b))
    s2.add_layout((labels_2))
    s2.xaxis.major_label_orientation = math.pi / 4
    s2.y_range = Range1d(min(min(_cum), min(cum_chg[0])) - 10, max(max(_cum), max(cum_chg[0])) + 10)

    tab1 = TabPanel(child=s1, title="step")
    tab2 = TabPanel(child=s2, title="cum")
    tabs = Tabs(tabs=[tab1, tab2])

    s3 = figure(width=570, height=400, tools=["pan", "crosshair", "wheel_zoom", "box_zoom", "save", "reset", "help"], toolbar_location='right')
    s3.xaxis.formatter = DatetimeTickFormatter(days="%d-%b-%y", months="%d-%b-%y")
    s3.add_tools(HoverTool(tooltips=[('date', '$x{%d.%b.%y}'), ('y', '$y')], formatters={'$x': 'datetime'}))
    s3.xgrid.visible = False
    s3.ygrid.visible = False
    s3.visible = False
    zero_line = Span(location=0, dimension='width', line_color='darkseagreen', line_width=1)
    s3.renderers.extend([zero_line])
    s3.title = 'Meeting Hist'
    s3.min_border_top = 30
    s3.min_border_left = 50

    taptool_1 = s1.select(type=TapTool)
    def callback_1(event):
        try:
            remove_glyphs(s3, 'meet_plot')
            s3.legend.items = []
        except:
            pass
        out_indicies = s1_source.selected.indices
        if len(out_indicies) > 0:
            if gen == 0:
                meet = s1_source.data['x'][int(out_indicies[0])]
                df_meet_hist = meet_hist[meet_hist['meet'] == meet].reset_index(drop=True)
            else:
                meet = int(out_indicies[0]) + 1
                df_meet_hist = meet_hist[meet_hist['meet_num'] == meet].reset_index(drop=True)
            s3.line(x=df_meet_hist['date'], y=df_meet_hist['step'], color='tomato', legend_label=str(meet), alpha=1.0, muted_alpha=0.1, name='meet_plot')
            s3.visible = True
            s3.legend.label_text_font = "calibri"
            s3.legend.label_text_font_size = "8pt"
            s3.legend.spacing = 1
            s3.legend.background_fill_alpha = 0.0
            s3.legend.click_policy = "mute"
        else:
            s3.visible = False
    s1.on_event(Tap, callback_1)

    taptool_2 = s2.select(type=TapTool)
    def callback_2(event):
        try:
            remove_glyphs(s3, 'cum_meet_plot')
            s3.legend.items = []
        except:
            pass
        out_indicies = s1_source.selected.indices
        if len(out_indicies) == 1:
            if gen == 0:
                meet = s1_source.data['x'][int(out_indicies[0])]
                df_meet_hist = meet_hist[meet_hist['meet'] == meet].reset_index(drop=True)
            else:
                meet = int(out_indicies[0]) + 1
                df_meet_hist = meet_hist[meet_hist['meet_num'] == meet].reset_index(drop=True)
            s3.line(x=df_meet_hist['date'], y=df_meet_hist['cum'], color='mediumseagreen', legend_label=str(meet), alpha=1.0, muted_alpha=0.1, name='cum_meet_plot')
            s3.visible = True
            s3.legend.label_text_font = "calibri"
            s3.legend.label_text_font_size = "8pt"
            s3.legend.spacing = 1
            s3.legend.background_fill_alpha = 0.0
            s3.legend.click_policy = "mute"
        elif len(out_indicies) == 2:
            if gen == 0:
                meet = [s1_source.data['x'][int(out_indicies[i])] for i in np.arange(len(out_indicies))]
                df1 = meet_hist[((meet_hist['meet'] == meet[0]) | (meet_hist['meet'] == meet[1]))]
                df1['sprd'] = df1.groupby('date')['cum'].diff()
                df_meet_hist = df1.dropna()
            else:
                meet = [int(out_indicies[i]) + 1 for i in np.arange(len(out_indicies))]
                df1 = meet_hist[((meet_hist['meet_num'] == meet[0]) | (meet_hist['meet_num'] == meet[1]))]
                df1['sprd'] = df1.groupby('date')['cum'].diff()
                df_meet_hist = df1.dropna()
            s3.line(x=df_meet_hist['date'], y=df_meet_hist['sprd'], color='darkgoldenrod', legend_label=str(meet[0])+' - '+str(meet[1]), alpha=1.0, muted_alpha=0.1, name='cum_meet_plot')
            s3.visible = True
            s3.legend.label_text_font = "calibri"
            s3.legend.label_text_font_size = "8pt"
            s3.legend.spacing = 1
            s3.legend.background_fill_alpha = 0.0
            s3.legend.click_policy = "mute"
        else:
            s3.visible = False
    s2.on_event(Tap, callback_2)

    return [tabs, s3]


def plot_wirp(dt1, chg=0, gen=0, dates=['']):
#    dt1 = dt
    n_crv = len(dt1[0].keys())
    crv = list(dt1[0].keys())
    n_dates = len(dt1[0][crv[0]])
    fixings = dt1[1]

    month = dict()
    step = dict()
    cum = dict()
    fwd_base = dict()
    month_chg = dict()
    step_chg = dict()
    cum_chg = dict()
    meet_hist = dict()
    today = ql.Date(datetime.datetime.now().day, datetime.datetime.now().month, datetime.datetime.now().year)

    for j in crv:
        meet_hist[j] = ccy(j,today).ois_meet_hist
        month[j] = [dt1[0][j][i]['meet_date'].tolist() for i in np.arange(n_dates)]
        step[j] =  [np.around(dt1[0][j][i]['step'],1).tolist() for i in np.arange(n_dates)]
        cum[j] =   [np.around(dt1[0][j][i]['cum'],0).tolist() for i in np.arange(n_dates)]
        fwd_base[j] = [dt1[0][j][i]['cb'].tolist() for i in np.arange(n_dates)]

    if n_crv != 1:
        itr = [max([len(step[j][0]) for j in crv]) - len(step[j][0]) for j in crv]
        for j in np.arange(len(itr)):
            for k in np.arange(n_dates):
                month[crv[j]][k] = month[crv[j]][k] + itr[j] * ['n/a']
                step[crv[j]][k] = step[crv[j]][k] + itr[j] * [0]
                cum[crv[j]][k] = cum[crv[j]][k] + itr[j] * [cum[crv[j]][k][-1]]
                fwd_base[crv[j]][k] = fwd_base[crv[j]][k] + itr[j] * [fwd_base[crv[j]][k][-1]]

    if n_dates >1:
        for j in crv:
#            j = 'SOFR_DC'
            cut_off = month[j][1].index(month[j][0][0])
            print('i am here:::: cutoff == ', cut_off)
            if cut_off != 0:
                month_chg[j] = [month[j][m][:cut_off]+month[j][0] for m in np.arange(1,n_dates)]    ##### augmented list of months
                step_chg[j] = [np.round(100*([tup[1] for item in month_chg[j][0] for tup in fixings[j] if tup[0] == item] - np.array(fwd_base[j][1][:cut_off])),1).tolist() +
                               (np.array(step[j][0][:-cut_off])-np.array(step[j][m][cut_off:])).tolist() +
                               cut_off*[0] for m in np.arange(1,n_dates)]
                cum_chg[j] = [list(accumulate(step_chg[j][m])) for m in np.arange(n_dates-1)]
            else:
                month_chg[j] = [month[j][0]]
                step_chg[j] = [(np.array(step[j][0]) - np.array(step[j][m])).tolist() for m in np.arange(1,n_dates)]
                cum_chg[j] = [(np.array(cum[j][0]) - np.array(cum[j][m])).tolist() for m in np.arange(1,n_dates)]

        itr2 = [max([len(step_chg[j][0]) for j in crv]) - len(step_chg[j][0]) for j in crv]
        for j in np.arange(len(itr2)):
            for k in np.arange(n_dates-1):
                month_chg[crv[j]][k] = month_chg[crv[j]][k] + itr2[j] * ['n/a']
                step_chg[crv[j]][k] = step_chg[crv[j]][k] + itr2[j] * [0]
                cum_chg[crv[j]][k] = cum_chg[crv[j]][k] + itr2[j] * [cum_chg[crv[j]][k][-1]]


    ### plot single curve + single chg:
    if n_crv == 1:
        _month = month[crv[0]][0]
        _step = step[crv[0]][0]
        _cum = cum[crv[0]][0]
        _fwd_base = fwd_base[crv[0]][0]
        x_range_var = _month
        s1_source = ColumnDataSource(data=dict(x=_month, y=_step, z=_cum, k=_fwd_base))

        if chg == 1:
            _month_chg = month_chg[crv[0]][0]
            _step_chg = step_chg[crv[0]][0]
            _cum_chg = cum_chg[crv[0]][0]
            x_range_var = _month_chg
            itr3 = len(_step_chg)-len(_step)
            _month = [str(i) for i in np.arange(-itr3,0)] + _month
            _step = itr3*[0] + _step
            _cum = itr3*[0] + _cum
            _fwd_base = itr3*[5.5] + _fwd_base
            print('*******_ month',_month)
            print('*******_ step', _step)
            print('*******_ step_chg', _step_chg)
            print('*******_ cum', _cum)
            print('*******_ cum_chg', _cum_chg)
            s1_source = ColumnDataSource(data=dict(x=_month, y=_step, z=_cum, k=_fwd_base, x2=_month_chg, y2=_step_chg, z2=_cum_chg))

        s1 = figure(x_range=x_range_var, width=600, height=400, tools=["pan", "tap","wheel_zoom", "box_zoom", "save", "reset", "help"], toolbar_location='left')
        s1.xgrid.visible = False
        s1.ygrid.visible = False
        s1.vbar(x='x', top='y', width=0.7, source=s1_source, color='lightsteelblue')
        zero_line = Span(location=0, dimension='width', line_color='darkseagreen', line_width=1)
        s1.renderers.extend([zero_line])
        labels_1 = LabelSet(x='x', y='y', text='y', level='glyph', text_align='center', y_offset=-16, source=s1_source,
                            text_font_size='10px', text_color='midnightblue')
        s1.add_layout((labels_1))
        s1.xaxis.major_label_orientation = math.pi / 4
        s1.y_range = Range1d( min(_step) - 5, max(_step) + 5)
        s1.min_border_bottom = 50
        s1.min_border_right = 50
        s1.title = 'Step'

        s2 = figure(width=525, height=400, tools=["pan", "crosshair","wheel_zoom", "box_zoom", "save", "reset", "help"], toolbar_location='right')
        s2.xaxis.formatter = DatetimeTickFormatter(days="%d-%b-%y", months="%d-%b-%y")
        s2.add_tools(HoverTool(tooltips=[('date', '$x{%d.%b.%y}'), ('y', '$y')], formatters={'$x': 'datetime'}))
        s2.xgrid.visible = False
        s2.ygrid.visible = False
        s2.visible = False
        zero_line = Span(location=0, dimension='width', line_color='darkseagreen', line_width=1)
        s2.renderers.extend([zero_line])
        s2.title = 'Meeting Hist'

        taptool = s1.select(type=TapTool)
        def callback(event):
            try:
                remove_glyphs(s2, 'meet_plot')
                s2.legend.items = []
            except:
                pass
            out_indicies = s1_source.selected.indices
            if len(out_indicies) > 0:
                if gen == 0:
                    meet = s1_source.data['x'][int(out_indicies[0])]
                    print(meet)
                    df_meet_hist = meet_hist[crv[0]][meet_hist[crv[0]]['meet'] == meet].reset_index(drop=True)
                else:
                    meet = int(out_indicies[0])+1
                    print(meet)
                    df_meet_hist = meet_hist[crv[0]][meet_hist[crv[0]]['meet_num'] == meet].reset_index(drop=True)
                s2.line(x=df_meet_hist['date'], y=df_meet_hist['step'], color='tomato', legend_label=str(meet), alpha=1.0,muted_alpha=0.1, name = 'meet_plot')
                s2.visible = True
            else:
                s2.visible = False

        s1.on_event(Tap, callback)

        if chg == 1:
#            s2 = figure(x_range=_month_chg, width=600, height=400, tools=["pan", "wheel_zoom", "box_zoom", "save", "reset", "help"], toolbar_location='right')
#            print('_month_chg:',_month_chg)
#            print('_step_chg:', _step_chg)
#            s2_source = ColumnDataSource(data=dict(x=_month_chg, y=_step_chg, z=_cum_chg))
#            s2.xgrid.visible = False
#            s2.ygrid.visible = False
            s1.circle(x='x2', y='y2', size=10, source=s1_source, color = 'firebrick', alpha=0.7, legend_label = dates[1].strftime('%d-%m-%Y'))  #dt1[crv[0]][1].strftime('%d-%b-%y')
#            zero_line = Span(location=0, dimension='width', line_color='darkseagreen', line_width=1)
#            s2.renderers.extend([zero_line])
            labels_1a = LabelSet(x='x2', y='y2', text='y2', level='glyph', text_align='center', y_offset=-16, source=s1_source, text_font_size='8px', text_color='blueviolet')
            s1.add_layout((labels_1a))
#            s2.xaxis.major_label_orientation = math.pi / 4
#            s2.y_range = Range1d(min(_step) - 5, max(_step) + 5)
#            s_plot.append(s2)
            s1.legend.location = 'bottom_right'
            s1.legend.label_text_font = "calibri"
            s1.legend.label_text_font_size = "6pt"
            s1.legend.spacing = 1
            s1.legend.background_fill_alpha = 0.0
            s1.legend.click_policy = "mute"
            s1.y_range = Range1d(  min(min(_step_chg),min(_step)) - 5, max(max(_step_chg),max(_step)) + 5)

        s3 = figure(x_range=_month, width=600, height=400, tools=["pan", "tap", "hover", "wheel_zoom", "box_zoom", "save", "reset", "help"], toolbar_location='right')
        s3.xgrid.visible = False
        s3.ygrid.visible = False
        s3.vbar(x='x', top='z', width=0.7, source=s1_source, color='lightsteelblue')
        zero_line = Span(location=0, dimension='width', line_color='darkseagreen', line_width=1)
        s3.renderers.extend([zero_line])
        labels_1 = LabelSet(x='x', y='z', text='z', level='glyph', text_align='center', y_offset=3, source=s1_source, text_font_size='8px', text_color='midnightblue')
        labels_2 = LabelSet(x='x', y='z', text='k', level='glyph', text_align='center', y_offset=-10, source=s1_source, text_font_size='8px', text_color='firebrick')
        s3.add_layout((labels_1))
        s3.add_layout((labels_2))
        s3.xaxis.major_label_orientation = math.pi / 4
        s3.y_range = Range1d( min(_cum) - 10, max(_cum) + 10)
        s3.title = 'Cum'

        s4 = figure(width=525, height=400, tools=["pan", "crosshair", "wheel_zoom", "box_zoom", "save", "reset", "help"], toolbar_location='right')
        s4.xaxis.formatter = DatetimeTickFormatter(days="%d-%b-%y", months="%d-%b-%y")
        s4.add_tools(HoverTool(tooltips=[('date', '$x{%d.%b.%y}'), ('y', '$y')], formatters={'$x': 'datetime'}))
        s4.xgrid.visible = False
        s4.ygrid.visible = False
        s4.visible = False
        zero_line = Span(location=0, dimension='width', line_color='darkseagreen', line_width=1)
        s4.renderers.extend([zero_line])
        s4.title = 'Meeting Hist: Cum'
        taptool2 = s3.select(type=TapTool)

        def callback2(event):
            try:
                remove_glyphs(s4, 'cum_meet_plot')
                s4.legend.items = []
            except:
                pass
            out_indicies = s1_source.selected.indices
            if len(out_indicies) > 0:
                if gen == 0:
#                    print("output :", s1_source.selected.indices)
#                    print('meet:', s1_source.data['x'][int(out_indicies[0])])
                    meet = s1_source.data['x'][int(out_indicies[0])]
                    df_meet_hist = meet_hist[crv[0]][meet_hist[crv[0]]['meet'] == meet].reset_index(drop=True)
                else:
                    meet = int(out_indicies[0])+1
                    df_meet_hist = meet_hist[crv[0]][meet_hist[crv[0]]['meet_num'] == meet].reset_index(drop=True)
                s4.line(x=df_meet_hist['date'], y=df_meet_hist['cum'], color='mediumseagreen', legend_label=str(meet), alpha=1.0, muted_alpha=0.1, name='cum_meet_plot')
                s4.visible = True
                print(s4.select(dict(type=GlyphRenderer))[0].name)
                print('legend', s4.legend[0].items[0].name)
            else:
                s4.visible = False
        s3.on_event(Tap, callback2)

        if chg == 1:
            s3.circle(x='x2', y='z2', size=10, source=s1_source, color='firebrick', alpha=0.7, legend_label=dates[1].strftime('%d-%m-%Y'))
            labels_1b = LabelSet(x='x2', y='z2', text='z2', level='glyph', text_align='center', y_offset=-16, source=s1_source, text_font_size='8px', text_color='blueviolet')
            s3.add_layout((labels_1b))
            s3.legend.location = 'bottom_left'
            s3.legend.label_text_font = "calibri"
            s3.legend.label_text_font_size = "6pt"
            s3.legend.spacing = 1
            s3.legend.background_fill_alpha = 0.0
            s3.legend.click_policy = "mute"
            s3.y_range = Range1d(min(min(_cum_chg), min(_cum)) - 10, max(max(_cum_chg), max(_cum)) + 10)

        grid = gridplot([[s1, s2],[s3, s4]])
        grid.toolbar_location = 'left'

    ### multi curves + single chg:
    else:
        print(n_crv, crv, month)
        n_grps = max([ len(month[crv[i]][0]) for i in np.arange(n_crv)])
        grps = np.arange(1,n_grps+1)
        step_data = pd.DataFrame()
        cum_data = pd.DataFrame()
        fwd_data = pd.DataFrame()
        for j in crv:
            step_data[j] =  step[j][0]
            cum_data[j] = cum[j][0]
            fwd_data[j] = fwd_base[j][0]
        step_data2 = dict([(key, list(step_data[key])) for key in crv])
        cum_data2 = dict([(key, list(cum_data[key])) for key in crv])
        fwd_data2 = dict([(key, list(fwd_data[key])) for key in crv])


        x_lab = [( str(grps[i]), j[:-3].ljust(10)+' '+month[j][0][i] ) for i in np.arange(len(grps))  for j in crv]
        counts = sum(zip(*step_data2.values()),())  # like an hstack
        color_schem = n_grps*['cornflowerblue','lightcoral','darkseagreen', 'khaki'][:n_crv]
        legend_names = n_grps*[crv[i][:-3] for i in np.arange(n_crv)]

        s1_source = ColumnDataSource(data=dict(x=(x_lab), counts=counts, colors=color_schem, legend_name=legend_names))
        s1 = figure(x_range=FactorRange(*x_lab), width=800, height=450,tools=["pan", "tap", "wheel_zoom", "box_zoom", "save", "reset", "help"], toolbar_location='right')
        s1.xgrid.visible = False
        s1.ygrid.visible = False
        s1.vbar(x='x', top='counts', width=0.7, source=s1_source, fill_color='colors', line_color='colors', legend_field='legend_name')
        labels_1 = LabelSet(x='x', y='counts', text='counts', level='glyph', text_align='center', y_offset=-14, source=s1_source, text_font_size='10px', text_color='midnightblue')
        s1.add_layout((labels_1))
        zero_line = Span(location=0, dimension='width', line_color='darkseagreen', line_width=1)
        s1.renderers.extend([zero_line])

        s1.legend.location = 'bottom_right'
        s1.legend.label_text_font = "calibri"
        s1.legend.label_text_font_size = "9pt"
        s1.legend.spacing = 1
        s1.legend.background_fill_alpha = 0.0
        s1.legend.click_policy = "mute"
        s1.xaxis.major_label_orientation = math.pi / 2
        s1.xaxis.axis_label_text_font_size = "2pt"
        s1.min_border_bottom = 50
        s1.title = 'Step'

        s3 = figure(width=525, height=475, tools=["pan", "crosshair","wheel_zoom", "box_zoom", "save", "reset", "help"], toolbar_location='right')
        s3.xaxis.formatter = DatetimeTickFormatter(days="%d-%b-%y", months="%d-%b-%y")
        s3.add_tools(HoverTool(tooltips=[('date', '$x{%d.%b.%y}'), ('y', '$y')], formatters={'$x': 'datetime'}))
        s3.xgrid.visible = False
        s3.ygrid.visible = False
        s3.visible = False
        zero_line = Span(location=0, dimension='width', line_color='darkseagreen', line_width=1)
        s3.renderers.extend([zero_line])
        s3.title = 'Meeting Hist'
        meet_color_schem = ['teal', 'tomato', 'mediumpurple', 'gold'][:n_crv]

        taptool = s1.select(type=TapTool)
        def callback(event):
            try:
                for i in np.arange(len(s3.select(dict(type=GlyphRenderer)))):
                    remove_glyphs(s3, s3.select(dict(type=GlyphRenderer))[i].name)
                s3.legend.items = []
            except:
                pass
            out_indicies = s1_source.selected.indices
            if len(out_indicies) > 0:
                if gen == 0:
                    print("output :", s1_source.selected.indices)
                    print('meet:', s1_source.data['x'][int(out_indicies[0])][0] )
                    meet = [tup[1][-6:] for tup in x_lab if tup[0] == s1_source.data['x'][int(out_indicies[0])][0]]
                    for j in np.arange(n_crv):
                        df_meet_hist = meet_hist[crv[j]][meet_hist[crv[j]]['meet'] == meet[j]].reset_index(drop=True)
                        s3.line(x=df_meet_hist['date'], y=df_meet_hist['step'], color=meet_color_schem[j], legend_label=crv[j] + ": " + meet[j], alpha=1.0, muted_alpha=0.1, name=crv[j] + ' meet_plot')
                else:
                    print('indices:', int(out_indicies[0]))
                    meet = int(s1_source.data['x'][int(out_indicies[0])][0])
                    print('meet:', meet)
                    for j in np.arange(n_crv):
                        df_meet_hist = meet_hist[crv[j]][meet_hist[crv[j]]['meet_num'] == meet].reset_index(drop=True)
                        s3.line(x=df_meet_hist['date'], y=df_meet_hist['step'], color=meet_color_schem[j], legend_label=crv[j]+": "+str(meet)+'th', alpha=1.0,muted_alpha=0.1, name = crv[j]+' meet_plot')
                s3.visible = True
                s3.legend.location = 'bottom_left'
                s3.legend.label_text_font = "calibri"
                s3.legend.label_text_font_size = "7pt"
                s3.legend.spacing = 1
                s3.legend.background_fill_alpha = 0.0
                s3.legend.click_policy = "mute"
            else:
                s3.visible = False
        s1.on_event(Tap, callback)


        cum_counts = sum(zip(*cum_data2.values()), ())  # like an hstack
        fwd_counts = sum(zip(*fwd_data2.values()), ())
        x_lab2 = [(str(grps[i]),
                   j[:-3].ljust(10) + str(fwd_base[j][0][i]).rjust(5) + month[j][0][i].rjust(17 - len(month[j][0][i])))
                  for i in np.arange(len(grps)) for j in crv]
        s2_source = ColumnDataSource(data=dict(x=(x_lab2), counts=cum_counts, colors=color_schem, legend_name=legend_names))
        s2 = figure(x_range=FactorRange(*x_lab2), width=800, height=450, tools=["pan", "tap", "wheel_zoom", "box_zoom", "save", "reset", "help"], toolbar_location='right')
        s2.xgrid.visible = False
        s2.ygrid.visible = False
        s2.vbar(x='x', top='counts', width=0.7, source=s2_source, fill_color='colors', line_color='colors',
                legend_field='legend_name')
        labels_2 = LabelSet(x='x', y='counts', text='counts', level='glyph', text_align='center', y_offset=-14,
                            x_offset=-3, source=s2_source, text_font_size='8px', text_color='midnightblue')
        s2.add_layout((labels_2))
        s2.renderers.extend([zero_line])

        s2.y_range = Range1d(min(cum_counts) - 15, max(cum_counts) + 15)
        s2.legend.location = 'bottom_left'
        s2.legend.label_text_font = "calibri"
        s2.legend.label_text_font_size = "9pt"
        s2.legend.spacing = 1
        s2.legend.background_fill_alpha = 0.0
        s2.legend.click_policy = "mute"
        s2.xaxis.major_label_orientation = math.pi / 2
        s2.xaxis.axis_label_text_font_size = "2pt"
        s2.title = 'Cum'


        s4 = figure(width=525, height=475, tools=["pan", "crosshair", "wheel_zoom", "box_zoom", "save", "reset", "help"], toolbar_location='right')
        s4.xaxis.formatter = DatetimeTickFormatter(days="%d-%b-%y", months="%d-%b-%y")
        s4.add_tools(HoverTool(tooltips=[('date', '$x{%d.%b.%y}'), ('y', '$y')], formatters={'$x': 'datetime'}))
        s4.xgrid.visible = False
        s4.ygrid.visible = False
        s4.visible = False
        zero_line = Span(location=0, dimension='width', line_color='darkseagreen', line_width=1)
        s4.renderers.extend([zero_line])
        s4.title = 'Meeting Hist: Cum'
        meet_color_schem = ['teal', 'tomato', 'mediumpurple', 'gold'][:n_crv]

        taptool2 = s2.select(type=TapTool)

        def callback2(event):
            try:
                for i in np.arange(len(s4.select(dict(type=GlyphRenderer)))):
                    remove_glyphs(s4, s4.select(dict(type=GlyphRenderer))[i].name)
                s4.legend.items = []
            except:
                pass
            out_indicies = s2_source.selected.indices
            if len(out_indicies) > 0:
                if gen == 0:
                    meet = [tup[1][-6:] for tup in x_lab if tup[0] == s1_source.data['x'][int(out_indicies[0])][0]]
                    for j in np.arange(n_crv):
                        df_meet_hist = meet_hist[crv[j]][meet_hist[crv[j]]['meet'] == meet[j]].reset_index(drop=True)
                        s4.line(x=df_meet_hist['date'], y=df_meet_hist['cum'], color=meet_color_schem[j], legend_label=crv[j]+": "+meet[j], alpha=1.0, muted_alpha=0.1, name=crv[j]+' meet_plot')
                else:
                    meet = int(s1_source.data['x'][int(out_indicies[0])][0])
                    print('meet:', meet)
                    for j in np.arange(n_crv):
                        df_meet_hist = meet_hist[crv[j]][meet_hist[crv[j]]['meet_num'] == meet].reset_index(drop=True)
                        s4.line(x=df_meet_hist['date'], y=df_meet_hist['cum'], color=meet_color_schem[j], legend_label=crv[j] + ": " + str(meet)+'th', alpha=1.0, muted_alpha=0.1, name=crv[j] + ' meet_plot')
                s4.visible = True
                s4.legend.location = 'bottom_left'
                s4.legend.label_text_font = "calibri"
                s4.legend.label_text_font_size = "7pt"
                s4.legend.spacing = 1
                s4.legend.background_fill_alpha = 0.0
                s4.legend.click_policy = "mute"
            else:
                s4.visible = False

        s2.on_event(Tap, callback2)

        grid = gridplot([[s1, s3], [s2, s4]])
        grid.toolbar_location = 'left'


        if chg == 1:
            s1.toolbar.active_tap = None
            s2.toolbar.active_tap = None
            n_grps2 = max([len(month_chg[crv[i]][0]) for i in np.arange(n_crv)])
            grps2 = np.arange(1, n_grps2 + 1)
            print('in')
            _step_chg = pd.DataFrame()
            _cum_chg = pd.DataFrame()
            for j in crv:
                _step_chg[j] = step_chg[j][0]
                _cum_chg[j] = cum_chg[j][0]
            print('*******_ month', month_chg)
            print('*******_ step_chg', _step_chg)
            print('*******_ cum_chg', _cum_chg)

            step_chg_data2 = dict([(key, list(_step_chg[key])) for key in crv])
            cum_chg_data2 = dict([(key, list(_cum_chg[key])) for key in crv])

            x_lab = [(str(grps2[i]), j[:-3].ljust(10) + ' ' + month_chg[j][0][i]) for i in np.arange(len(grps2)) for j in crv]
            counts = sum(zip(*step_chg_data2.values()), ())  # like an hstack
            cum_counts = sum(zip(*cum_chg_data2.values()), ())
#            color_schem = n_grps2 * ['cornflowerblue','lightcoral','darkseagreen', 'khaki'][:n_crv]
#            legend_names = n_grps2 * [crv[i][:-3] for i in np.arange(n_crv)]
            color_schem2 = ['mediumblue', 'tomato', 'darkseagreen', 'khaki']

#            s5_source = ColumnDataSource(data=dict(x=(x_lab), counts=counts, colors=color_schem, legend_name=legend_names))
            s5 = figure(x_range=FactorRange(*x_lab), width=800, height=450, tools=["pan", "tap","wheel_zoom", "box_zoom", "save", "reset", "help"], toolbar_location='right')
            s5.add_tools(HoverTool(tooltips=[('date', '@x'), ('y', '$y')]))
            s5.xgrid.visible = False
            s5.ygrid.visible = False
            for j in np.arange(n_crv):
                s5.scatter(x=x_lab[j::n_crv], y=counts[j::n_crv], marker='circle_dot', size=8, color=color_schem2[j] ,legend_label=crv[j][:-3], alpha=1.0, muted_alpha=0.1)
#            s5.vbar(x='x', top='counts', width=0.7, source=s5_source, fill_color='colors', line_color='colors', legend_field='legend_name')
#            s5.scatter(x=x_lab[::2], y=counts[::2], marker='circle_dot', size = 8, color='lightskyblue', legend_label='sofr',  alpha = 1.0, muted_alpha=0.1)
#            s5.scatter(x=x_lab[1::2], y=counts[1::2], marker='circle_dot', size = 8, color='tomato', legend_label='sonia',  alpha = 1.0, muted_alpha=0.1)
#            s5.circle(x='x', y='counts', size=9, source=s5_source)
#            labels_3 = LabelSet(x='x', y='counts', text='counts', level='glyph', text_align='center', y_offset=-14, source=s3_source, text_font_size='10px', text_color='midnightblue')
#            s5.add_layout((labels_3))
            zero_line = Span(location=0, dimension='width', line_color='darkseagreen', line_width=1)
            s5.renderers.extend([zero_line])
            s5.legend.location = 'bottom_right'
            s5.legend.label_text_font = "calibri"
            s5.legend.label_text_font_size = "9pt"
            s5.legend.spacing = 1
            s5.legend.background_fill_alpha = 0.0
            s5.legend.click_policy = "mute"
            s5.xaxis.major_label_orientation = math.pi / 2
            s5.xaxis.axis_label_text_font_size = "2pt"
            s5.min_border_bottom = 50
            s5.title = 'Step Chg'

            s6 = figure(x_range=FactorRange(*x_lab), width=800, height=450, tools=["pan", "tap", "wheel_zoom", "box_zoom", "save", "reset", "help"], toolbar_location='right')
            s6.add_tools(HoverTool(tooltips=[('date', '@x'), ('y', '$y')]))
            s6.xgrid.visible = False
            s6.ygrid.visible = False
            for j in np.arange(n_crv):
                s6.scatter(x=x_lab[j::n_crv], y=cum_counts[j::n_crv], marker='circle_dot', size=8, color=color_schem2[j], legend_label=crv[j][:-3]+": "+dates[1].strftime('%d-%m-%Y'), alpha=1.0, muted_alpha=0.1)
            zero_line = Span(location=0, dimension='width', line_color='darkseagreen', line_width=1)
            s6.renderers.extend([zero_line])
            s6.legend.location = 'bottom_left'
            s6.legend.label_text_font = "calibri"
            s6.legend.label_text_font_size = "7.5pt"
            s6.legend.spacing = 1
            s6.legend.background_fill_alpha = 0.0
            s6.legend.click_policy = "mute"
            s6.xaxis.major_label_orientation = math.pi / 2
            s6.xaxis.axis_label_text_font_size = "2pt"
            s6.min_border_bottom = 50
            s6.title = 'Cum Chg'

            #            taptool = s5.select(type=TapTool)
#            def callback(event):
#                out_indicies = s5_source.selected.indices
#                print("output :", s5_source.selected.indices)
#                x_filter = s5_source.data['x'][int(out_indicies[0]):int(out_indicies[0]+2)]
#                if len(out_indicies) > 0:
#                    s5.quad(top=[5], bottom=[-25], left=[x_filter[0]], right=[x_filter[1]], color="khaki", alpha =0.25)
                    #s5.patch( x= [x_filter[0],x_filter[0],x_filter[1],x_filter[1]], y=[-25, 25, -25, 25], color = 'khaki')
#            s5.on_event(Tap, callback)


            grid = gridplot([[s1, s5], [s2, s6]])
            grid.toolbar_location = 'left'

    return grid


def plot_opt_vol_surf_bokeh(vol_surf):
    print(vol_surf, len(vol_surf))
    live_px = vol_surf[0].spot_px

    df_call = [vol_surf[i].tab[vol_surf[i].tab['opt_type'] == 1] for i in np.arange(len(vol_surf))]
    df_put = [vol_surf[i].tab[vol_surf[i].tab['opt_type'] == -1] for i in np.arange(len(vol_surf))]

    s1 = figure(width=700, height=300, tools=["pan", "crosshair", "wheel_zoom", "box_zoom", "save", "reset", "help"], toolbar_location='right')
    s1.add_tools(HoverTool(tooltips=[('x', '$x'), ('y', '$y')]))
    s1.xgrid.visible = False
    s1.ygrid.visible = False
    for i in np.arange(len(df_call)):
        s1.line(x=df_call[i]['delta'], y=df_call[i]['iv'], width=0.7, color='royalblue', legend_label=ql_to_datetime(vol_surf[i].ref_date).strftime('%d-%m-%Y'))
        s1.scatter(x=df_call[i]['delta'], y=df_call[i]['iv'], width=0.7, color='navy', size=10, marker="dot")
        live_line = Span(location=50, dimension='height', line_color='goldenrod', line_width=1)
        s1.add_layout(live_line)
    s1.legend.location = 'bottom_right'
    s1.legend.label_text_font = "calibri"
    s1.legend.label_text_font_size = "9pt"
    s1.legend.spacing = 1
    s1.legend.click_policy = "mute"
    s1.legend.background_fill_alpha = 0.0
    s1.yaxis.axis_label = 'imp. vol.'
    s1.xaxis.axis_label = 'delta'

    s2 = figure(width=700, height=300, tools=["pan", "crosshair", "wheel_zoom", "box_zoom", "save", "reset", "help"],toolbar_location='right')
    s2.add_tools(HoverTool(tooltips=[('x', '$x'), ('y', '$y')]))
    s2.xgrid.visible = False
    s2.ygrid.visible = False
    for i in np.arange(len(df_call)):
        s2.line(x=df_call[i]['strikes'], y=df_call[i]['iv'], width=0.7, color='royalblue', legend_label=ql_to_datetime(vol_surf[i].ref_date).strftime('%d-%m-%Y'))
        s2.scatter(x=df_call[i]['strikes'], y=df_call[i]['iv'], width=0.7, color='navy', size=10, marker="dot")
        live_line = Span(location=live_px, dimension='height', line_color='goldenrod', line_width=1)
        s2.add_layout(live_line)
    s2.legend.location = 'bottom_right'
    s2.legend.label_text_font = "calibri"
    s2.legend.label_text_font_size = "9pt"
    s2.legend.spacing = 1
    s2.legend.click_policy = "mute"
    s2.legend.background_fill_alpha = 0.0
    s2.yaxis.axis_label = 'imp. vol.'
    s2.xaxis.axis_label = 'K'

    s3 = figure(width=700, height=300, tools=["pan", "crosshair", "wheel_zoom", "box_zoom", "save", "reset", "help"],
                toolbar_location='right')
    s3.add_tools(HoverTool(tooltips=[('x', '$x'), ('y', '$y')]))
    s3.xgrid.visible = False
    s3.ygrid.visible = False
    for i in np.arange(len(df_put)):
        s3.line(x=df_put[i]['delta'], y=df_put[i]['iv'], width=0.7, color='palevioletred', legend_label=ql_to_datetime(vol_surf[i].ref_date).strftime('%d-%m-%Y'))
        s3.scatter(x=df_put[i]['delta'], y=df_put[i]['iv'], width=0.7, color='red', size=10, marker="dot")
        live_line = Span(location=-50, dimension='height', line_color='goldenrod', line_width=1)
        s3.add_layout(live_line)
    s3.legend.location = 'bottom_right'
    s3.legend.label_text_font = "calibri"
    s3.legend.label_text_font_size = "9pt"
    s3.legend.spacing = 1
    s3.legend.click_policy = "mute"
    s3.legend.background_fill_alpha = 0.0
    s3.yaxis.axis_label = 'imp. vol.'
    s3.xaxis.axis_label = 'delta'

    s4 = figure(width=700, height=300, tools=["pan", "crosshair", "wheel_zoom", "box_zoom", "save", "reset", "help"],
                toolbar_location='right')
    s4.add_tools(HoverTool(tooltips=[('x', '$x'), ('y', '$y')]))
    s4.xgrid.visible = False
    s4.ygrid.visible = False
    for i in np.arange(len(df_put)):
        s4.line(x=df_put[i]['strikes'], y=df_put[i]['iv'], width=0.7, color='palevioletred', legend_label=ql_to_datetime(vol_surf[i].ref_date).strftime('%d-%m-%Y'))
        s4.scatter(x=df_put[i]['strikes'], y=df_put[i]['iv'], width=0.7, color='red', size=10, marker="dot")
        live_line = Span(location=live_px, dimension='height', line_color='goldenrod', line_width=1)
        s4.add_layout(live_line)
    s4.legend.location = 'bottom_right'
    s4.legend.label_text_font = "calibri"
    s4.legend.label_text_font_size = "9pt"
    s4.legend.spacing = 1
    s4.legend.click_policy = "mute"
    s4.legend.background_fill_alpha = 0.0
    s4.yaxis.axis_label = 'imp. vol.'
    s4.xaxis.axis_label = 'K'

    tab1 = TabPanel(child=s2, title="call strikes")
    tab2 = TabPanel(child=s1, title="call delta")
    tab3 = TabPanel(child=s3, title="put delta")
    tab4 = TabPanel(child=s4, title="put strikes")

    tabs = Tabs(tabs=[tab1, tab2, tab3, tab4])

    return [tabs]


def plt_opt_strat_bokeh(st, add_delta = [0] , payoff_increm_calc = 100):
    #### **** add_delta not implemented for strategy payoff - but implemented for expiry payoff and strategy delta   #####
#    v2 = build_vol_surf(['RXJ4P 133'], chain_len=[12,12], b=0)
#    st = bond_fut_opt_strat(['RXJ4'], ['C', 'C'], [135, 136.5], [1, -1], s_range=[-1, 1], increm=0.5, built_surf=v2)

    spot_idx = st.strat.loc[st.strat['ATM_K'] == 0].index[0]

    x_spot = st.strat['fut_px'][spot_idx]
    #### payoff at expiry
    x1 = np.linspace(min(st.strat['fut_px']), max(st.strat['fut_px']), num=payoff_increm_calc)
    if len(add_delta) > 1:
        d_payoff1 = fut_payoff(x1, [st.fut], add_delta)
        y1 = opt_payoff(x1, st.opt_dets, st.strat_px) + d_payoff1
        y1_fmt = [convert_to_64(px_dec_to_opt_frac(y1[i])) for i in np.arange(len(y1))]
        st.strat['strat_delta'] = st.strat['strat_delta'] + 100 * np.array(add_delta[0])  #### neds testing
    else:
        y1 = opt_payoff(x1, st.opt_dets, st.strat_px)
        y1_fmt = [convert_to_64(px_dec_to_opt_frac(y1[i])) for i in np.arange(len(y1))]

    if st.type == 'USD':
        px_label = px_dec_to_opt_frac(st.strat_px)
        y3 = [convert_to_64(st.strat['strat_px_fmt'][i]) for i in np.arange(len(st.strat))]
        _tooltips = [('fut', '$x{0.00}'), ('px', '@y2{0.00}'), ('px_fmt', '@y2_fmt'), ('y_dist', '@k_dist{0.0}')]
    elif st.type == 'stir':
        px_label = str(np.round(100*st.strat_px,2))
        y3 =  100*st.strat['strat_px']
        y1 = y1*100
        _tooltips = [('fut', '$x{0.000}'), ('px', '@y2_fmt{0.0}'), ('y_dist', '@k_dist{0.0}')]
    else:
        px_label = str(np.round(st.strat_px, 3))
        y3 =  st.strat['strat_px']
        _tooltips = [('fut', '$x{0.00}'), ('px', '@y2{0.00}'), ('y_dist', '@k_dist{0.0}')]



    p1 = figure(width=700, height=350, tools=["pan", "crosshair", "wheel_zoom", "box_zoom", "save", "reset", "help"],toolbar_location='right')
    main_source = ColumnDataSource(data={'x2': st.strat['fut_px'],
                                         'y2': y3,
                                         'y3': y3,
                                         'k_dist': st.strat['ATM_K'],
                                         'y2_fmt': st.strat['strat_px_fmt'] })
    p1.add_tools(HoverTool(tooltips=_tooltips))
    p1.xgrid.visible = False
    p1.ygrid.visible = False
    if st.type == 'USD':
        p1.line(x=x1, y=y1_fmt, width=0.7, color='black', alpha=1.0, muted_alpha=0.1, legend_label="@expiry")
        p1.line(x='x2', y='y3', width=0.7, color='navy', alpha=1.0, muted_alpha=0.1, legend_label="opt_px: "+px_label, source=main_source, name = 'payoff')
        p1.yaxis.axis_label = 'strat_px (64th)'
    else:
        p1.line(x=x1, y=y1, width=0.7, color='black', alpha=1.0, muted_alpha=0.1, legend_label="@expiry")
        p1.line(x='x2', y='y2', width=0.7, color='navy', alpha=1.0, muted_alpha=0.1, legend_label="opt_px: "+px_label, source=main_source)
        p1.yaxis.axis_label = 'strat_px'
    live_line = Span(location=x_spot, dimension='height', line_color='goldenrod', line_width=1)
    zero_line = Span(location=0, dimension='width', line_color='darkseagreen', line_width=1)
    p1.add_layout(live_line)
    p1.add_layout(zero_line)
    p1_source = ColumnDataSource(data=dict(x=np.round(st.strat['fut_px'][::int(len(st.strat) / 6)], 1).tolist(),z=np.round(st.strat['ATM_K'][::int(len(st.strat) / 6)], 1).tolist()))
    labels_yld = LabelSet(x='x', y=5, y_units='screen', text='z', source=p1_source, text_font='calibri', text_color='firebrick', text_font_size='9px', text_align='center', x_offset=0)
    p1.add_layout(labels_yld)
    p1.xaxis.ticker = np.round(st.strat['fut_px'][::int(len(st.strat) / 6)], 2)
    p1.legend.location = 'top_left'
    p1.legend.label_text_font = "calibri"
    p1.legend.label_text_font_size = "9pt"
    p1.legend.spacing = 1
    p1.legend.click_policy = "mute"
    p1.legend.background_fill_alpha = 0.0

    p2_source = ColumnDataSource(data=dict(x=np.round(st.strat['fut_px'][::int(len(st.strat) / 6)], 1).tolist(), z=np.round(0.01 * st.strat['strat_delta'][::int(len(st.strat) / 6)],2).tolist()))
    p2 = figure(width=700, height=225, tools=["pan", "crosshair", "wheel_zoom", "box_zoom", "save", "reset", "help"], toolbar_location='right')
    p2.add_tools(HoverTool(tooltips=[('x', '$x{0.00}'), ('y', '$y{0.00}')]))
    p2.xgrid.visible = False
    p2.ygrid.visible = False
    p2.line(x=st.strat['fut_px'], y=st.strat['strat_delta'] / 100, width=0.7, color='green', alpha=1.0, muted_alpha=0.1, legend_label="delta")
    live_line = Span(location=x_spot, dimension='height', line_color='goldenrod', line_width=1)
    labels_delta = LabelSet(x='x', y=5, y_units='screen', text='z', source=p2_source, text_font='calibri', text_color='firebrick', text_font_size='9px', text_align='right', x_offset=0)
    p2.xaxis.ticker = np.round(st.strat['fut_px'][::int(len(st.strat) / 6)], 2)
    p2.add_layout(live_line)
    p2.add_layout(labels_delta)
    p2.legend.location = 'top_left'
    p2.legend.label_text_font = "calibri"
    p2.legend.label_text_font_size = "9pt"
    p2.legend.spacing = 1
    p2.legend.click_policy = "mute"
    p2.legend.background_fill_alpha = 0.0
    p2.yaxis.axis_label = 'strat_delta'

    s_plot = [p1,p2]
#    grid = gridplot([[p1], [p2]])   <----- issue !!
#    grid.toolbar_location = 'right'

    return s_plot


def plot_tool_bbg_listed(v2, fut_ticker, opt_w):
    ticker_list = [fut_ticker] + v2['ticker'].tolist()
    print(ticker_list)
    st_date = '20230801'

    df1 = con.bdh(ticker_list, 'PX_LAST', st_date, datetime.datetime.now().strftime('%Y%m%d'))
    df1.dropna(inplace=True)
    px_series = np.round(100 * np.sum([np.array(df1.iloc[:, i + 1]) * opt_w[i] for i in np.arange(len(opt_w))], axis=0),1)

    h1 = figure(width=700, height=350, tools=["pan", "crosshair", "wheel_zoom", "box_zoom", "save", "reset", "help"], toolbar_location='right')
    h1.xaxis.formatter = DatetimeTickFormatter(days="%d-%b-%y", months="%d-%b-%y")
    h1.add_tools(HoverTool(tooltips=[('date', '$x{%d.%b.%y}'), ('y', '$y{0.0}')], formatters={'$x': 'datetime'}))
    h1.xgrid.visible = False
    h1.ygrid.visible = False
    h1.line(x=df1.index, y=px_series, width=0.7, color='navy', legend_label="strat", alpha=1.0)
    h1.legend.location = 'top_right'
    h1.legend.label_text_font = "calibri"
    h1.legend.label_text_font_size = "9pt"
    h1.legend.spacing = 1
    h1.legend.click_policy = "mute"
    h1.legend.background_fill_alpha = 0.0
    h1.yaxis.axis_label = 'px'
    h1.xaxis.axis_label = 'Date'

    h1.y_range = Range1d(min(px_series) - 2, max(px_series) + 2)
    # SECOND AXIS
    h1.extra_y_ranges = {"y2_range": Range1d(start=min(df1.iloc[:, 0]) - 0.05, end=max(df1.iloc[:, 0]) + 0.05)}
    h1.add_layout(LinearAxis(y_range_name="y2_range"), "right")
    h1.line(x=df1.index, y=df1.iloc[:, 0], width=0.7, color='green', legend_label="fut", alpha=0.2, y_range_name='y2_range')

    return h1


def plot_inflation_fixings(a, crv, gen=0):
#    a = 'UKRPI'
#    crv = [ukrpi1, ukrpi2]
    today = ql.Date(datetime.datetime.now().day, datetime.datetime.now().month, datetime.datetime.now().year)
    for inf_crv in crv:
        inf_crv.curve[1]['yoy'] = inf_crv.curve[1]['index'].pct_change(periods=12) * 100


    fix_hist = ccy_infl(a, today).fix_hist
    fix_df = []
    for i in np.arange(len(crv)):
        fix_df.append(crv[i].curve[1][crv[i].curve[1]['months'] > crv[i].base_month][:12]['months'].tolist())

    fix_months = np.unique(fix_df)
    fix_months = [ql_to_datetime(fix_months[i]).strftime('%b-%y') for i in np.arange(len(fix_months))]
    fixings = np.round(crv[0].curve[1][crv[0].curve[1]['months'].isin(np.unique(fix_df))]['yoy'], 2).tolist()
    fixings_chg = np.round(100 * (crv[0].curve[1][crv[0].curve[1]['months'].isin(np.unique(fix_df))]['yoy'] - crv[1].curve[1][crv[1].curve[1]['months'].isin(np.unique(fix_df))]['yoy']),1).tolist()

    ##### getting barcap forecasts
    crv[0].curve[2]['yoy'] = crv[0].curve[2]['index'].pct_change(periods=12) * 100
    barcap_f = np.round(crv[0].curve[2][crv[0].curve[2]['months'].isin(np.unique(fix_df))]['yoy'], 2).tolist()

#    s_plot = []
    s1_source = ColumnDataSource(data=dict(x=fix_months, y=fixings, z=fixings_chg, b=barcap_f ))

    s1 = figure(x_range=fix_months, width=550, height=300, tools=["pan", "tap", "wheel_zoom", "box_zoom", "save", "reset", "help"], toolbar_location='right')
    s1.xgrid.visible = False
    s1.ygrid.visible = False
    s1.vbar(x='x', top='y', width=0.7, source=s1_source, color='lightsteelblue')
    s1.y_range = Range1d( min(1, min(fixings)-1.5) , max(fixings) + 0.2)
    labels_1 = LabelSet(x='x', y='y', text='y', level='glyph', text_align='center', y_offset=-10, source=s1_source, text_font_size='10px', text_color='midnightblue')
    labels_2 = LabelSet(x='x', y=min(1, min(fixings)-1.5), text='b', level='glyph', text_align='center', y_offset=8, source=s1_source, text_font_size='10px', text_color='darkgreen')
    s1.add_layout((labels_1))
    s1.add_layout((labels_2))
    s1.xaxis.major_label_orientation = math.pi / 2
    s1.yaxis.axis_label = 'Fixings (vs Barcap)'
#    s_plot.append(s1)

    s2 = figure(x_range=fix_months, width=550, height=125, tools=["pan", "tap", "wheel_zoom", "box_zoom", "save", "reset", "help"], toolbar_location='right')
    s2.xgrid.visible = False
    s2.ygrid.visible = False
    s2.circle(x='x', y='z', size=8, source=s1_source, color='firebrick', alpha=0.8)
    zero_line = Span(location=0, dimension='width', line_color='darkseagreen', line_width=1)
    s2.renderers.extend([zero_line])
    labels_1a = LabelSet(x='x', y='z', text='z', level='glyph', text_align='center', y_offset=-14, source=s1_source, text_font_size='8px', text_color='firebrick')
    s2.add_layout((labels_1a))
    s2.y_range = Range1d( (min(fixings_chg)*(  1-(0.2*np.sign(min(fixings_chg)))))-5 , 5+max(fixings_chg)*(  1+(0.2*np.sign(max(fixings_chg)))))
#    print('min:', min(fixings_chg), 'max:', max(fixings_chg))
#    print('y2_min:', (min(fixings_chg)*(  1-(0.2*np.sign(min(fixings_chg)))))-2  )
#    print('y2_max:', 2+max(fixings_chg)*(  1+(0.2*np.sign(max(fixings_chg))))  )
    s2.yaxis.axis_label = 'Chg (bps)'
    s2.yaxis.major_label_text_font_size = '7pt'
    s2.xaxis.visible = False
#    s_plot.append(s2)

    tab1 = TabPanel(child=layout([[s1], [s2]]), title="Fixings")
#    tab2 = TabPanel(child=s2, title="cum")
    tabs = Tabs(tabs=[tab1])

    s3 = figure(width=570, height=450, tools=["pan", "crosshair", "wheel_zoom", "box_zoom", "save", "reset", "help"], toolbar_location='right')
    s3.xaxis.formatter = DatetimeTickFormatter(days="%d-%b-%y", months="%d-%b-%y")
    s3.add_tools(HoverTool(tooltips=[('date', '$x{%d.%b.%y}'), ('y', '$y')], formatters={'$x': 'datetime'}))
    s3.xgrid.visible = False
    s3.ygrid.visible = False
    s3.visible = False
    zero_line = Span(location=0, dimension='width', line_color='darkseagreen', line_width=1)
    s3.renderers.extend([zero_line])
    s3.title = 'Fixing Hist'
    s3.min_border_top = 30
    s3.min_border_left = 50

    taptool_1 = s1.select(type=TapTool)
    def callback_1(event):
        try:
            remove_glyphs(s3, 'fix_plot')
            s3.legend.items = []
        except:
            pass
        out_indicies = s1_source.selected.indices
        print('out_indicies: ',out_indicies)
        if len(out_indicies) == 1:
            if gen == 0:
                fix = s1_source.data['x'][int(out_indicies[0])]
                print('fix: ', fix)
                df_fix_hist = fix_hist[fix_hist['fix_month2'] == fix].reset_index(drop=True)
                df_fix_hist = df_fix_hist.sort_values('date')
                print('df_fix: ', df_fix_hist)
            else:
                fix = int(out_indicies[0]) + 1
                df_fix_hist = fix_hist[fix_hist['gen_month'] == fix].reset_index(drop=True)
                df_fix_hist = df_fix_hist.sort_values('date')
            s3.line(x=df_fix_hist['date'], y=df_fix_hist['fixing'], color='tomato', legend_label=str(fix), alpha=1.0, muted_alpha=0.1, name='fix_plot')
            s3.visible = True
            s3.legend.label_text_font = "calibri"
            s3.legend.label_text_font_size = "8pt"
            s3.legend.spacing = 1
            s3.legend.background_fill_alpha = 0.0
            s3.legend.click_policy = "mute"
        elif len(out_indicies) == 2:
            print('out_indicies: ', out_indicies)
            if gen == 0:
                fix = [s1_source.data['x'][int(out_indicies[i])] for i in np.arange(len(out_indicies))]
                print('fix: ', fix)
                df1 = fix_hist[((fix_hist['fix_month2'] == fix[0]) | (fix_hist['fix_month2'] == fix[1]))]
                df1['sprd'] = 100*df1.groupby('date')['fixing'].diff()
                print('df1: ', df1)
                df_fix_hist = df1.sort_values('date').dropna()
            else:
                fix = [int(out_indicies[i]) + 1 for i in np.arange(len(out_indicies))]
                df1 = fix_hist[((fix_hist['gen_month'] == fix[0]) | (fix_hist['gen_month'] == fix[1]))]
                df1['sprd'] = 100*df1.groupby('date')['fixing'].diff()
                df_fix_hist = df1.sort_values('date').dropna()
            s3.line(x=df_fix_hist['date'], y=df_fix_hist['sprd'], color='darkgoldenrod', legend_label=str(fix[0]) + ' - ' + str(fix[1]), alpha=1.0, muted_alpha=0.1, name='fix_plot')
            s3.visible = True
            s3.legend.label_text_font = "calibri"
            s3.legend.label_text_font_size = "8pt"
            s3.legend.spacing = 1
            s3.legend.background_fill_alpha = 0.0
            s3.legend.click_policy = "mute"
        else:
            s3.visible = False
    s1.on_event(Tap, callback_1)

    return [tabs,s3]


def swap_heatmap(crv, b=0, offset = [-1], ois_flag = 0, z_offset = 0, z_roll = ['3M','6M']):

    h1 = curve_hmap(crv, b=b, offset=offset, ois_flag=ois_flag)

    df_rates = h1.rates[:-1]
    for i in list(df_rates.index):
        if any(x == i for x in ['11Y', '13Y', '40Y']):
            df_rates = df_rates.drop([i])

    df_rates_chg = h1.rates_chg[h1.offset[z_offset]][:-1]
    for i in list(df_rates_chg.index):
        if any(x == i for x in ['11Y', '13Y', '40Y']):
            df_rates_chg = df_rates_chg.drop([i])

    m_coolwarm_rgb = (255 * cm.coolwarm(range(256))).astype('int')
    coolwarm_palette = [RGB(*tuple(rgb)).to_hex() for rgb in m_coolwarm_rgb]

    df1 = pd.DataFrame(df_rates.stack(), columns=['rate']).reset_index()
    df2 = pd.DataFrame(df_rates_chg.stack(), columns=['chg']).reset_index()
    df1.columns = ['Tenor', 'Curve', 'Rate']
    df1['Chg'] = df2['chg']
    n_crv = df_rates.shape[1]
    s1_source = ColumnDataSource(df1)

    df3 = pd.DataFrame(h1.curves.stack(), columns=['fwds']).reset_index()
    df4 = pd.DataFrame(h1.chg[h1.offset[z_offset]].stack(), columns=['chg']).reset_index()
    df3.columns = ['Fwds', 'Curve', 'Rate']
    df3['Chg'] = df4['chg']
    s2_source = ColumnDataSource(df3)

    f1 = df1['Chg'].tolist() + df3['Chg'].tolist()
    mapper_rates = LinearColorMapper(palette=coolwarm_palette, low=1, high=6.5)
    mapper_chg = LinearColorMapper(palette=coolwarm_palette, low=min(f1), high=max(f1))

    s1 = figure(title="Rate", x_range=df_rates.columns.tolist(), y_range=df_rates.index.tolist(), x_axis_location="below", width=100 * n_crv, height=400, toolbar_location=None)
    s1.grid.grid_line_color = None
    s1.axis.axis_line_color = None
    s1.axis.major_tick_line_color = None
    s1.axis.major_label_text_font_size = "12px"
    s1.yaxis.axis_label = 'Tenor'

    s1.rect(x="Curve", y="Tenor", width=1, height=1, source=s1_source, fill_color={'field': 'Rate', 'transform': mapper_rates}, line_color=None)
    # s1.multi_line(xs=[[0,1], [1,2], [2,3], [3,4]], ys=[[0,0], [0,0], [0,0], [0,0]], color=['green', 'yellow', 'red', 'blue'], line_width=4)
    labels = LabelSet(x='Curve', y='Tenor', text='Rate', source=s1_source, level='glyph', text_align='center', y_offset=-7, text_color='black', text_font_size='9pt')
    s1.add_layout(labels)

    s2 = figure(title='Chg: ' + str(ql_to_datetime(h1.dates[z_offset + 1]).strftime('%d-%b-%y')), x_range=df_rates.columns.tolist(), y_range=df_rates.index.tolist(), x_axis_location="below", y_axis_location="right",
                width=100 * n_crv - 75, height=400, toolbar_location=None)
    s2.grid.grid_line_color = None
    s2.axis.axis_line_color = None
    s2.axis.major_tick_line_color = None
    s2.axis.major_label_text_font_size = "12px"
    s2.yaxis.visible = False

    s2.rect(x="Curve", y="Tenor", width=1, height=1, source=s1_source, fill_color={'field': 'Chg', 'transform': mapper_chg}, line_color=None)
    labels_chg = LabelSet(x='Curve', y='Tenor', text='Chg', source=s1_source, level='glyph', text_align='center', y_offset=-7, text_color='black', text_font_size='9pt')
    s2.add_layout(labels_chg)

    s3 = figure(title="Fwds", x_range=df_rates.columns.tolist(), y_range=df3.Fwds.unique().tolist(), x_axis_location="below", width=100 * n_crv - 50, height=400, toolbar_location=None)
    s3.grid.grid_line_color = None
    s3.axis.axis_line_color = None
    s3.axis.major_tick_line_color = None
    s3.axis.major_label_text_font_size = "12px"
    # s3.yaxis.axis_label = 'Fwd'

    s3.rect(x="Curve", y="Fwds", width=1, height=1, source=s2_source, fill_color={'field': 'Rate', 'transform': mapper_rates}, line_color=None)
    labels2 = LabelSet(x='Curve', y='Fwds', text='Rate', source=s2_source, level='glyph', text_align='center', y_offset=-7, text_color='black', text_font_size='9pt')
    s3.add_layout(labels2)

    s4 = figure(title="Chg", x_range=df_rates.columns.tolist(), y_range=df3.Fwds.unique().tolist(), x_axis_location="below", y_axis_location="right", width=100 * n_crv - 75, height=400, toolbar_location=None)
    s4.grid.grid_line_color = None
    s4.axis.axis_line_color = None
    s4.axis.major_tick_line_color = None
    s4.axis.major_label_text_font_size = "12px"
    s4.yaxis.visible = False

    s4.rect(x="Curve", y="Fwds", width=1, height=1, source=s2_source, fill_color={'field': 'Chg', 'transform': mapper_chg}, line_color=None)
    labels_chg2 = LabelSet(x='Curve', y='Fwds', text='Chg', source=s2_source, level='glyph', text_align='center', y_offset=-7, text_color='black', text_font_size='9pt')
    s4.add_layout(labels_chg2)

    df5 = pd.DataFrame(h1.steep[::-1].stack(), columns=['spread']).reset_index()
    df6 = pd.DataFrame(pd.DataFrame(h1.steep_chg[h1.offset[0]])[::-1].stack(), columns=['chg']).reset_index()
    df5.columns = ['Steep', 'Curve', 'Spread']
    df5['Chg'] = np.round(df6['chg'], 1)
    s3_source = ColumnDataSource(df5)

    df7 = pd.DataFrame(h1.roll[z_roll[0]][::-1].stack(), columns=['roll_1']).reset_index()
    df8 = pd.DataFrame(h1.roll[z_roll[1]][::-1].stack(), columns=['roll_2']).reset_index()
    df7.columns = ['Steep', 'Curve', 'Roll_1']
    df7['Roll_1'] = np.round(df7['Roll_1'], 1)
    df7['Roll_2'] = np.round(df8['roll_2'], 1)
    s4_source = ColumnDataSource(df7)

    f2 = df5['Chg'].tolist()
    f3 = df7['Roll_1'].tolist() + df7['Roll_2'].tolist()
    mapper_curve = LinearColorMapper(palette=coolwarm_palette, low=-50, high=50)
    mapper_curve_chg = LinearColorMapper(palette=coolwarm_palette[::-1], low=min(f2), high=max(f2))
    mapper_roll = LinearColorMapper(palette=coolwarm_palette[::-1], low=min(f3), high=max(f3))

    s5 = figure(title="Curve", x_range=df_rates.columns.tolist(), y_range=df5.Steep.unique().tolist(), x_axis_location="below", width=100 * n_crv, height=400, toolbar_location=None)
    s5.grid.grid_line_color = None
    s5.axis.axis_line_color = None
    s5.axis.major_tick_line_color = None
    s5.axis.major_label_text_font_size = "12px"
    s5.yaxis.axis_label = 'Curve'

    s5.rect(x="Curve", y="Steep", width=1, height=1, source=s3_source, fill_color={'field': 'Spread', 'transform': mapper_curve}, line_color=None)
    labels3 = LabelSet(x='Curve', y='Steep', text='Spread', source=s3_source, level='glyph', text_align='center', y_offset=-7, text_color='black', text_font_size='9pt')
    s5.add_layout(labels3)

    s6 = figure(title="Chg", x_range=df_rates.columns.tolist(), y_range=df5.Steep.unique().tolist(), x_axis_location="below", y_axis_location="right", width=100 * n_crv - 75, height=400, toolbar_location=None)
    s6.grid.grid_line_color = None
    s6.axis.axis_line_color = None
    s6.axis.major_tick_line_color = None
    s6.axis.major_label_text_font_size = "12px"
    s6.yaxis.visible = False

    s6.rect(x="Curve", y="Steep", width=1, height=1, source=s3_source, fill_color={'field': 'Chg', 'transform': mapper_curve_chg}, line_color=None)
    labels_chg3 = LabelSet(x='Curve', y='Steep', text='Chg', source=s3_source, level='glyph', text_align='center', y_offset=-7, text_color='black', text_font_size='9pt')
    s6.add_layout(labels_chg3)

    s7 = figure(title='Roll: ' + z_roll[0], x_range=df_rates.columns.tolist(), y_range=df5.Steep.unique().tolist(), x_axis_location="below", width=100 * n_crv - 50, height=400, toolbar_location=None)
    s7.grid.grid_line_color = None
    s7.axis.axis_line_color = None
    s7.axis.major_tick_line_color = None
    s7.axis.major_label_text_font_size = "12px"
    # s7.yaxis.visible = False

    s7.rect(x="Curve", y="Steep", width=1, height=1, source=s4_source, fill_color={'field': 'Roll_1', 'transform': mapper_roll}, line_color=None)
    labels_roll1 = LabelSet(x='Curve', y='Steep', text='Roll_1', source=s4_source, level='glyph', text_align='center', y_offset=-7, text_color='black', text_font_size='9pt')
    s7.add_layout(labels_roll1)

    s8 = figure(title='Roll: ' + str(z_roll[1]), x_range=df_rates.columns.tolist(), y_range=df5.Steep.unique().tolist(), x_axis_location="below", y_axis_location="right", width=100 * n_crv - 75, height=400, toolbar_location=None)
    s8.grid.grid_line_color = None
    s8.axis.axis_line_color = None
    s8.axis.major_tick_line_color = None
    s8.axis.major_label_text_font_size = "12px"
    s8.yaxis.visible = False

    s8.rect(x="Curve", y="Steep", width=1, height=1, source=s4_source, fill_color={'field': 'Roll_2', 'transform': mapper_roll}, line_color=None)
    labels_roll2 = LabelSet(x='Curve', y='Steep', text='Roll_2', source=s4_source, level='glyph', text_align='center', y_offset=-7, text_color='black', text_font_size='9pt')
    s8.add_layout(labels_roll2)

    p = layout(children=[[s1, s2, s3, s4], [s5, s6, s7, s8]])

    # grid = gridplot([[s1, s2, s3, s4]], width=300, height=500)
    return p