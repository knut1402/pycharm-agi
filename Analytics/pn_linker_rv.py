import numpy as np
import panel as pn
import inspect
import pandas as pd
import hvplot.pandas
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

class LinkerRV(param.Parameterized):
    plot_button = param.Action(lambda x: x.param.trigger('plot_button'), label='Plot')

    def __init__(self):
        super(LinkerRV, self).__init__()  # Initialize the param.Parameterized base class
        today = ql.Date(datetime.datetime.now().day, datetime.datetime.now().month, datetime.datetime.now().year)
        c = ccy('SONIA_DC', today)

        self.linkers = ['GB00BYY5F144', 'GB00B128DH60', 'GB00BZ1NTB69', 'GB00B3Y1JG82', 'GB0008932666', 'GB00BNNGP551',
                        'GB00B3D4VD98', 'GB00BMF9LJ15', 'GB00B46CGH68', 'GB0031790826', 'GB00BYZW3J87', 'GB00B1L6W962',
                        'GB00BLH38265', 'GB00B3LZBF68', 'GB00BGDYHF49', 'GB00B3MYD345', 'GB00B7RN0G65', 'GB00BMF9LH90',
                        'GB00BYMWG366', 'GB00B24FFM16', 'GB00BZ13DV40', 'GB00B421JZ66', 'GB00BNNGP882', 'GB00B73ZYW09',
                        'GB00B0CNHZ09', 'GB00BYVP4K94', 'GB00BP9DLZ64', 'GB00B4PTCY75', 'GB00BD9MZZ71', 'GB00BDX8CX86',
                        'GB00BM8Z2W66']

        self.comparators = ['GB00BL68HJ26', 'GB00BDRHNP05', 'GB00BMBL1G81', 'GB00BLPK7227', 'GB00B24FF097', 'GB0004893086',
                            'GB0004893086', 'GB0004893086', 'GB00B52WS153', 'GB0032452392', 'GB0032452392', 'GB00BZB26Y51',
                            'GB00BJQWYH73', 'GB00BJQWYH73', 'GB00BJQWYH73', 'GB00B1VWPJ53', 'GB00B84Z9V04', 'GB00BNNGP775',
                            'GB00BDCHBW80', 'GB00BDCHBW80', 'GB00BMBL1F74', 'GB00BMBL1F74', 'GB00BLH38158', 'GB00B6RNH572',
                            'GB00B06YGN05', 'GB00BD0XH204', 'GB00B54QLM75', 'GB00BMBL1D50', 'GB00BYYMZX75', 'GB00BFMCN652',
                            'GB00BLBDX619']

        self.linkers = [self.linkers[i] + ' Govt' for i in np.arange(len(self.linkers))]
        self.comparators = [self.comparators[i] + ' Govt' for i in np.arange(len(self.comparators))]

        self.options_list = con.ref( self.linkers, 'SECURITY_NAME').set_index('ticker').loc[self.linkers]['value'].tolist()
        self.layout_pane = pn.Column()
        self.multi_select = pn.widgets.MultiSelect(name='Curves', options=self.options_list, size=6, styles={'color': 'black', 'font-size': '8pt'}, width=200, height=800, margin=(5, 20, 10, 10))

        t = ql_to_datetime(today)
        self.date_input = pn.widgets.DatePicker(name='Date', value=t, styles={'color': 'black', 'font-size': '8pt'}, width=100, height=30, margin=(20, 20, 10, 10))
        self.offset_dates = pn.widgets.TextInput(name='Offsets', value='-1y',  styles={'color': 'black', 'font-size': '8pt'}, width=120, height=30, margin=(20, 20, 10, 10))
        self.comparator_notification = pn.widgets.StaticText(name='Comparators:', value='')


    def create_layout(self):
        plot_button = pn.widgets.Button(name='Plot', button_type='primary', on_click=self.build_plot, width=120, height=30, margin=(20, 5, 10, 10), styles={'color': 'gray', 'font-size': '12pt'})
        return pn.Column(
            pn.Row(self.date_input, self.offset_dates),
            pn.Row(plot_button),
            pn.Row(self.multi_select, self.layout_pane),
            pn.Row(self.comparator_notification) )

    def build_plot(self, event):
        self.layout_pane.clear()
        print("building plot:")
#        self.update_notification.value = '........'
        a1 = self.multi_select
        a2 = self.date_input
        a3 = self.offset_dates
