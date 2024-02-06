import numpy as np
import sys
import os
import datetime
from dateutil.relativedelta import relativedelta
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

con = pdblp.BCon(debug=False, port=8194, timeout=50000)
con.start()

class SwapMon(param.Parameterized):
    build_button = param.Action(lambda x: x.param.trigger('build_button'), label='Build')
    calculate_button = param.Action(lambda x: x.param.trigger('calculate_button'), label='Tab-Calc')

    def __init__(self, **params):
        super(SwapMon, self).__init__(**params)  # Initialize the param.Parameterized base class
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
        t = ql_to_datetime(today)
        self.date_input = pn.widgets.DatePicker(name='Date', value=t, styles={'color': 'black', 'font-size': '10pt'}, width=100, height=30, margin=(23, 20, 10, 10))
        t1 = ql_to_datetime(c.cal.advance(today, -1, ql.Days))
        self.offset_date = pn.widgets.DatePicker(name='Offset', value=t1, styles={'color': 'black', 'font-size': '10pt'}, width=100, height=30, margin=(23, 20, 10, 10))
        self.quick_dates = pn.widgets.Select(name='Quick Dates', options=['Live', '1m', '3m', '6m', '1y'], styles={'color': 'black', 'font-size': '10pt'}, width=100, height=30, margin=(23, 20, 10, 10))
        self.curve_input.param.watch(self.update_curve, 'value')
#        self.date_input.param.watch(self.update_curve, 'value')     ##### otherwise triggers before re-calc offset
        self.offset_date.param.watch(self.update_curve, 'value')
        self.update_notification = pn.widgets.StaticText(name='Status', value='df not yet updated')

        # Curve table setup
        self.curve_data = pd.DataFrame({'x1': [2, 2, 5, 2, 5], 'x2': [5, 10, 30, 5, 10], 'x3': [0, 0, 0, 10, 30],
                                        'Rate': [0.0, 0.0, 0.0, 0.0, 0.0], '1m': [0.0, 0.0, 0.0, 0.0, 0.0],
                                        '3m': [0.0, 0.0, 0.0, 0.0, 0.0], '6m': [0.0, 0.0, 0.0, 0.0, 0.0],
                                        '1y': [0.0, 0.0, 0.0, 0.0, 0.0]})
        self.curve_table = pn.widgets.Tabulator(self.curve_data, show_index=False,  row_height=30, name='df3',
                                                widths={'x1': 50, 'x2': 50, 'x3': 50, 'Rate': 50, '1m': 50, '3m': 50, '6m': 50, '1y': 50},
                                                stylesheets=[css2], selectable = 'checkbox')
        self.curve_table.param.watch(self._update_row, 'selection')

        # Fwds table setup
        self.fwd_data = pd.DataFrame({'x1': [1, 1, 2], 'x2': [1, 10, 1], 'x3': [0, 0, 3], 'x4': [0, 0, 1],
                                      'Fwds': [0.0, 0.0, 0.0], 'Chg': [0.0, 0.0, 0.0]})
        self.fwd_table = pn.widgets.Tabulator(self.fwd_data, show_index=False, row_height=30, name='df4',
                                              widths={'x1': 50, 'x2': 50, 'x3': 50, 'x4': 50, 'Fwds': 60, 'Chg': 60}, margin=(10,10,10,15),
                                              stylesheets=[css2], selectable = 'checkbox')
        self.fwd_table.param.watch(self._update_row, 'selection')

        print('now : initiating')

        ### output panes
        self.curve_df = pn.widgets.DataFrame(pd.DataFrame(columns=['Tenor', 'SwapRate', 'Δ1', 'Fwds', 'Rate', 'Δ2', 'Curve', 'Sprd', 'Δ3','Fly', 'Lvl','Δ4']),
                                             show_index = False, row_height = 30, name='df1',
                                             autosize_mode='none',
                                             widths={'Tenor': 50, 'SwapRate': 70, 'Δ1': 50, 'Fwds': 70, 'Rate': 70, 'Δ2': 50, 'Curve': 75, 'Sprd': 65, 'Δ3': 50, 'Fly': 75, 'Lvl': 65, 'Δ4': 50},
                                             width=800, height=510)
        self.ivsp_df = pn.widgets.DataFrame(pd.DataFrame(columns=['Fut', 'Px', 'Yield', 'IVSP', 'Chg:1D']),
                                            show_index=False, row_height=30, name='df2', autosize_mode='none',
                                            widths={'Fut': 70, 'Px': 70, 'Yield': 70, 'IVSP': 50, 'Chg:1D': 50})
        self.curve_plot = pn.Column()
        self.curve_tab_plot = pn.Column()
        self.fwd_tab_plot = pn.Column()
        self.multi_plot = pn.Column()

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
            self.date_input.value =  ql_to_datetime(c.cal.advance( datetime_to_ql(new_date) , 0, ql.Days))
            self.offset_date.value = ql_to_datetime(c.cal.advance( datetime_to_ql(new_date) , -1, ql.Days))

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

    def _update_row(self, event):
        print('self.curve_table.selection:', self.curve_table.selection)
        curve_indices = self.curve_table.selection
        fwd_indices = self.fwd_table.selection
        print('curve_indices:', curve_indices, 'fwd_indices:', fwd_indices)
        if len(curve_indices)+len(fwd_indices) == 1:
            if len(curve_indices) == 1:             #### only curve table called
                self.multi_plot.clear()
                new_df = self.curve_data.iloc[int(curve_indices[0])]
