import numpy as np
import panel as pn
import inspect
import pandas as pd
import hvplot.pandas
from bokeh.models.widgets.tables import NumberFormatter, BooleanFormatter
from bokeh.plotting import figure, show
from bokeh.models import HoverTool, BoxZoomTool, ResetTool
from bokeh.models import ColumnDataSource
from bokeh.layouts import row, column, gridplot, grid
from bokeh.palettes import Category10, brewer, Category20

import sys
import os
import datetime
#from datetime import datetime, timedelta, time
from dateutil.relativedelta import relativedelta
import param


sys.path.append(os.path.abspath("C:/Users/A00007579/PycharmProjects/pythonProject/Builds"))
sys.path.append(os.path.abspath("C:/Users/A00007579/PycharmProjects/pythonProject/Sundry"))
sys.path.append(os.path.abspath("C:/Users/A00007579/PycharmProjects/pythonProject/"))
sys.path.append(os.path.abspath("C:/Users/A00007579/PycharmProjects/pythonProject/DataLake"))
from Utilities import *
from Conventions import FUT_CT,FUT_CT_Q, ccy, ccy_infl
from OIS_DC_BUILD import ois_dc_build
from SWAP_BUILD import swap_build
from SWAP_PRICER import Swap_Pricer, Swap_curve_fwd, quick_swap
from SWAP_TABLE import swap_table, swap_table2, curve_hmap
from INF_ZC_BUILD import infl_zc_swap_build, Infl_ZC_Pricer, inf_swap_table
from BOND_CURVES import bond_curve_build
from VOL_BUILD import build_vol_surf, build_vol_spline, bond_fut_opt_strat, get_sim_option_px, build_stir_vol_surf, stir_opt_strat
from PLOT import plt_curve, plt_inf_curve, plt_opt_strat, rates_hm, curve_hm, plt_ois_curve, plot_opt_vol_surf, plt_stir_opt_strat, plotool, ecfc_plot
from PLOT_BOKEH import plt_ois_curve_bokeh, plt_inf_curve_bokeh, ecfc_plot, plot_tool_bbg, plot_inflation_fixings
from BOND_TABLES import linker_table
from INFL_CARRY import linker_carry_calc
#from MINING import get_data, data_heatmap, run_gmm

con = pdblp.BCon(debug=False, port=8194, timeout=50000)
con.start()


class InflSwapMon(param.Parameterized):
    update_flag = param.Boolean(default=False)  # Define update_flag as a param attribute
    build_button = param.Action(lambda x: x.param.trigger('build_button'), label='Build')
    calculate_button = param.Action(lambda x: x.param.trigger('calculate_button'), label='Tab-Calc')
    def __init__(self):
        super(InflSwapMon, self).__init__()  # Initialize the param.Parameterized base class
        today = ql.Date(datetime.datetime.now().day, datetime.datetime.now().month, datetime.datetime.now().year)
        self.infcurve = None
        c = ccy('SOFR_DC', today)
        pn.extension('tabulator')

        css2 = """
                .tabulator .tabulator-header .tabulator-col .tabulator-col-content .tabulator-col-title{
                    font-size: 11px;
                    color: #0072b5;
                }
                .tabulator .tabulator-tableholder .tabulator-table .tabulator-row .tabulator-cell {
                    font-size: 11px;
                    height: 20px;
                }
                .tabulator .tabulator-tableholder .tabulator-table{
                    font-size: 11px;
                }
                """

        self.curve_input = pn.widgets.Select(name='Curve', options=['UKRPI', 'HICPxT', 'FRCPI', 'USCPI'], width=100, height=50, margin=(20, 20, 10, 10),styles={'color': 'blue', 'font-size': '12pt'})
        t = ql_to_datetime(today)
        self.date_input = pn.widgets.DatePicker(name='Date', value=t, styles={'color': 'black', 'font-size': '10pt'}, width=100, height=30, margin=(23, 20, 10, 10))
        t1 = ql_to_datetime(c.cal.advance(today, -1, ql.Days))
        self.offset_date = pn.widgets.DatePicker(name='Offset', value=t1, styles={'color': 'black', 'font-size': '10pt'}, width=100, height=30, margin=(23, 20, 10, 10))
        self.quick_dates = pn.widgets.Select(name='Quick Dates', options=['Live', '1m', '3m', '6m', '1y'], styles={'color': 'black', 'font-size': '10pt'}, width=100, height=30, margin=(23, 20, 10, 10))
        self.lag = pn.widgets.TextInput(name='Lag', value=str(ccy_infl(self.curve_input.value,today).lag), styles={'color': 'black', 'font-size': '10pt'}, width=60, height=30, margin=(20, 20, 10, 10))
        self.fixings = pn.widgets.Select(name='Fixing Curve', options=['Market', 'Barcap', 'Seas'], width=100,height=50, margin=(20, 20, 10, 10), styles={'color': 'black', 'font-size': '10pt'})
        self.curve_input.param.watch(self.update_curve, 'value')
        self.date_input.param.watch(self.update_curve, 'value')
        self.offset_date.param.watch(self.update_curve, 'value')
        self.update_notification = pn.widgets.StaticText(name='Status', value='df not yet updated')
        self.generic = pn.widgets.Checkbox(name='Fix:#', value=False, styles={'color': 'black', 'font-size': '9pt'}, width=100, height=30, margin=(55, 10, 0, 20))
        self.df_pane = pn.widgets.DataFrame(pd.DataFrame(), show_index = False, row_height = 30, name='df1', width=800, height=510)

