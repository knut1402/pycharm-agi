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
from PLOT_BOKEH import swap_heatmap
from BOND_TABLES import linker_table
from INFL_CARRY import linker_carry_calc


con = pdblp.BCon(debug=False, port=8194, timeout=50000)
con.start()

class SwapHeatMap(param.Parameterized):
    plot_button = param.Action(lambda x: x.param.trigger('plot_button'), label='Calc')

    def __init__(self):
        super(SwapHeatMap, self).__init__()  # Initialize the param.Parameterized base class
        today = ql.Date(datetime.datetime.now().day, datetime.datetime.now().month, datetime.datetime.now().year)
        c = ccy('SOFR_DC', today)

        options_list = ['SOFR_DC', 'ESTER_DC', 'SONIA_DC', 'AONIA_DC', 'CORRA_DC']
        self.layout_pane = pn.Column()
        self.multi_select = pn.widgets.MultiSelect(name='Curves', options=options_list, size=6, styles={'color': 'black', 'font-size': '8pt'}, width=120, height=800, margin=(5, 20, 10, 10))

        t = ql_to_datetime(today)
        self.date_input = pn.widgets.DatePicker(name='Date', value=t, styles={'color': 'black', 'font-size': '8pt'}, width=100, height=30, margin=(20, 20, 10, 10))
        self.offset_dates = pn.widgets.TextInput(name='Offsets ', value='-1',  styles={'color': 'black', 'font-size': '8pt'}, width=120, height=30, margin=(20, 20, 10, 10))
        self.ois_flag = pn.widgets.Checkbox(name='OIS:', value=True, styles={'color': 'black', 'font-size': '9pt'}, width=100, height=30, margin=(50, 10, 0, 10))
        self.z_offset = pn.widgets.TextInput(name='Offset', value='0',styles={'color': 'black', 'font-size': '8pt'}, width=50, height=30, margin=(20, 20, 10, 10))
        self.z_roll = pn.widgets.TextInput(name='Roll [1M, 3M, 6M, 1]', value='3M, 6M', styles={'color': 'black', 'font-size': '8pt'}, width=100, height=30, margin=(20, 20, 10, 10))

    def create_layout(self):
        plot_button = pn.widgets.Button(name='Calc', button_type='primary', on_click=self.build_plot, width=120, height=30, margin=(5, 5, 10, 10), styles={'color': 'gray', 'font-size': '12pt'})
        return pn.Column(
            pn.Row(self.date_input, self.offset_dates, self.z_offset, self.z_roll, self.ois_flag),
            pn.Row(plot_button),
            pn.Row(self.multi_select, self.layout_pane) )

    def build_plot(self, event):
        self.layout_pane.clear()
        print("building heatmap:")
        a1 = self.multi_select
        a2 = self.date_input
        a3 = self.offset_dates
        a4 = self.ois_flag
        a5 = self.z_offset
        a6 = self.z_roll
        print(a1.value, type(a1.value))
        print(a2.value, type(a2.value))
        print(a3.value, type(a3.value))
        print(a4.value, type(a4.value))
        print(a5.value, type(a5.value))
        print(a6.value, type(a6.value))
        b1 = a6.value
        b2 = [item.strip() for item in b1.split(',')]
        b3 = []
        for i in b2:
            if len(i) == 2:
                b3.append(i)
            else:
                b3.append(int(i))
        b4 = [a3.value]
        b5 = []
        for i in b4:
            if len(i) < 4:
                b5 = b5 + [int(i)]
            else:
                b5 = b5 + [i]

        fig1 = swap_heatmap(a1.value, b= a2.value.strftime('%d-%m-%Y'), offset = b5, ois_flag = int(a4.value), z_offset = int(a5.value), z_roll = b3)
        self.layout_pane.extend([fig1])
        print("done!")
        return

    def view(self):
            return self.create_layout