#        a4 = self.max_tenor
        print(a1.value, type(a1.value))
        print(a2.value.strftime('%Y%m%d'), type(a2.value))
        print(a3.value, type(a3.value))

        if len(a1.value) == 1:
            m1 = 'ry'
            t11 = 'Yields'
            t12 = 'Breakeven'
            t13 = 'Z-Score: BEI'
            t21 = 'Z-Spread'
            t22 = 'Rel Z-Spread'
            t23 = 'Z-Score: Rel Z-Spread'
        elif len(a1.value) == 2:
            m1 = 'spread'
            t11 = 'Curve'
            t12 = 'Curve Spread'
            t13 = 'Z-Score: Curve'
            t21 = 'Z-Spread: Curve'
            t22 = 'Rel Z-Spread'
            t23 = 'Z-Score: Rel Z-Spread'
        elif len(a1.value) == 3:
            m1 = 'fly'
            t11 = 'Fly'
            t12 = 'Fly Spread'
            t13 = 'Z-Score: Fly'
            t21 = 'Z-Spread: Fly'
            t22 = 'Rel Z-Spread'
            t23 = 'Z-Score: Rel Z-Spread'

        start_dt = bbg_date_str(ql.UnitedKingdom().advance( datetime_to_ql(a2.value), ql.Period(a3.value)))
        linker_feed = a1.value
        feed = [self.options_list.index(linker_feed[i]) for i in np.arange(len(linker_feed))]
        linker__isin_feed = list(np.array(self.linkers)[feed])
        comp_feed = list(np.array(self.comparators)[feed])

        comp_name = con.ref(comp_feed, 'SECURITY_NAME').set_index('ticker').loc[comp_feed]['value'].tolist()
        self.comparator_notification.value = [comp_name[j] for j in np.arange(len(comp_name))]

        df1 = con.bdh(linker__isin_feed , ['YLD_YTM_MID', 'Z_SPRD_MID'], start_dt, a2.value.strftime('%Y%m%d'))
        df2 = con.bdh(comp_feed, ['YLD_YTM_MID', 'Z_SPRD_MID'], start_dt, a2.value.strftime('%Y%m%d'))

        ry = get_linker_metrics(df1, linker__isin_feed, m=m1)
        nom = get_linker_metrics(df2, comp_feed, m=m1)

        df_comb = pd.DataFrame()
        df_comb[m1] = nom[m1] - ry[m1]
        df_comb['z_sprd'] = nom[m1+'z_sprd'] - ry[m1+'z_sprd']
        df_comb['z_score_1m'] = roll_zscore(df_comb[m1], 20)
        df_comb['z_score_3m'] = roll_zscore(df_comb[m1], 60)
        df_comb['z_score_6m'] = roll_zscore(df_comb[m1], 180)
        df_comb['rel_z_z_score_1m'] = roll_zscore(df_comb['z_sprd'], 20)
        df_comb['rel_z_z_score_3m'] = roll_zscore(df_comb['z_sprd'], 60)
        df_comb['rel_z_z_score_6m'] = roll_zscore(df_comb['z_sprd'], 180)

        s1 = figure(title=t11, width=550, height=300, tools=["pan", "tap", "wheel_zoom", "box_zoom", "save", "reset", "help"], toolbar_location='left')
        s1.xaxis.formatter = DatetimeTickFormatter(days="%d-%b-%y", months="%d-%b-%y")
        s1.add_tools(HoverTool(tooltips=[('date', '$x{%d.%b.%y}'), ('y', '$y{0.0}')], formatters={'$x': 'datetime'}))
        s1.xgrid.visible = False
        s1.ygrid.visible = False
        s1.line(x=ry['date'], y=ry[m1], line_width=0.9, color='lightsteelblue', muted_alpha=0.1, legend_label="RY "+m1)
        s1.line(x=nom['date'], y=nom[m1], line_width=0.9, color='sandybrown', muted_alpha=0.1, legend_label="Nom "+m1)
        s1.xaxis.visible = False
        s1.legend.location = 'top_left'
        s1.legend.label_text_font = "calibri"
        s1.legend.label_text_font_size = "9pt"
        s1.legend.spacing = 1
        s1.legend.click_policy = "mute"
        s1.legend.background_fill_alpha = 0.0

        s2 = figure(title=t12, width=550, height=350, tools=["pan", "tap", "wheel_zoom", "box_zoom", "save", "reset", "help"], toolbar_location='left')
        s2.xaxis.formatter = DatetimeTickFormatter(days="%d-%b-%y", months="%d-%b-%y")
        s2.add_tools(HoverTool(tooltips=[('date', '$x{%d.%b.%y}'), ('y', '$y{0.0}')], formatters={'$x': 'datetime'}))
        s2.xgrid.visible = False
        s2.ygrid.visible = False
        s2.line(x=ry['date'], y=df_comb[m1], line_width=0.7, color='firebrick', alpha=0.8)
        s2.xaxis.major_label_orientation = math.pi / 4

        s3 = figure(title=t13, width=550, height=200, tools=["pan", "tap", "wheel_zoom", "box_zoom", "save", "reset", "help"], toolbar_location='left')
        s3.xaxis.formatter = DatetimeTickFormatter(days="%d-%b-%y", months="%d-%b-%y")
        s3.add_tools(HoverTool(tooltips=[('date', '$x{%d.%b.%y}'), ('y', '$y{0.0}')], formatters={'$x': 'datetime'}))
        s3.xgrid.visible = False
        s3.ygrid.visible = False
        s3.line(x=ry['date'], y=df_comb['z_score_3m'], line_width=0.6, color='indigo', alpha=0.8, legend_label="z_score: 3m")
        s3.line(x=ry['date'], y=df_comb['z_score_6m'], line_width=0.6, color='green', alpha=0.8, legend_label="z_score: 6m")
        zero_line = Span(location=0, dimension='width', line_color='darkslategray', line_width=1)
        s3.renderers.extend([zero_line])
        s3.xaxis.visible = False
        s3.legend.location = 'top_left'
        s3.legend.label_text_font = "calibri"
        s3.legend.label_text_font_size = "9pt"
        s3.legend.spacing = 1
        s3.legend.click_policy = "mute"
        s3.legend.background_fill_alpha = 0.0

        s4 = figure(title=t21, width=550, height=300, tools=["pan", "tap", "wheel_zoom", "box_zoom", "save", "reset", "help"], toolbar_location='right')
        s4.xaxis.formatter = DatetimeTickFormatter(days="%d-%b-%y", months="%d-%b-%y")
        s4.add_tools(HoverTool(tooltips=[('date', '$x{%d.%b.%y}'), ('y', '$y{0.0}')], formatters={'$x': 'datetime'}))
        s4.xgrid.visible = False
        s4.ygrid.visible = False
        s4.line(x=ry['date'], y=ry[m1+'z_sprd'], line_width=0.9, color='lightsteelblue', legend_label="UKTi")
        s4.line(x=nom['date'], y=nom[m1+'z_sprd'], line_width=0.8, color='sandybrown', legend_label="UKT")
        s4.xaxis.visible = False
        s4.legend.location = 'top_left'
        s4.legend.label_text_font = "calibri"
        s4.legend.label_text_font_size = "9pt"
        s4.legend.spacing = 1
        s4.legend.click_policy = "mute"
        s4.legend.background_fill_alpha = 0.0

        s5 = figure(title=t22, width=550, height=350, tools=["pan", "tap", "wheel_zoom", "box_zoom", "save", "reset", "help"], toolbar_location='right')
        s5.xaxis.formatter = DatetimeTickFormatter(days="%d-%b-%y", months="%d-%b-%y")
        s5.add_tools(HoverTool(tooltips=[('date', '$x{%d.%b.%y}'), ('y', '$y{0.0}')], formatters={'$x': 'datetime'}))
        s5.xgrid.visible = False
        s5.ygrid.visible = False
        s5.line(x=ry['date'], y=df_comb['z_sprd'], line_width=0.7, color='firebrick', alpha=0.8)
        s5.xaxis.major_label_orientation = math.pi / 4

        s6 = figure(title=t23, width=550, height=200, tools=["pan", "tap", "wheel_zoom", "box_zoom", "save", "reset", "help"], toolbar_location='right')
        s6.xaxis.formatter = DatetimeTickFormatter(days="%d-%b-%y", months="%d-%b-%y")
        s6.add_tools(HoverTool(tooltips=[('date', '$x{%d.%b.%y}'), ('y', '$y{0.0}')], formatters={'$x': 'datetime'}))
        s6.xgrid.visible = False
        s6.ygrid.visible = False
        s6.line(x=ry['date'], y=df_comb['rel_z_z_score_3m'], line_width=0.6, color='indigo', alpha=0.8, muted_alpha=0.1, legend_label="z_score: 3m")
        s6.line(x=ry['date'], y=df_comb['rel_z_z_score_6m'], line_width=0.6, color='green', alpha=0.8, muted_alpha=0.1, legend_label="z_score: 6m")
        zero_line = Span(location=0, dimension='width', line_color='darkslategray', line_width=1)
        s6.renderers.extend([zero_line])
        s6.xaxis.visible = False
        s6.legend.location = 'top_left'
        s6.legend.label_text_font = "calibri"
        s6.legend.label_text_font_size = "9pt"
        s6.legend.spacing = 1
        s6.legend.click_policy = "mute"
        s6.legend.background_fill_alpha = 0.0

        p = layout(children=[[s1, s4], [s2, s5], [s3, s6]])
        self.layout_pane.extend([p])
        print("done!")
        return

    def view(self):
            return self.create_layout

