import numpy as np
import sys
import os
import datetime
from dateutil.relativedelta import relativedelta
from scipy import stats
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
from OIS_DC_BUILD import ois_dc_build, get_wirp
from SWAP_BUILD import swap_build
from SWAP_PRICER import Swap_Pricer, Swap_curve_fwd, quick_swap
from SWAP_TABLE import swap_table, swap_table2, curve_hmap
from INF_ZC_BUILD import infl_zc_swap_build, Infl_ZC_Pricer, inf_swap_table
from BOND_CURVES import bond_curve_build
from VOL_BUILD import build_vol_surf, build_vol_spline, bond_fut_opt_strat, get_sim_option_px, build_stir_vol_surf, stir_opt_strat
from PLOT import plt_curve, plt_inf_curve, plt_opt_strat, rates_hm, curve_hm, plt_ois_curve, plot_opt_vol_surf, plt_stir_opt_strat, plotool, ecfc_plot
from PLOT_BOKEH import plt_ois_curve_bokeh, plt_inf_curve_bokeh, ecfc_plot, plot_tool_bbg, plot_wirp, plot_simple_wirp, plot_opt_vol_surf_bokeh, plt_opt_strat_bokeh, plot_tool_bbg_listed
from BOND_TABLES import linker_table
from INFL_CARRY import linker_carry_calc

con = pdblp.BCon(debug=False, port=8194, timeout=50000)
con.start()


class ListedTab(param.Parameterized):
    build_button = param.Action(lambda x: x.param.trigger('plot_button'), label='Build')
    reset_button = param.Action(lambda x: x.param.trigger('reset_button'), label='Reset')
    strat_button = param.Action(lambda x: x.param.trigger('strat_button'), label='Calc')
    plot_vol_button = param.Action(lambda x: x.param.trigger('plot_vol_button'), label='Plot Vol')
    plot_strat_hist_button = param.Action(lambda x: x.param.trigger('plot_strat_hist_button'), label='Plot Hist')

    def __init__(self):
        super(ListedTab, self).__init__()
        self.today = ql.Date(datetime.datetime.now().day, datetime.datetime.now().month, datetime.datetime.now().year)
        self.vol_surf = None
        self.c = ccy('SOFR_DC', self.today)
        pn.extension('tabulator')

        FUT_CT = {'1': 'F', '2': 'G', '3': 'H', '4': 'J', '5': 'K', '6': 'M', '7': 'N', '8': 'Q', '9': 'U', '10': 'V','11': 'X', '12': 'Z'}
        FUT_M = pd.DataFrame()
        d1 = ql.Date(15, self.today.month(), self.today.year())
        s1 = pd.Series([d1 + ql.Period(i, ql.Months) for i in range(12)])
        FUT_M['Date'] = pd.Series(s1.tolist())
        FUT_M['TickerMonth'] = pd.Series([FUT_CT[str(FUT_M['Date'][i].month())] + str(FUT_M['Date'][i].year())[-1:] for i in range(len(FUT_M))])
        FUT_M['BondMonth'] = pd.Series([True, True, True] + [any(x == FUT_M['TickerMonth'][i][0] for x in ['H', 'M', 'U', 'Z']) for i in np.arange(3, len(FUT_M))])
        t1 = [FUT_M['TickerMonth'][i] for i in np.arange(len(FUT_M))]
        self.ticker_list_bonds = ['FV', 'TY', 'US', 'WN', '1I', '2I', '3I', '4I', '5I', '1M', '2M', '3M', '4M', '5M', '1C','2C', '3C', '4C', '5C', '1J', '2J', '3J', '4J', '5J', 'DU', 'OE', 'RX', 'UB']
        self.ticker_list_stir = ['SFR', '0Q', '2Q', '3Q', '4Q', 'ER', '0R', '2R', '3R', '4R', 'SFI', '0N', '2N', '3N', '4N']
        self.ticker_list_all = self.ticker_list_bonds+self.ticker_list_stir
        self.strikes_list = [108, 110, 119, 125] + flat_lst([[i] * 5 for i in [108, 110, 119, 125]]) + [105.5, 117, 133, 133] + flat_lst([[i] * 5 for i in [96, 96, 96]])

        self.offset_dates = pn.widgets.TextInput(name='Offsets', value=str(-1), styles={'color': 'black', 'font-size': '8pt'}, width=120, height=30,margin=(5, 5, 10, 5))
        self.multi_select_ticker = pn.widgets.MultiSelect(name='Ticker', options=self.ticker_list_bonds+self.ticker_list_stir, size=8, styles={'color': 'black', 'font-size': '9pt'}, width=80, height=800, margin=(5, 20, 10, 10))
        self.multi_select_expiry = pn.widgets.MultiSelect(name='Expiry', options=t1, size=8, styles={'color': 'black', 'font-size': '9pt'}, width=70, height=800, margin=(5, 20, 10, 10))
        self.s_range = pn.widgets.TextInput(name='s_range [-1, 1]', value="[-1,1]",styles={'color': 'black', 'font-size': '8pt'}, width=100, height=30, margin=(5, 20, 10, 10), visible=False)