#        self.df_pane = pn.widgets.DataFrame(pd.DataFrame(columns=['Tenor', 'ZC', 'Δ1', 'Months', 'Barcap', 'Mkt', 'Chg', 'Fwds', 'Fwd.ZC', 'Δ.1', 'Curves', 'Rate', 'Δ:1', '1M', '2M', '3M']),
#                                             show_index = False, row_height = 30, name='df1',
#                                             autosize_mode='none',
#                                             widths={'Tenor': 50, 'SwapRate': 70, 'Δ1': 50, 'Fwds': 70, 'Rate': 70, 'Δ2': 50, 'Curve': 75, 'Sprd': 65, 'Δ3': 50, 'Fly': 75, 'Lvl': 65, 'Δ4': 50},
#                                             width=800, height=510)

        self.plot_pane = pn.Column()
        self.fixings_plot = pn.Column()

        # Interactive table setup
        self.table_data = pd.DataFrame({'x1': [2, 2, 2], 'x2': [4, 9, 30], 'Rate': [0.0, 0.0, 0.0], '1m': [0.0, 0.0, 0.0],'3m': [0.0, 0.0, 0.0], '6m': [0.0, 0.0, 0.0], '1y': [0.0, 0.0, 0.0]})
        self.interactive_table = pn.widgets.Tabulator(self.table_data, show_index=False,  stylesheets=[css2])

        # Function to handle quick date selection
        @pn.depends(self.quick_dates.param.value)
        def handle_quick_dates(selected_period):
            if selected_period == 'Live':
                new_date = t
            elif selected_period == '1m':
                new_date = t - relativedelta(months=1)
            elif selected_period == '3m':
                new_date = t - relativedelta(months=3)
            elif selected_period == '6m':
                new_date = t - relativedelta(months=6)
            elif selected_period == '1y':
                new_date = t - relativedelta(years=1)
            else:
                new_date = t
            self.date_input.value = new_date

    def update_curve(self, event):
        os.chdir('C:\\Users\A00007579\PycharmProjects\pythonProject')
        today = ql.Date(datetime.datetime.now().day, datetime.datetime.now().month, datetime.datetime.now().year)
        self.lag.value = str(ccy_infl(self.curve_input.value, today).lag)
        self.build_infcurve(event)

    def create_layout(self):
        print('inflation_create_layout')
        calculate_button = pn.widgets.Button(name='Tab-Calc', button_type='primary', on_click=self.build_table, width=50, height=30, margin=(40, 10, 0, 0), styles={'color': 'gray', 'font-size': '12pt'})
        build_button = pn.widgets.Button(name='Build', button_type='primary', on_click=self.build_infcurve, width=50, height=30, margin=(40, 10, 0, 0), styles={'color': 'gray', 'font-size': '12pt'})
        return pn.Column(
            pn.Row(self.curve_input, self.quick_dates, self.date_input, self.offset_date, self.lag, self.fixings, build_button, calculate_button, self.generic),
            pn.Row(self.df_pane, self.interactive_table),
            pn.Row(self.plot_pane, pn.Spacer(width=50), self.fixings_plot ),
            self.update_notification
        )


    def build_infcurve(self, event):
        print("update_curve called with event:")
        self.update_notification.value = '........'
        a1 = self.curve_input.value
        a2 = self.date_input.value.strftime('%d-%m-%Y')
        a3 = self.offset_date.value.strftime('%d-%m-%Y')
        a4 = self.lag.value
        a5 = self.fixings.value
        print(a1)
        print(a2)
        print(a3)
        print(a4, type(a4))
        print(a5)

        b3 = [item.strip() for item in a3.split(',')]
        b4 = [a2]
        for i in b3:
            if len(i) < 4:
                b4 = b4 + [int(i)]
            else:
                b4 = b4 + [i]

        a6 = 0
        a7 = 0
        if a5 == 'Market':
            a6 = 1
        if a5 == 'Barcap':
            a7 = 1

        print(b3, b4)
        self.infcurve = [ infl_zc_swap_build(a1, b=b4[i] ) for i in np.arange(len(b4)) ]
        print('bases:', self.infcurve[0].base_month, self.infcurve[1].base_month)

        b5 = [int(item.strip()) for item in a4.split(',')]
        if len(b5) == 1:
            print(b5)
            b6 = b5 + [b5[0]+ int((self.infcurve[1].base_month - self.infcurve[0].base_month)/30) ]     #### auto adjusting the lags to get same base pricing in ZC Table
        else:
            b6 = b5
        print(b6)
        self.plot_pane.clear()
        self.fixings_plot.clear()
        self.df_pane.value = inf_swap_table(self.infcurve, lag = b6,
                                 outright_rates=[1,2,3,4,5,6,7,8,9,10,12,15,20,25,30],
                                 fwd_rates= [(1,1), (2,1), (3,1), (4,1), (2,2), (3,2), (5,5), (10,5), (10,10), (15,15) ],
                                 curve_rates= [(2,3), (2,5), (2,10), (5,10), (5,30), (10,30)],
                                 fly_rates= [(2,3,5), (2,5,10), (3,5,7), (5,10,30)],
                                 shift = [0,'1M','2M','3M'], price_nodes = 1, use_forecast = a7, use_mkt_fixing = a6).table
        print('table done')
        fig1 = plt_inf_curve_bokeh([a1], h1=[0, a3], max_tenor=30, bar_chg = 1, sprd = 0, built_curve = self.infcurve, name = '', p_dim=[750,300])
        self.plot_pane.extend([column(*fig1)])

        fig2 = plot_inflation_fixings(a1, self.infcurve, gen = self.generic.value)
        self.fixings_plot.extend([row(*fig2)])


        self.update_notification.value = 'updated at: ' + datetime.datetime.now().strftime("%H:%M:%S")
        print("update df done")
        return

    def build_table(self, event):
        for row_index in np.arange(len(self.table_data)):
            st_tn = int(self.interactive_table.value.loc[row_index, 'x1'])
            mt_tn = int(self.interactive_table.value.loc[row_index, 'x2'])#
            result = [Swap_Pricer([[self.curve,i,st_tn],[self.curve,i,mt_tn]]).table['Spread'][1] for i in [0, '1M', '3M', '6M', 1]]
            self.interactive_table.value.at[row_index, 'Rate'] = np.round(result[0],1)
            self.interactive_table.value.at[row_index, '1m'] = np.round(result[1],1)
            self.interactive_table.value.at[row_index, '3m'] = np.round(result[2],1)
            self.interactive_table.value.at[row_index, '6m'] = np.round(result[3],1)
            self.interactive_table.value.at[row_index, '1y'] = np.round(result[4],1)

        self.interactive_table.value = self.table_data  # Refresh the table

    def view(self):
        return self.create_layout






