#               print(new_df)
                a1 = [int(new_df['x1'].tolist()), int(new_df['x2'].tolist()), int(new_df['x3'].tolist())]
                print('a1: ', a1)
                fig3 = plot_tool_bbg([a1], self.curve)
                self.curve_tab_plot.clear()
                self.curve_tab_plot.extend([column(*fig3)])
            else:
                self.multi_plot.clear()
                new_df = self.fwd_data.iloc[int(fwd_indices[0])]
#               print(new_df)
                a1 = [int(new_df['x1'].tolist()), int(new_df['x2'].tolist()), int(new_df['x3'].tolist()), int(new_df['x4'].tolist())]
                print('a1: ',a1)
                fig2 = plot_tool_bbg([a1], self.curve)
                self.fwd_tab_plot.clear()
                self.fwd_tab_plot.extend([column(*fig2)])
        elif len(curve_indices)+len(fwd_indices) > 1:
            self.fwd_tab_plot.clear()
            self.curve_tab_plot.clear()
            new_df_1 = self.curve_data.iloc[curve_indices]
            print('new_df_1:',new_df_1)
            new_df_2 = self.fwd_data.iloc[fwd_indices]
            print('new_df_2:', new_df_2)
            if len(fwd_indices) > 0:
                a1 = [[int(new_df_2['x1'][i]), int(new_df_2['x2'][i]), int(new_df_2['x3'][i]), int(new_df_2['x4'][i])] for i in fwd_indices]
#                a1 = [[int(new_df_1['x1'][i]), int(new_df_1['x2'][i]), int(new_df_1['x3'][i])] for i in curve_indices]
                if len(curve_indices) > 0:
                    a2 = [[int(new_df_1['x1'][i]), int(new_df_1['x2'][i]), int(new_df_1['x3'][i])] for i in curve_indices]
#                    a2 = [[int(new_df_2['x1'][i]), int(new_df_2['x2'][i]), int(new_df_2['x3'][i]), int(new_df_2['x4'][i])] for i in fwd_indices]
                    a1 = a1 + a2
            else:
                a1 = [[int(new_df_1['x1'][i]), int(new_df_1['x2'][i]), int(new_df_1['x3'][i])] for i in curve_indices]
