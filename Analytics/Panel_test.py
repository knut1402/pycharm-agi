import panel as pn
import pandas as pd
import hvplot.pandas
from bokeh.models.widgets.tables import NumberFormatter, BooleanFormatter
import sys
import os
import datetime
from dateutil.relativedelta import relativedelta
import param

sys.path.append(os.path.abspath("C:/Users/A00007579/PycharmProjects/pythonProject/Builds"))
sys.path.append(os.path.abspath("C:/Users/A00007579/PycharmProjects/pythonProject/Sundry"))
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
from BOND_TABLES import linker_table
from INFL_CARRY import linker_carry_calc
#from MINING import get_data, data_heatmap, run_gmm






class SwapMon:
    def __init__(self):
        today = ql.Date(datetime.datetime.now().day,datetime.datetime.now().month,datetime.datetime.now().year)
        self.curve = None
        c = ccy('SOFR_DC', today)
        pn.extension('tabulator')
        self.update_flag = param.Boolean(default=False)
        self.df_pane = param.DataFrame()

        self.curve_input = pn.widgets.Select(name='Curve', options=['SOFR_DC', 'ESTER_DC', 'SONIA_DC'], width=100, height=50, margin = (20, 20, 10, 10), styles={'color': 'blue', 'font-size': '12pt'})
        t = ql_to_datetime(today)
        self.date_input = pn.widgets.DatePicker(name='Date', value = t, styles={'color': 'black', 'font-size': '10pt'}, width=100, height=30, margin = (23, 20, 10, 10))
        t1 = ql_to_datetime( c.cal.advance(today,-1,ql.Days))
        self.offset_date = pn.widgets.DatePicker(name='Offset', value = t1, styles={'color': 'black', 'font-size': '10pt'}, width=100, height=30, margin = (23, 20, 10, 10))
        self.quick_dates = pn.widgets.Select(name='Quick Dates', options=['Live','1m', '3m', '6m', '1y'], styles={'color': 'black', 'font-size': '10pt'}, width=100, height=30, margin = (23, 20, 10, 10))
        self.auto_recalc_checkbox = pn.widgets.Checkbox(name='Auto-recal',width=100, height=30,  styles={'color': 'grey', 'font-size': '8pt'}, margin = (60, 20, 10, 10))
        self.auto_recalc_checkbox.param.watch(self.toggle_auto_update, 'value')

        self.update_notification = pn.widgets.StaticText(name='Status', value='df not yet updated')

        self.curve_input.param.watch(self.update_dataframe, 'value')
        self.date_input.param.watch(self.update_dataframe, 'value')
        self.offset_date.param.watch(self.update_dataframe, 'value')
        self.offset_date.param.watch(self.create_layout, 'value')
        #self.debug_text = pn.widgets.StaticText(name='Debug Info', value='')

        # Interactive table setup
        table_data = {'x1': [2, 2, 2], 'x2': [4, 9, 30], 'Rate': [0.0, 0.0, 0.0], '1m': [0.0, 0.0, 0.0],'3m': [0.0, 0.0, 0.0], '6m': [0.0, 0.0, 0.0], '1y': [0.0, 0.0, 0.0]}
        df_table = pd.DataFrame(table_data)
        # formatters = {cols: NumberFormatter(format='0.00') for cols in df_table.columns if df_table[cols].dtype == np.float64}
        self.calc_button = pn.widgets.Button(name='Calc', button_type='primary', width=50, height=30, margin=(10, 10, 0, 0), styles={'color': 'gray', 'font-size': '12pt'})
        self.interactive_table = pn.widgets.Tabulator(df_table, show_index=False)

        self.edited_rows = set()
        self.interactive_table.on_edit(self.on_table_edit)
        self.calc_button.on_click(self.update_tab)

        self.view = self.create_layout()

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

    @pn.depends('Curve','Date', 'Offset', watch = True)
    def update_dataframe(self, event = None):
        print("update_curve called with event:", event)
        self.update_notification.value = '........'
        a1 = self.date_input.value
        print(a1)
        a2 = self.offset_date.value
        print(a2)
        self.curve = ois_dc_build('SOFR_DC', b= a1.strftime('%d-%m-%Y'))
        self.df_pane = pn.pane.DataFrame(swap_table(self.curve, offset = [a2.strftime('%d-%m-%Y')]).table, index=False)
        fig1 = plt_ois_curve(['SOFR_DC'], h1=[0, a2.strftime('%d-%m-%Y')], max_tenor=30, bar_chg = 1, sprd = 0, name = '',fwd_tenor = '1d',int_tenor = '1m', tail = 1, curve_fill = "")
        fig1_pane = pn.pane.Matplotlib(fig1, width=550)
        self.update_notification.value = 'updated at: ' + datetime.datetime.now().strftime("%H:%M:%S")
        self.update_flag = not self.update_flag
        print("update df done")
        #self.debug_text.value = f"a5: {a5}"
        return pn.Row(self.df_pane, fig1_pane)


