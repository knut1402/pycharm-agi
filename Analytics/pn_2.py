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
from PLOT_BOKEH import plt_ois_curve_bokeh, plt_inf_curve_bokeh, ecfc_plot, plot_tool_bbg
from BOND_TABLES import linker_table
from INFL_CARRY import linker_carry_calc
#from MINING import get_data, data_heatmap, run_gmm


con = pdblp.BCon(debug=False, port=8194, timeout=50000)
con.start()


class SwapMon(param.Parameterized):
    update_flag = param.Boolean(default=False)  # Define update_flag as a param attribute
    calculate_button = param.Action(lambda x: x.param.trigger('calculate_button'), label='Calc')
    auto_recalc = param.Boolean(default=False, label="Auto Recalc")
    curve_row = param.DataFrame()
    fwd_row = param.DataFrame()
    def __init__(self):
        super(SwapMon, self).__init__()  # Initialize the param.Parameterized base class
        today = ql.Date(datetime.datetime.now().day, datetime.datetime.now().month, datetime.datetime.now().year)
        self.curve = None
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

        self.curve_input = pn.widgets.Select(name='Curve', options=['SOFR_DC', 'ESTER_DC', 'SONIA_DC'], width=100, height=50, margin=(20, 20, 10, 10),styles={'color': 'blue', 'font-size': '12pt'})
        t = ql_to_datetime(today-3)
        self.date_input = pn.widgets.DatePicker(name='Date', value=t, styles={'color': 'black', 'font-size': '10pt'}, width=100, height=30, margin=(23, 20, 10, 10))
        t1 = ql_to_datetime(c.cal.advance(today, -4, ql.Days))
        self.offset_date = pn.widgets.DatePicker(name='Offset', value=t1, styles={'color': 'black', 'font-size': '10pt'}, width=100, height=30, margin=(23, 20, 10, 10))
        self.quick_dates = pn.widgets.Select(name='Quick Dates', options=['Live', '1m', '3m', '6m', '1y'], styles={'color': 'black', 'font-size': '10pt'}, width=100, height=30, margin=(23, 20, 10, 10))
        self.curve_input.param.watch(self.update_curve, 'value')
        self.date_input.param.watch(self.update_curve, 'value')
        self.offset_date.param.watch(self.update_curve, 'value')
        self.update_notification = pn.widgets.StaticText(name='Status', value='df not yet updated')
        self.param.watch(self.toggle_auto_recalc, 'auto_recalc')
        self.periodic_callback = None

        # Curve table setup
        self.curve_data = pd.DataFrame({'x1': [2, 2, 5, 2, 5], 'x2': [5, 10, 30, 5, 10], 'x3': [0, 0, 0, 10, 30],
                                        'Rate': [0.0, 0.0, 0.0, 0.0, 0.0], '1m': [0.0, 0.0, 0.0, 0.0, 0.0],'3m': [0.0, 0.0, 0.0, 0.0, 0.0], '6m': [0.0, 0.0, 0.0, 0.0, 0.0], '1y': [0.0, 0.0, 0.0, 0.0, 0.0]})
        self.curve_table = pn.widgets.Tabulator(self.curve_data, show_index=False,  row_height=30, name='df3',
                                                      widths={'x1': 50, 'x2': 50, 'x3': 50, 'Rate': 50, '1m': 50, '3m': 50, '6m': 50, '1y': 50},
                                                      stylesheets=[css2], selectable = 'checkbox')
        self.curve_table.param.watch(self._update_curve_row, 'selection')

        # Fwds table setup
        self.fwd_data = pd.DataFrame({'x1': [1, 1, 2], 'x2': [1, 10, 1], 'x3': [0, 0, 3], 'x4': [0, 0, 1],
                                        'Fwds': [0.0, 0.0, 0.0], 'Chg': [0.0, 0.0, 0.0]})
        self.fwd_table = pn.widgets.Tabulator(self.fwd_data, show_index=False, row_height=30, name='df4',
                                              widths={'x1': 50, 'x2': 50, 'x3': 50, 'x4': 50, 'Fwds': 60, 'Chg': 60}, margin=(10,10,10,15), stylesheets=[css2],
                                              selectable = 'checkbox')
        self.fwd_table.param.watch(self._update_fwd_row, 'value')
        print(' ####################           look at me: initiating NOW')

        # Function to handle quick date selection
        @pn.depends(self.quick_dates.param.value, watch=True)
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

    def build_table(self):
        for row_index in np.arange(len(self.curve_data)):
            sw1 = int(self.curve_table.value.loc[row_index, 'x1'])
            sw2 = int(self.curve_table.value.loc[row_index, 'x2'])
            sw3 = int(self.curve_table.value.loc[row_index, 'x3'])
            if sw3 == 0:
                result = [Swap_Pricer([[self.curve, i, sw1], [self.curve, i, sw2]]).table['Spread'][1] for i in
                          [0, '1M', '3M', '6M', 1]]
            else:
                result = [
                    Swap_Pricer([[self.curve, i, sw1], [self.curve, i, sw2], [self.curve, i, sw3]]).table['Fly'][2] for
                    i in [0, '1M', '3M', '6M', 1]]

            self.curve_table.value.at[row_index, 'Rate'] = np.round(result[0], 1)
            self.curve_table.value.at[row_index, '1m'] = np.round(result[1], 1)
            self.curve_table.value.at[row_index, '3m'] = np.round(result[2], 1)
            self.curve_table.value.at[row_index, '6m'] = np.round(result[3], 1)
            self.curve_table.value.at[row_index, '1y'] = np.round(result[4], 1)

        self.curve_table.value = self.curve_data

    def fwds_table(self):
        for row_index in np.arange(len(self.fwd_data)):
            sw1 = int(self.fwd_table.value.loc[row_index, 'x1'])
            sw2 = int(self.fwd_table.value.loc[row_index, 'x2'])
            sw3 = int(self.fwd_table.value.loc[row_index, 'x3'])
            sw4 = int(self.fwd_table.value.loc[row_index, 'x4'])
            if ((sw3 == 0) & (sw4 == 0)):
                result = [ np.round(Swap_Pricer([[self.curve, sw1, sw2]]).table['Rate'][0],3) ]
            else:
                result = [ np.round(Swap_Pricer([[self.curve, sw1, sw2], [self.curve, sw3, sw4]]).table['Spread'][1], 1) ]

            self.fwd_table.value.at[row_index, 'Fwds'] = result[0]

        self.fwd_table.value = self.fwd_data

    def _update_curve_row(self, event=None):
        curve_indices = self.curve_table.selection
        if curve_indices:
            self.curve_row = self.curve_data.iloc[curve_indices]

    def _update_fwd_row(self, event):
        fwd_indices = self.fwd_table.selection
        if fwd_indices:
            self.fwd_row = self.fwd_data.iloc[fwd_indices]


    @param.depends('curve_row')  # React to changes in curve_row
    def update_plot_tool2(self):
        if self.curve_row is not None and not self.curve_row.empty:
            a1 = [self.curve_row['x1'].tolist()[0], self.curve_row['x2'].tolist()[0], self.curve_row['x3'].tolist()[0]]
            print(a1)
            a2 = [self.curve_row['x1'].tolist(), self.curve_row['x2'].tolist(), self.curve_row['x3'].tolist()]
            print(a2)

            fig3 = plot_tool_bbg(a1, self.curve)
        else:
            fig3 = pn.Row()
        return pn.Card( fig3, title="Curve Plot")


    @param.depends('fwd_row')  # React to changes in fwd_row
    def update_plot_tool(self):
        if self.fwd_row is not None and not self.fwd_row.empty:
            a1 = [self.fwd_row['x1'].tolist()[0], self.fwd_row['x2'].tolist()[0],
                  self.fwd_row['x3'].tolist()[0], self.fwd_row['x4'].tolist()[0]]
            print(a1)
            a2 = [self.fwd_row['x1'].tolist(), self.fwd_row['x2'].tolist(),
                  self.fwd_row['x3'].tolist(), self.fwd_row['x4'].tolist()]
            print(a2)

            fig2 = plot_tool_bbg(a1, self.curve)
        else:
            fig2 = pn.Row()
        return pn.Card( fig2, title="Fwds Plot")


    def calc_callback_fx(self, event):
        self.build_table()
        self.fwds_table()


    @pn.depends('update_flag', watch = False)  # Re-evaluate when update_flag changes
    def create_layout(self):
        print('create_layout trig')
        calculate_button = pn.widgets.Button(name='Tab-Calc', button_type='primary', on_click=self.calc_callback_fx, width=60, height=40, margin=(32, 15, 5, 5), styles={'color': 'gray', 'font-size': '12pt'})
        auto_recalc_toggle = pn.widgets.Checkbox(name="Auto-Recalc", value=self.auto_recalc, width=100, height=30,  styles={'color': 'grey', 'font-size': '8pt'}, margin = (60, 20, 10, 10))
        out1 = self.build_curve()

        return pn.Column(
            pn.Row(self.curve_input, self.quick_dates, self.date_input, self.offset_date, auto_recalc_toggle, calculate_button),
            pn.Row(out1[0], pn.Column(out1[2], self.curve_table,  self.fwd_table, width=450, height=225), pn.Spacer(width=75) , pn.Column(self.update_plot_tool, pn.Spacer(height=10), self.update_plot_tool2)),
            pn.Row(out1[1]),
            pn.Row(out1[3]))

    def update_curve(self, event = None):
        print('flag triggered')
        self.update_flag = not self.update_flag

    def build_curve(self):
        print("update_curve called with event:")
        self.update_notification.value = '........'
        a1 = self.date_input.value
        print('input_date:', a1.strftime('%d-%m-%Y'))
        a2 = self.offset_date.value
        print('offset_date:', a2.strftime('%d-%m-%Y'))
        a3 = self.curve_input
        self.curve = ois_dc_build(a3.value, b=a1.strftime('%d-%m-%Y'))
        swp_prc_tab =  swap_table(self.curve, offset=[a2.strftime('%d-%m-%Y')])
        swp_prc_tab.table.columns = ['Tenor', 'SwapRate', 'Δ1', 'Fwds', 'Rate', 'Δ2', 'Curve', 'Sprd', 'Δ3', 'Fly', 'Lvl', 'Δ4']
        df_pane = pn.widgets.DataFrame(swp_prc_tab.table, show_index = False, row_height = 30, name='df1', autosize_mode='none',
                                       widths={'Tenor': 50, 'SwapRate': 70, 'Δ1': 50, 'Fwds': 70, 'Rate': 70, 'Δ2': 50, 'Curve': 75, 'Sprd': 65, 'Δ3': 50, 'Fly': 75, 'Lvl': 65, 'Δ4': 50},
                                       width=800, height=510)
        fig1 = plt_ois_curve_bokeh([a3.value], h1=[0, a2.strftime('%d-%m-%Y')],
                                   max_tenor=30, bar_chg = 1, sprd = 0, name = '', fwd_tenor = '1y',int_tenor = '1y',
                                   built_curve= swp_prc_tab.all_curves, tail = 1, curve_fill = "", p_dim=[800,300])
        self.update_notification.value = 'updated at: ' + datetime.datetime.now().strftime("%H:%M:%S")
        print("update df done")

        if self.curve.ccy == 'USD':
            ivsp_data = pd.DataFrame(columns=['Fut', 'Px', 'Yield', 'IVSP', 'Chg:1D'])
            ivsp_data['Fut'] = ['TUH4', 'FVH4', 'TYH4', 'UXYH4', 'USH4', 'WNH4']
            ivsp_data['Px'] = [con.ref(ivsp_data['Fut'][i] + ' Comdty', ['PX_LAST'])['value'][0] for i in np.arange(len(ivsp_data['Fut']))]
            bond_fut_dets = [con.ref(ivsp_data['Fut'][i] + ' Comdty', ['FUT_CTD_ISIN', 'FUT_DLV_DT_LAST', 'FUT_CTD_MTY', 'FUT_CNVS_FACTOR', 'CRNCY'])['value']
                             for i in np.arange(len(ivsp_data['Fut']))]
            ivsp_data['Yield'] = [con.ref(bond_fut_dets[i][0] + ' Govt', ['YLD_YTM_BID'],
                                          ovrds=[('PX_BID', ivsp_data['Px'][i] * bond_fut_dets[i][3]), (('SETTLE_DT', bbg_date_str(bond_fut_dets[i][1], ql_date=0)))])['value'][0]
                                  for i in np.arange(len(bond_fut_dets))]
            swp_rates = Swap_Pricer([[swp_prc_tab.all_curves[0], str(bond_fut_dets[i][1].day)+'-'+str(bond_fut_dets[i][1].month)+'-'+str(bond_fut_dets[i][1].year),
                                      str(bond_fut_dets[i][2].day)+'-'+str(bond_fut_dets[i][2].month)+'-'+str(bond_fut_dets[i][2].year)]
                                     for i in np.arange(len(bond_fut_dets)) ]).rate
            ivsp_data['IVSP'] = np.round(-100*(ivsp_data['Yield'] - np.array(swp_rates)),1)

            offset_px = [con.ref(ivsp_data['Fut'][i] + ' Comdty', ['YEST_FUT_PX'])['value'][0] for i in np.arange(len(ivsp_data))]
            offset_yield = [con.ref(bond_fut_dets[i][0] + ' Govt', ['YLD_YTM_BID'],
                                          ovrds=[('PX_BID', offset_px[i] * bond_fut_dets[i][3]), (('SETTLE_DT', bbg_date_str(bond_fut_dets[i][1], ql_date=0)))])['value'][0]
                                  for i in np.arange(len(bond_fut_dets))]
            offset_swp_rt = Swap_Pricer([[swp_prc_tab.all_curves[1], str(bond_fut_dets[i][1].day)+'-'+str(bond_fut_dets[i][1].month)+'-'+str(bond_fut_dets[i][1].year),
                                      str(bond_fut_dets[i][2].day)+'-'+str(bond_fut_dets[i][2].month)+'-'+str(bond_fut_dets[i][2].year)]
                                     for i in np.arange(len(bond_fut_dets)) ]).rate
            offset_ivsp = -100*( np.array(offset_yield) - np.array(offset_swp_rt))

            ivsp_data['Chg:1D'] = np.round(ivsp_data['IVSP'] - offset_ivsp, 1)
            ivsp_data['Yield'] = np.round(ivsp_data['Yield'], 3)
            ivsp_data['Px'] = [px_dec_to_frac(ivsp_data['Px'][i]) for i in np.arange(len(ivsp_data)) ]
            df_ivsp = pn.widgets.DataFrame(ivsp_data, show_index=False, row_height=30, name='df2', autosize_mode='none',
                                       widths={'Fut': 70, 'Px': 70, 'Yield': 70, 'IVSP': 50, 'Chg:1D': 50})


        return df_pane, pn.Column(*fig1), df_ivsp, self.update_notification


    def toggle_auto_recalc(self, event):
        if event.new:
            self.periodic_callback = pn.state.add_periodic_callback(self.auto_update_curve, period=120000)  # 120000 ms = 2 mins
        else:
            if self.periodic_callback:
                pn.state.remove_periodic_callback(self.periodic_callback)
                self.periodic_callback = None
    def auto_update_curve(self):
        self.update_curve()

    def view(self):
        return self.create_layout



