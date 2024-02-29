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
from OIS_DC_BUILD import ois_dc_build, get_wirp
from SWAP_BUILD import swap_build
from SWAP_PRICER import Swap_Pricer, Swap_curve_fwd, quick_swap
from SWAP_TABLE import swap_table, swap_table2, curve_hmap
from INF_ZC_BUILD import infl_zc_swap_build, Infl_ZC_Pricer, inf_swap_table
from BOND_CURVES import bond_curve_build
from VOL_BUILD import build_vol_surf, build_vol_spline, bond_fut_opt_strat, get_sim_option_px, build_stir_vol_surf, stir_opt_strat
from PLOT import plt_curve, plt_inf_curve, plt_opt_strat, rates_hm, curve_hm, plt_ois_curve, plot_opt_vol_surf, plt_stir_opt_strat, plotool, ecfc_plot
from PLOT_BOKEH import plt_ois_curve_bokeh, plt_inf_curve_bokeh, ecfc_plot, plot_tool_bbg, plot_wirp
from BOND_TABLES import linker_table
from INFL_CARRY import linker_carry_calc
#from MINING import get_data, data_heatmap, run_gmm


con = pdblp.BCon(debug=False, port=8194, timeout=50000)
con.start()

class WirpPlot(param.Parameterized):
    plot_button = param.Action(lambda x: x.param.trigger('plot_button'), label='Plot')

    def __init__(self):
        super(WirpPlot, self).__init__()  # Initialize the param.Parameterized base class
        today = ql.Date(datetime.datetime.now().day, datetime.datetime.now().month, datetime.datetime.now().year)
        self.c = ccy('SOFR_DC', today)

        options_list = ['SOFR_DC', 'ESTER_DC', 'SONIA_DC']
        self.layout_pane = pn.Column()
        self.multi_select = pn.widgets.MultiSelect(name='Curves', options=options_list, size=6, styles={'color': 'black', 'font-size': '8pt'}, width=120, height=800, margin=(5, 20, 10, 10))
        self.offset_dates = pn.widgets.TextInput(name='Offsets [latest -> earliest]', value=ql_to_datetime( self.c.cal.advance(today, ql.Period('0D'), ql.Preceding) ).strftime('%d-%m-%Y'),  styles={'color': 'black', 'font-size': '8pt'}, width=350, height=30, margin=(20, 20, 10, 10))
        self.changes = pn.widgets.Checkbox(name='Chg', value=False, styles={'color': 'black', 'font-size': '8pt'}, width=50, height=30, margin=(20, 2, 10, 10))
        self.generic = pn.widgets.Checkbox(name='Gen', value=False, styles={'color': 'black', 'font-size': '8pt'}, width=50, height=30, margin=(20, 10, 10, 2))

    def create_layout(self):
        plot_button = pn.widgets.Button(name='Calc', button_type='primary', on_click=self.build_plot, width=120, height=30, margin=(10, 5, 10, 10), styles={'color': 'gray', 'font-size': '12pt'})
        return pn.Column(
            pn.Row(self.offset_dates ),
            pn.Row(plot_button, self.changes, self.generic),
            pn.Row(self.multi_select, self.layout_pane) )

    def build_plot(self, event):
        today = ql.Date(datetime.datetime.now().day, datetime.datetime.now().month, datetime.datetime.now().year)
        self.layout_pane.clear()
        print("building plot:")
        a1 = self.multi_select
        a2 = self.offset_dates
        a3 = self.changes
        a4 = self.generic
        b2 = a2.value
        b3 = [item.strip() for item in b2.split(',')]
        b4 = []
        for i in b3:
            if len(i) < 4:
                b4 = b4 + [ql_to_datetime(self.c.cal.advance(today, ql.Period(str(i)+'D')))]
            else:
                b4 = b4 + [datetime.datetime.strptime(i, '%d-%m-%Y')]
        print(b4)
        print('b4_type:', type(b4[0]))

        df = get_wirp( [a1.value, b4])
        fig1 = plot_wirp(df, chg=a3.value, gen=a4.value, dates=b4)
        self.layout_pane.extend([fig1])
        print("done!")
        return

    def view(self):
            return self.create_layout