#                a1 = [[int(new_df_2['x1'][i]), int(new_df_2['x2'][i]), int(new_df_2['x3'][i]),int(new_df_2['x4'][i])] for i in fwd_indices]
            print('a1: ', a1)
            fig4 = plot_tool_bbg(a1, self.curve, p_dim=[700,400])
            self.multi_plot.clear()
            self.multi_plot.extend([column(*fig4)])
        else:
            fig3 = pn.Row()
            fig2 = pn.Row()
            self.fwd_tab_plot.clear()
            self.curve_tab_plot.clear()
            self.multi_plot.clear()
        return

    def calc_callback_fx(self, event):
        self.build_table()
        self.fwds_table()

    def create_layout(self):
        print('create: layout')
        build_button = pn.widgets.Button(name='Build', button_type='primary',  width=60, height=40, margin=(32, 15, 5, 5), styles={'color': 'red', 'font-size': '12pt'})
        build_button.on_click(self.build_curve)
        calculate_button = pn.widgets.Button(name='Tab-Calc', button_type='primary', on_click=self.calc_callback_fx, width=60, height=40, margin=(32, 15, 5, 5), styles={'color': 'gray', 'font-size': '12pt'})

        return pn.Column(
            pn.Row(self.curve_input, self.quick_dates, self.date_input, self.offset_date, build_button, calculate_button),
            pn.Row(self.curve_df, pn.Column(self.ivsp_df, self.curve_table,  self.fwd_table, width=450, height=225), pn.Spacer(width=75),
                   pn.Column(pn.Card( self.fwd_tab_plot, title="Fwds   Plot  "),
                             pn.Spacer(height=15),
                             pn.Card( self.curve_tab_plot, title="Curve Plot"),
                             pn.Spacer(height=15),
                             pn.Card(self.multi_plot, title="Multi     Plot   "))),
            pn.Row(self.curve_plot),
            pn.Row(self.update_notification) )

    def build_curve(self, event):
        print("build curve...")
        self.update_notification.value = '........'
        a1 = self.date_input.value
        print('input_date:', a1.strftime('%d-%m-%Y'))
        a2 = self.offset_date.value
        print('offset_date:', a2.strftime('%d-%m-%Y'))
        a3 = self.curve_input
        self.curve = ois_dc_build(a3.value, b=a1.strftime('%d-%m-%Y'))
        swp_prc_tab =  swap_table(self.curve, offset=[a2.strftime('%d-%m-%Y')])
        swp_prc_tab.table.columns = ['Tenor', 'SwapRate', 'Δ1', 'Fwds', 'Rate', 'Δ2', 'Curve', 'Sprd', 'Δ3', 'Fly', 'Lvl', 'Δ4']
        self.curve_df.value = swp_prc_tab.table
        self.curve_plot.clear()
        fig1 = plt_ois_curve_bokeh([a3.value], h1=[0, a2.strftime('%d-%m-%Y')],
                                   max_tenor=30, bar_chg = 1, sprd = 0, name = '', fwd_tenor = '1y',int_tenor = '1y',
                                   built_curve= swp_prc_tab.all_curves, tail = 1, curve_fill = "", p_dim=[800,300])
        self.curve_plot.extend([column(*fig1)])
        self.build_table()
        self.fwds_table()

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
            self.ivsp_df.value = ivsp_data
        self.update_notification.value = 'updated at: ' + datetime.datetime.now().strftime("%H:%M:%S")
        print("curve, df, fig: done")
        return

    def update_curve(self, event):
        self.build_curve(event)

    def view(self):
        return self.create_layout













#    def _update_fwd_row(self, event):
#        print('self.fwd_table.selection:', self.fwd_table.selection)
#        fwd_indices = self.fwd_table.selection
#        all_indices = self.curve_table.selection + self.fwd_table.selection
#        if len(all_indices) == 1:
#            new_df = self.fwd_data.iloc[int(fwd_indices[0])]
#            print(new_df)
#            a1 = [int(new_df['x1'].tolist()), int(new_df['x2'].tolist()),
#                  int(new_df['x3'].tolist()), int(new_df['x4'].tolist())]
#            print(a1)
#            fig2 = plot_tool_bbg([a1], self.curve)
#        else:
#            fig2 = pn.Row()
#        self.fwd_tab_plot.clear()
#        self.fwd_tab_plot.extend([column(*fig2)])
#        return













