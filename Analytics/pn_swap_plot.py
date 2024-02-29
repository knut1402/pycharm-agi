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

class SwapPlot(param.Parameterized):
    plot_button = param.Action(lambda x: x.param.trigger('plot_button'), label='Plot')

    def __init__(self):
        super(SwapPlot, self).__init__()  # Initialize the param.Parameterized base class
        today = ql.Date(datetime.datetime.now().day, datetime.datetime.now().month, datetime.datetime.now().year)
        c = ccy('SOFR_DC', today)

        options_list = ['SOFR_DC', 'ESTER_DC', 'SONIA_DC']
        self.layout_pane = pn.Column()
        self.multi_select = pn.widgets.MultiSelect(name='Curves', options=options_list, size=6, styles={'color': 'black', 'font-size': '8pt'}, width=120, height=800, margin=(5, 20, 10, 10))

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
        plot_button = pn.widgets.Button(name='Calc', button_type='primary', on_click=self.build_plot, width=120, height=30, margin=(20, 5, 10, 10), styles={'color': 'gray', 'font-size': '12pt'})
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
        fig1 = plt_ois_curve_bokeh(a1.value, h1=b4, max_tenor=int(a3.value), bar_chg=int(a4.value), sprd=int(a5.value), name='', fwd_tenor=a6.value, int_tenor=a7.value, tail=1, curve_fill="", label_curve_name=1, p_dim=[1000,600])
        self.layout_pane.extend([column(*fig1)])
        print("done!")
        return

    def view(self):
            return self.create_layout