#        # Periodic callback function
#    def auto_update(self):
#        if self.auto_recalc_checkbox.value:
#            self.update_dataframe(self.curve_input.value, self.date_input.value)

    # Linking the checkbox to start/stop the periodic callback
    def toggle_auto_update(self,event):
        if event.new:
            pn.state.add_periodic_callback(auto_update, 120000)  # 120000 milliseconds = 2 minutes
        else:
            pn.state.remove_periodic_callback(auto_update)

#    self.auto_recalc_checkbox.param.watch(toggle_auto_update, 'value')




    # Callback for edits in the table
    def on_table_edit(event):
        self.edited_rows.add(event.row)

    # Callback function for the button
    def update_tab(event):
        for row_index in self.edited_rows:
            st_tn = int(self.interactive_table.value.loc[row_index, 'x1'])
            mt_tn = int(self.interactive_table.value.loc[row_index, 'x2'])#
            result = [Swap_Pricer([[self.curve,i,st_tn],[self.curve,i,mt_tn]]).table['Spread'][1] for i in [0, '1M', '3M', '6M', 1]]
            self.interactive_table.value.at[row_index, 'Rate'] = np.round(result[0],1)
            self.interactive_table.value.at[row_index, '1m'] = np.round(result[1],1)
            self.interactive_table.value.at[row_index, '3m'] = np.round(result[2],1)
            self.interactive_table.value.at[row_index, '6m'] = np.round(result[3],1)
            self.interactive_table.value.at[row_index, '1y'] = np.round(result[4],1)

        self.edited_rows.clear()  # Clear the set after updating
        self.interactive_table.value = self.interactive_table.value  # Refresh the table

    @pn.depends('df_pane', watch=True)
    def create_layout(self, event=None):
        print("update_layout called with event:", event, self.df_pane)
        return pn.Column(
            pn.Row(self.curve_input, self.quick_dates, self.date_input, self.offset_date, self.auto_recalc_checkbox),
            self.update_dataframe(),
            self.update_notification,
            pn.Row(pn.pane.Markdown("## Curves"), self.calc_button),
            self.interactive_table)












class Quix2:
    def __init__(self):
        self.SwapMonitor = SwapMon()
        # Initialize other tabs (placeholders for this example)
        self.other_tab_1 = pn.pane.Markdown("## Other Tab 1 Content")
        self.other_tab_2 = pn.pane.Markdown("## Other Tab 2 Content")

        # Combine all tabs into a Tabs layout
        self.tabs = pn.Tabs(
            ('Swap Monitor', self.SwapMonitor.view),
            ('Swap Fwds', self.other_tab_1),
            ('Swap HM', self.other_tab_2)
        )
    def servable(self):
        return self.tabs.servable()

main_q = Quix2()
main_q.servable()