#        self.s_increm = pn.widgets.TextInput(name='s_increm [0.5]', value=str('not in use'), styles={'color': 'black', 'font-size': '8pt'}, width=100, height=30, margin=(5, 20, 10, 10), visible=False)
        self.add_delta = pn.widgets.TextInput(name='add_delta [-0.5, 135]', value="[0]",styles={'color': 'black', 'font-size': '8pt'}, width=100, height=30, margin=(5, 20, 10, 10), visible=False)

        #### outputs
        self.title_pane = pn.pane.Markdown("     ", style={'marginTop': '15px', 'marginLeft': '33px'})
        self.vol_tab = pn.Column()
        self.vol_plot_pane = pn.Card(title='Vol Surf', visible=False)
        self.strat_plot = pn.Card(title='Option Strat', visible=False)
        self.hist_plot_pane = pn.Card(title='History', visible=False)

    def create_layout(self):
        build_button = pn.widgets.Button(name='Build', button_type='primary', on_click=self.build_tab, width=180, height=30, margin=(20, 5, 10, 10), styles={'color': 'gray', 'font-size': '12pt'})
        reset_button = pn.widgets.Button(name='Reset', button_type='primary', on_click=self.reset_tab, width=180, height=30, margin=(20, 5, 10, 10), styles={'color': 'gray', 'font-size': '12pt'})
        strat_button = pn.widgets.Button(name='Calc', button_type='primary', on_click=self.strat_calc, width=180,height=30, margin=(20, 5, 10, 10), styles={'color': 'gray', 'font-size': '12pt'})
        plot_vol_button = pn.widgets.Button(name='Plot Vol', button_type='primary', on_click=self.vol_plot, width=180, height=30, margin=(20, 5, 10, 5), styles={'color': 'gray', 'font-size': '12pt'})
        plot_strat_hist_button = pn.widgets.Button(name='Plot Hist', button_type='primary', on_click=self.hist_plot, width=180, height=30, margin=(20, 5, 10, 5), styles={'color': 'gray', 'font-size': '12pt'})
        return pn.Column(
            pn.Row(build_button, self.title_pane, pn.Spacer(width=20), self.offset_dates, plot_vol_button, strat_button, plot_strat_hist_button, self.s_range, self.add_delta),
            pn.Row( pn.Column( pn.Row(self.multi_select_ticker, self.multi_select_expiry), reset_button), pn.Column(self.vol_tab ),
                   pn.Column( self.vol_plot_pane, pn.Spacer(height=15), self.strat_plot, pn.Spacer(height=15), self.hist_plot_pane )))

    def build_tab(self, event):
        self.vol_tab.clear()
        self.vol_plot_pane.clear()
        self.strat_plot.clear()
        self.hist_plot_pane.clear()
        self.vol_plot_pane.visible = False
        self.strat_plot.visible = False
        self.hist_plot_pane.visible = False
        self.strat_plot.title = "Option Strat"
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
        print("building opt_mon:")

        a1 = self.multi_select_ticker
        a2 = self.multi_select_expiry
        self.ticker = a1.value[0]+a2.value[0]+'P '+ str(self.strikes_list[self.ticker_list_all.index(a1.value[0])])
        print(self.ticker)
        if a1.value[0] in self.ticker_list_bonds:
            v1 = build_vol_surf([self.ticker], chain_len=[12, 12], b=0)
        else:
            v1 = build_stir_vol_surf([self.ticker], chain_len=[20, 20], b=0)
        self.vol_surf = v1
        self.title_pane.object = f""" ## {a1.value[0]+a2.value[0]+" :: "+
                                          ql_to_datetime(self.vol_surf.expiry_dt).strftime('%d-%b-%Y')+"   ::    "+
                                          str(np.round(v1.spot_px,2))+"    DTE:"+
                                          str(self.vol_surf.expiry_dt-self.today) } """
        print('vol surf build done')
        df1 = v1.tab[['strikes','px', 'px_64', 'Yld', 'ATM_K', 'bs_px', 'iv', 'delta', 'gamma']].round({'px':3, 'Yld':3, 'ATM_K':1, 'bs_px':4, 'iv':2, 'delta':1, 'gamma':2})
        df1['opt_type'] = [v1.tab['ticker'][i].split()[0][-1] for i in np.arange(len(v1.tab))]
        df1['unit'] = np.repeat(0,len(df1))
        df1 = df1[['opt_type','strikes', 'unit', 'px', 'px_64', 'Yld', 'ATM_K', 'bs_px', 'iv', 'delta', 'gamma']]
        tab1 = pn.widgets.Tabulator(df1, layout='fit_data', height=1000, width=703, stylesheets=[css2], show_index= False, groupby=['opt_type'])
        tab1.style.background_gradient(cmap="coolwarm_r",subset=df1.columns.str.contains("unit|strikes"))

        self.vol_tab.extend([tab1])
        self.s_range.visible = True