class InflSwapMon(param.Parameterized):
    update_flag = param.Boolean(default=False)  # Define update_flag as a param attribute
    build_button = param.Action(lambda x: x.param.trigger('build_button'), label='Build')
    calculate_button = param.Action(lambda x: x.param.trigger('calculate_button'), label='Calc')
    def __init__(self):
        super(InflSwapMon, self).__init__()  # Initialize the param.Parameterized base class
        today = ql.Date(datetime.datetime.now().day, datetime.datetime.now().month, datetime.datetime.now().year)
        self.infcurve = None
        c = ccy('SOFR_DC', today)
        pn.extension('tabulator')

        self.curve_input = pn.widgets.Select(name='Curve', options=['UKRPI', 'HICPxT', 'FRCPI', 'USCPI'], width=100, height=50, margin=(20, 20, 10, 10),styles={'color': 'blue', 'font-size': '12pt'})
        t = ql_to_datetime(today-2)
        self.date_input = pn.widgets.DatePicker(name='Date', value=t, styles={'color': 'black', 'font-size': '10pt'}, width=100, height=30, margin=(23, 20, 10, 10))
        t1 = ql_to_datetime(c.cal.advance(today, -3, ql.Days))
        self.offset_date = pn.widgets.DatePicker(name='Offset', value=t1, styles={'color': 'black', 'font-size': '10pt'}, width=100, height=30, margin=(23, 20, 10, 10))
        self.quick_dates = pn.widgets.Select(name='Quick Dates', options=['Live', '1m', '3m', '6m', '1y'], styles={'color': 'black', 'font-size': '10pt'}, width=100, height=30, margin=(23, 20, 10, 10))
        self.lag = pn.widgets.TextInput(name='Lag', value='3', styles={'color': 'black', 'font-size': '10pt'}, width=60, height=30, margin=(20, 20, 10, 10))
        self.fixings = pn.widgets.Select(name='Fixing Curve', options=['Market', 'Barcap', 'Seas'], width=100,height=50, margin=(20, 20, 10, 10), styles={'color': 'black', 'font-size': '10pt'})
        self.curve_input.param.watch(self.update_curve, 'value')
        self.date_input.param.watch(self.update_curve, 'value')
        self.offset_date.param.watch(self.update_curve, 'value')
        self.update_notification = pn.widgets.StaticText(name='Status', value='df not yet updated')
        self.df_pane = pn.pane.DataFrame(pd.DataFrame(), sizing_mode='stretch_width')
        self.plot_pane = pn.Column(margin=(20, 20, 20, 300))

        # Interactive table setup
        self.table_data = pd.DataFrame({'x1': [2, 2, 2], 'x2': [4, 9, 30], 'Rate': [0.0, 0.0, 0.0], '1m': [0.0, 0.0, 0.0],'3m': [0.0, 0.0, 0.0], '6m': [0.0, 0.0, 0.0], '1y': [0.0, 0.0, 0.0]})
        self.interactive_table = pn.widgets.Tabulator(self.table_data, show_index=False, margin=(20, 20, 300, 10))

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

    def update_curve(self, event=None):
        self.update_flag = not self.update_flag

    def create_layout(self):
        print('inflation_create_layout')
        calculate_button = pn.widgets.Button(name='Calc', button_type='primary', on_click=self.build_table, width=50, height=30, margin=(10, 10, 0, 0), styles={'color': 'gray', 'font-size': '12pt'})
        build_button = pn.widgets.Button(name='Build', button_type='primary', on_click=self.build_infcurve, width=50, height=30, margin=(40, 10, 0, 0), styles={'color': 'gray', 'font-size': '12pt'})
        return pn.Column(
            pn.Row(self.curve_input, self.quick_dates, self.date_input, self.offset_date, self.lag, self.fixings, build_button),
            self.df_pane,
            self.update_notification,
            pn.Row(pn.pane.Markdown("## Curves"), calculate_button),
            pn.Row(self.interactive_table, pn.Spacer(), self.plot_pane)
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
        b5 = [int(item.strip()) for item in a4.split(',')]
        if len(b5) == 1:
            b6 = b5 * len(self.infcurve)
        else:
            b6 = b5
        print(b6)
        self.plot_pane.clear()
        self.df_pane.object = inf_swap_table(self.infcurve, lag = b6,
                                 outright_rates=[1,2,3,4,5,6,7,8,9,10,12,15,20,25,30],
                                 fwd_rates= [(1,1), (2,1), (3,1), (4,1), (2,2), (3,2), (5,5), (10,5), (10,10), (15,15) ],
                                 curve_rates= [(2,3), (2,5), (2,10), (5,10), (5,30), (10,30)],
                                 fly_rates= [(2,3,5), (2,5,10), (3,5,7), (5,10,30)],
                                 shift = [0,'1M','2M','3M'], price_nodes = 1, use_forecast = a7, use_mkt_fixing = a6).table

        fig1 = plt_inf_curve_bokeh([a1], h1=[0, a3], max_tenor=30, bar_chg = 1, sprd = 0, built_curve = self.infcurve, name = '')
        self.plot_pane.extend([column(*fig1)])
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



class Swap_Plot(param.Parameterized):
    plot_button = param.Action(lambda x: x.param.trigger('plot_button'), label='Plot')
    def __init__(self):
        super(Swap_Plot, self).__init__()  # Initialize the param.Parameterized base class
        today = ql.Date(datetime.datetime.now().day, datetime.datetime.now().month, datetime.datetime.now().year)
        c = ccy('SOFR_DC', today)

        options_list = ['SOFR_DC', 'ESTER_DC', 'SONIA_DC']
        self.layout_pane = pn.Column()
        self.multi_select = pn.widgets.MultiSelect(name='Curves', options=options_list, size=6, styles={'color': 'black', 'font-size': '8pt'}, width=180, height=800, margin=(5, 20, 10, 10))

        self.offset_dates = pn.widgets.TextInput(name='Offsets', value='0',  styles={'color': 'black', 'font-size': '8pt'}, width=120, height=30, margin=(20, 20, 10, 10))
        self.max_tenor = pn.widgets.TextInput(name='Max Tenor', value='30',
                                              styles={'color': 'black', 'font-size': '8pt'}, width=60, height=30,
                                              margin=(20, 20, 10, 10))
        self.changes = pn.widgets.TextInput(name='Changes', value='0',
                                            styles={'color': 'black', 'font-size': '8pt'}, width=60, height=30,
                                            margin=(20, 20, 10, 10))
        self.spreads = pn.widgets.TextInput(name='Spreads', value='0',
                                            styles={'color': 'black', 'font-size': '8pt'}, width=60, height=30,
                                            margin=(20, 20, 10, 10))
        self.fwd_tenor = pn.widgets.TextInput(name='Fwd Tenor', value='1d',
                                              styles={'color': 'black', 'font-size': '8pt'}, width=60, height=30,
                                              margin=(20, 20, 10, 10))
        self.int_tenor = pn.widgets.TextInput(name='Internal Tenor', value='1m',
                                              styles={'color': 'black', 'font-size': '8pt'}, width=60, height=30,
                                              margin=(20, 20, 10, 10))

    def create_layout(self):
        plot_button = pn.widgets.Button(name='Calc', button_type='primary', on_click=self.build_plot, width=180, height=30, margin=(20, 5, 10, 10), styles={'color': 'gray', 'font-size': '12pt'})
        return pn.Column(
            pn.Row(self.offset_dates, self.max_tenor, self.changes, self.spreads, self.fwd_tenor, self.int_tenor),
            pn.Row(plot_button),
            pn.Row(self.multi_select, self.layout_pane) )

    def build_plot(self, event):
        self.layout_pane.clear()
        print("building plot:")
#        self.update_notification.value = '........'
        a1 = self.multi_select
        a2 = self.offset_dates
        a3 = self.max_tenor
        a4 = self.changes
        a5 = self.spreads
        a6 = self.fwd_tenor
        a7 = self.int_tenor
        print(a1.value, type(a1.value))
        print(a2.value, type(a2.value))
        print(a3.value, type(a3.value))
        print(a4.value, type(a4.value))
        print(a5.value, type(a5.value))
        print(a6.value, type(a6.value))
        print(a7.value, type(a7.value))
        b2 = a2.value
        b3 = [item.strip() for item in b2.split(',')]
        b4 = []
        for i in b3:
            if len(i) < 4:
                b4 = b4 + [int(i)]
            else:
                b4 = b4 + [i]
        fig1 = plt_ois_curve_bokeh(a1.value, h1=b4, max_tenor=int(a3.value), bar_chg=int(a4.value), sprd=int(a5.value), name='', fwd_tenor=a6.value, int_tenor=a7.value, tail=1, curve_fill="", label_curve_name=1)
        self.layout_pane.extend([column(*fig1)])
        print("done!")
        return

    def view(self):
            return self.create_layout



class ECFC(param.Parameterized):
    plot_button = param.Action(lambda x: x.param.trigger('plot_button'), label='Plot')
    def __init__(self):
        super(ECFC, self).__init__()
        today = ql.Date(datetime.datetime.now().day, datetime.datetime.now().month, datetime.datetime.now().year)
        c = ccy('SOFR_DC', today)

        list1 = ["GDP", "CPI", "PCE", "Core-PCE", "UNEMP", "FISC"]
        list2 = ["US", "EU", "GB", "DE", "FR", "IT", "ES", "CA", "AU", "NZ", "SE", "NO", "CH", "JP", "KR", "CN"]
        list3 = [str(today.year()+i) for i in np.arange(5)-1]
        list4 = ["BAR", "BOA", "BNP", "CE", "CIT", "CAG", "CSU", "DNS", "FTC", "GS", "HSB", "IG", "JPM", "MS", "NTX", "NS", "NDA", "PMA", "UBS", "WF", "SCB"]
        list5 = ["FED", "ECB", "BOE", "OEC", "IMF", "WB", "EU", "EC", "OBR", "IST", "DBK", "ISE", "BOC", "RBA", "RIK", "NOR", "NPC"]
        self.layout_pane = pn.Column()
        self.multi_select_data = pn.widgets.MultiSelect(name='Data', options=list1, size=6, styles={'color': 'black', 'font-size': '8pt'}, width=100, height=300, margin=(5, 20, 10, 10))
        self.multi_select_region = pn.widgets.MultiSelect(name='Region', options=list2, size=6, styles={'color': 'black', 'font-size': '8pt'}, width=100, height=300, margin=(5, 20, 10, 10))
        self.multi_select_year = pn.widgets.MultiSelect(name='Year', options=list3, size=6, styles={'color': 'black', 'font-size': '8pt'}, width=100, height=300, margin=(5, 20, 10, 10))
        self.multi_select_contrib = pn.widgets.MultiSelect(name='Contrib', options=list4, size=6, styles={'color': 'black', 'font-size': '8pt'}, width=100, height=300, margin=(5, 20, 10, 10))
        self.multi_select_off = pn.widgets.MultiSelect(name='Official', options=list5, size=6, styles={'color': 'black', 'font-size': '8pt'}, width=100, height=300, margin=(5, 20, 10, 10))

    def create_layout(self):
        plot_button = pn.widgets.Button(name='Calc', button_type='primary', on_click=self.build_plot, width=180, height=30, margin=(20, 5, 10, 10), styles={'color': 'gray', 'font-size': '12pt'})
        return pn.Column(
            pn.Row(self.multi_select_data, self.multi_select_region, self.multi_select_year, self.multi_select_contrib, self.multi_select_off),
            pn.Row(plot_button),
            pn.Row(self.layout_pane))

    def build_plot(self, event):
        self.layout_pane.clear()
        print("building plot:")
        a1 = self.multi_select_data
        a2 = self.multi_select_region
        a3 = self.multi_select_year
        a4 = self.multi_select_contrib
        a5 = self.multi_select_off
        print(a1.value[0], len(a1.value))
        print(a2.value[0], type(a2.value[0]))
        print(a3.value, type(a3.value))
        print(a4.value, type(a4.value))
        print(a5.value, type(a5.value))
        s_plot = []
        n_plot = len(a1.value)*len(a2.value)*len(a3.value)
        print(n_plot)
        for i in np.arange(len(a1.value)):
            for j in np.arange(len(a2.value)):
                for k in np.arange(len(a3.value)):
                    fig1 = ecfc_plot(a1.value[i], a2.value[j], a3.value[k], contrib1 = a4.value[0], off = a5.value[0])
                    s_plot.append(fig1)

        self.layout_pane.extend( [gridplot(s_plot, ncols=3) ] )

        print("done!")
        return

    def view(self):
            return self.create_layout





class Quix2:
    def __init__(self):
        print('quix_call_swap_mon')
        print("quix2 is being called from", inspect.getmodulename(inspect.stack()[1][1]))
#        self.SwapMonitor = SwapMon()
        self.SwapPlot = Swap_Plot()
        self.InflSwapMonitor = InflSwapMon()
#        self.Eco = ECFC()
        print('quix_finish_all_calls')

        # Combine all tabs into a Tabs layout
        self.tabs = pn.Tabs(
            ('Swap Monitor', SwapMon().view()),
            ('Inflation Swap', self.InflSwapMonitor.view()),
            ('Swap Plot', self.SwapPlot.view()),
            ('Eco', self.Eco.view())
        )
    def servable(self):
        return self.tabs.servable()

# main_q = SwapMon.make_it_servable()
# main_q.servable()

#SwapMon.make_it_servable()