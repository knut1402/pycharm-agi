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
        self.multi_select_data = pn.widgets.MultiSelect(name='Data', options=list1, size=8, styles={'color': 'black', 'font-size': '8pt'}, width=100, height=300, margin=(5, 20, 10, 10))
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