#        self.s_increm.visible = True
        self.add_delta.visible = True
        self.vol_plot_pane.visible = True
        self.strat_plot.visible = True
        self.hist_plot_pane.visible = True
        print("done!")
        return

    def strat_calc(self, event):
        self.strat_plot.clear()
        print("building strat:")
        b1 = self.multi_select_ticker
        b2 = self.multi_select_expiry

        b3 = self.s_range.value
        print('b3:', b3, type(b3))
        b3 = [ int(item.strip()) for item in b3.translate(str.maketrans({'[': '', ']': ''})).split(',')]
        print('b3:', b3, type(b3))
        b5 = self.add_delta.value
        b5 = [float(item.strip()) for item in b5.translate(str.maketrans({'[': '', ']': ''})).split(',')]
        print('b5:', b5)

        t = b1.value[0]+b2.value[0]
        mask = [i for i, e in enumerate(self.vol_tab[0].value['unit']) if e != 0]
        v_filter = self.vol_surf.tab.loc[mask,:]
        opt_t = [v_filter['ticker'][i].split()[0][-1] for i in mask]
        opt_s = v_filter['strikes'].tolist()
        opt_w = self.vol_tab[0].value['unit'].iloc[mask].tolist()
        delta_strat = np.round(np.dot(v_filter['delta'],opt_w),1)
        increm = self.vol_surf.tab['strikes'][1]-self.vol_surf.tab['strikes'][0]

        if b1.value[0] in self.ticker_list_bonds:
            osb = bond_fut_opt_strat(t, opt_t, opt_s, opt_w, s_range=b3, increm = increm, built_surf = self.vol_surf)
        else:
            osb = stir_opt_strat(t, opt_t, opt_s, opt_w, s_range=[-0.25, 0.25], increm=increm, built_surf=self.vol_surf)
        print(osb.strat)

        fig2 = plt_opt_strat_bokeh(osb, add_delta = b5 , payoff_increm_calc = 100)
        self.strat_plot.extend([column(*fig2)])
        if osb.type == 'USD':
            self.strat_plot.title = "Option Strat: "+t+opt_t[0]+'   :  '+' px: '+px_dec_to_opt_frac(osb.strat_px)+'   delta:   '+str(delta_strat)
        elif osb.type == 'stir':
            self.strat_plot.title = "Option Strat: " + t + opt_t[0] + '   :  ' + ' px: ' + str(np.round(100*osb.strat_px,2)) + '   delta:   ' + str(delta_strat)
        else:
            self.strat_plot.title = "Option Strat: " + t + opt_t[0] + '   :  ' + ' px: ' + str(np.round(osb.strat_px,3)) + '   delta:   ' + str(delta_strat)

        print("strat: done!")
        return

    def vol_plot(self, event):
        self.vol_plot_pane.clear()
        print("plotting vol_surf:")
        a1 = self.offset_dates.value
        b1 = self.multi_select_ticker
        if len(a1) != 0:
            a2 = [item.strip() for item in a1.split(',')]
            a3 = []
            for i in a2:
                if len(i) < 4:
                    a3 = a3 + [ql_to_datetime(self.c.cal.advance(self.today, ql.Period(str(i) + 'D'))).strftime('%d-%m-%Y')]
                else:
                    a3 = a3 + [datetime.datetime.strptime(i, '%d-%m-%Y').strftime('%d-%m-%Y')]
            print('dates: ', a3)
            print('ticker: ', self.ticker)
            if b1.value[0] in self.ticker_list_bonds:
                vol_surfs = [self.vol_surf] + [build_vol_surf([self.ticker], chain_len=[12, 12], b=j) for j in a3]
            else:
                vol_surfs = [self.vol_surf] + [build_stir_vol_surf([self.ticker], chain_len=[20, 20], b=j) for j in a3]
        else:
            vol_surfs = [self.vol_surf]
        fig1 = plot_opt_vol_surf_bokeh(vol_surfs)

        self.vol_plot_pane.extend([column(*fig1)])
        print("vol plot: done!")
        return

    def reset_tab(self,event):
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

        df2 = self.vol_tab[0].value
        df2['unit'] = np.repeat(0,len(df2))
        #        print(df2['unit'])
        tab2 = pn.widgets.Tabulator(df2, layout='fit_data', height=1000, width=703, stylesheets=[css2], show_index=False, groupby=['opt_type'])
        tab2.style.background_gradient(cmap="coolwarm_r", subset=df2.columns.str.contains("unit|strikes"))
#        self.vol_tab.clear()
#        self.vol_tab.extend([tab2])
        self.vol_tab.objects = [tab2]

    def hist_plot(self, event):
        self.hist_plot_pane.clear()
        print("collecting hist:")
        b1 = self.multi_select_ticker
        b2 = self.multi_select_expiry

        t = self.vol_surf.fut
        mask = [i for i, e in enumerate(self.vol_tab[0].value['unit']) if e != 0]
        v_filter = self.vol_surf.tab.loc[mask,:]
        print(v_filter)
        opt_w = self.vol_tab[0].value['unit'].iloc[mask].tolist()
        print(opt_w)

        fig3 = plot_tool_bbg_listed(v_filter, t, opt_w)
        self.hist_plot_pane.extend([fig3])

        print("hist: done!")
        return

    def view(self):
            return self.create_layout
