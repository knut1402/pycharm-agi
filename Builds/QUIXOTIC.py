#################           QUIXOTIC - tkinter Class implementation         ######################
##################################################################################################

import os
import pandas as pd
import numpy as np
import tkinter as tk
from tkinter import ttk
import ttkthemes
from ttkthemes import ThemedTk

import math
import datetime
#import tia
#from tia.bbg import LocalTerminal as LT
import pdblp
import eikon as ek
import runpy
import QuantLib as ql
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import minmax_scale
from tabulate import tabulate
from pandastable import Table, TableModel
import pickle
import re

from matplotlib import style
import mplcursors
#style.use("ggplot")
mpl.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

LARGE_FONT = ("Verdana", 10)

con = pdblp.BCon(debug=False, port=8194, timeout=50000)
con.start()

os.chdir('C:\\Users\A00007579\OneDrive - Allianz Global Investors\Documents\Python archive\Swaps') 
from Utilities import *
from Conventions import FUT_CT,FUT_CT_Q, ccy, ccy_infl
from OIS_DC_BUILD import ois_dc_build
from SWAP_BUILD import swap_build
from SWAP_PRICER import Swap_Pricer
from SWAP_TABLE import swap_table, curve_hmap, swap_table2
from INF_ZC_BUILD import infl_zc_swap_build, Infl_ZC_Pricer, inf_swap_table
from VOL_BUILD import build_vol_surf, build_vol_spline, bond_fut_opt_strat, get_sim_option_px, build_stir_vol_surf, stir_opt_strat
from PLOT import plt_curve, plt_inf_curve, plt_opt_strat, rates_hm, curve_hm, plt_ois_curve, plot_opt_vol_surf, plt_stir_opt_strat, plotool, ecfc_plot
from BOND_TABLES import linker_table
from INFL_CARRY import linker_carry_calc
from BOND_CURVES import bond_curve_build

#eikon_app_key= '6ccde6df4ee247cea42850581c08b61c4126f047'
#ek.set_app_key(eikon_app_key)
#from SWAPTION import Swaption_Pricer, Swaption_Curve, usd_volc, gbp_volc, usd_volc_sofr     #### req eikon




class Quix(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
#        tk.Tk.iconbitmap(self, default = 'ico')
        self.geometry("1800x1200")
        tk.Tk.wm_title(self, "Quixotic")

#        s = ttk.Style()
#        s.theme_use('default')
#        s.configure('TNotebook.Tab', background="red")
#        s.map("TNotebook", background= [("selected", "blue")])
        
        container = ScrollableNotebook(self)
        container.grid(row=0, column=0)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        ##### List of Tabs
        container.add(FundSizer(container), text='Fund Sizing')
#        container.add(SwapMon1(container), text='Swap Monitor')
        container.add(Eco(container), text='Eco')        
        container.add(Plotter(container), text='Plotool')
        container.add(SwapMon(container), text='Swap Monitor')
        container.add(InfSwapMon(container), text='Inflation Swap Monitor')
        container.add(SwapPricer(container), text='Swap Pricer')
        container.add(SwapFwds(container), text='Swap Fwds')
        container.add(SwapCrvs(container), text='Swap Curves')
        container.add(SwapRV(container), text='Swap RV')
        container.add(SwapHM(container), text='Swap Heatmap')
        container.add(SwaptionCurve(container), text='Swaption Curve')
        container.add(SwaptionPricer(container), text='Swaption Pricer')
        container.add(OptChain(container), text='Option Chain')
        container.add(OptStrat(container), text='Option Strat')
        container.add(OptVol(container), text='Option Vol')
        container.add(BFStrikes(container), text='Bond Futures Strikes')
        container.add(InfFix(container), text='Inflation Fixings')
        container.add(InfSwapPricer(container), text='Inflation Swap Pricer')
        container.add(InfMon1(container), text='Inflation Monitor')
        container.add(BondCurves(container), text='Bond Curves')

        container.pack(expand = 1, fill ="both")
        
class ScrollableNotebook(ttk.Frame):
    def __init__(self,parent,*args,**kwargs):
        ttk.Frame.__init__(self, parent, *args)
        self.xLocation = 0
        self.notebookContent = ttk.Notebook(self,**kwargs)
        self.notebookContent.pack(fill="both", expand=True)

        self.notebookTab = ttk.Notebook(self,**kwargs)
        self.notebookTab.bind("<<NotebookTabChanged>>",self._tabChanger)

        slideFrame = ttk.Frame(self)
        slideFrame.place(relx=1.0, x=0, y=1, anchor=tk.NE)
        leftArrow = ttk.Label(slideFrame, text="\u25c0")
        leftArrow.bind("<1>",self._leftSlide)
        leftArrow.pack(side=tk.LEFT)
        rightArrow = ttk.Label(slideFrame, text=" \u25b6")
        rightArrow.bind("<1>",self._rightSlide)
        rightArrow.pack(side=tk.RIGHT)
        self.notebookContent.bind( "<Configure>", self._resetSlide)

    def _tabChanger(self,event):
        self.notebookContent.select(self.notebookTab.index("current"))

    def _rightSlide(self,event):
        if self.notebookTab.winfo_width()>self.notebookContent.winfo_width()-30:
            if (self.notebookContent.winfo_width()-(self.notebookTab.winfo_width()+self.notebookTab.winfo_x()))<=35:
                self.xLocation-=20
                self.notebookTab.place(x=self.xLocation,y=0)
    def _leftSlide(self,event):
        if not self.notebookTab.winfo_x()== 0:
            self.xLocation+=20
            self.notebookTab.place(x=self.xLocation,y=0)

    def _resetSlide(self,event):
        self.notebookTab.place(x=0,y=0)
        self.xLocation = 0

    def add(self,frame,**kwargs):
        if len(self.notebookTab.winfo_children())!=0:
            self.notebookContent.add(frame, text="",state="hidden")
        else:
            self.notebookContent.add(frame, text="")
        self.notebookTab.add(ttk.Frame(self.notebookTab),**kwargs)

    def forget(self,tab_id):
        self.notebookContent.forget(tab_id)
        self.notebookTab.forget(tab_id)

    def hide(self,tab_id):
        self.notebookContent.hide(tab_id)
        self.notebookTab.hide(tab_id)

    def identify(self,x, y):
        return self.notebookTab.identify(x,y)

    def index(self,tab_id):
        return self.notebookTab.index(tab_id)

    def insert(self,pos,frame, **kwargs):
        self.notebookContent.insert(pos,frame, **kwargs)
        self.notebookTab.insert(pos,frame,**kwargs)

    def select(self,tab_id):
        self.notebookContent.select(tab_id)
        self.notebookTab.select(tab_id)

    def tab(self,tab_id, option=None, **kwargs):
        return self.notebookTab.tab(tab_id, option=None, **kwargs)

    def tabs(self):
        return self.notebookContent.tabs()

    def enable_traversal(self):
        self.notebookContent.enable_traversal()
        self.notebookTab.enable_traversal()        
        

class FundSizer(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)
        
        label = ttk.Label(self, text = "Fund Sizing Monitor", font = LARGE_FONT)
        label.grid(row = 0, column = 0, columnspan = 5, sticky = 'W')
        
        FSInsttype = ttk.Label(self, text = 'Instr Type')
        FSInsttype.grid(row = 4, column = 0 , sticky = 'W')
        
        FSTicker = ttk.Label(self, text = 'Ticker')
        FSTicker.grid(row = 4, column = 1 , sticky = 'W')
        
        m1 = tk.StringVar(self)
        FSHeading = ttk.Combobox(self, width = 15, textvariable = m1, name = 'headingselect')
        FSHeading['values'] =  ('FX', 'Bond Futures', 'Index Futures','Options', 'Bonds', 'Generic')
        FSHeading.grid(row = 3, column = 1, columnspan = 1, sticky = 'W')
        
        n_maxrows = 15
        n_maxrows = [str(i) for i in np.arange(n_maxrows)]
        dict_rows = dict([(key, []) for key in n_maxrows ])
        dict_tickers = dict([(key, []) for key in n_maxrows ])
        
        for i in n_maxrows:
            m2 = tk.StringVar(self)
            instselect = ttk.Combobox(self, width = 10, textvariable = m2, name = 'instselect'+'_'+i )
            instselect['values'] = ('FX', 'Bond Futures', 'Index Futures','Options', 'Bonds', 'Generic')
            instselect.grid(row = 5+int(i), column = 0)
            dict_rows[i].append(instselect)
            
            e = tk.Entry(self, width=20, name = 'ticker_'+i , bg='beige', relief = 'flat', border = 2)
            e.grid(row= 5+int(i), column=1, sticky='W')
            dict_tickers[i].append(e)
            
            c1 = tk.Entry(self, width=10, name = 'c1_'+i , relief = 'flat', border = 2)
            c1.grid(row= 5+int(i), column=2, sticky='W')
            dict_tickers[i].append(c1)
            
            c2 = tk.Entry(self, width=10, name = 'c2_'+i , relief = 'flat', border = 2)
            c2.grid(row= 5+int(i), column=3, sticky='W')
            dict_tickers[i].append(c2)
            
            c3 = tk.Entry(self, width=10, name = 'c3_'+i , bg='light blue', relief = 'flat', border = 2)
            c3.grid(row= 5+int(i), column=4, sticky='W')
            dict_tickers[i].append(c3)
            
        n_maxcols = 4
        n_maxcols = [str(i) for i in np.arange(n_maxcols)]
        dict_cols = dict([(key, []) for key in n_maxcols ])
        for i in n_maxcols:
            m3 = tk.StringVar(self)
            fundselect = ttk.Combobox(self, width = 27, textvariable = m3, name = 'fundselect'+'_'+i )
            fundselect['values'] = ('L-OFIM01', 'L-FIML', 'Y-C59', 'L-STRAB', 'Y-C58','L-OILG01')
            fundselect.grid(row = 1, column = 2+(3*int(i)), columnspan = 3)
            dict_cols[i].append(fundselect)
            fundaum = tk.Entry(self, width=30, name = 'fundaum_'+i , relief = 'flat', border = 2)
            fundaum.grid(row= 2,column = 2+(3*int(i)), columnspan = 3)
            dict_cols[i].append(fundaum)
            
            FSHead1 = tk.Entry(self, width = 10, bg = 'light grey')
            FSHead1.grid(row = 3, column = 2+(3*int(i)) , sticky = 'W')
            FSHead2 = tk.Entry(self, width = 10, bg = 'light grey')
            FSHead2.grid(row = 3, column = 3+(3*int(i)) , sticky = 'W')
            FSHead3 = tk.Entry(self, width = 10, bg = 'light grey')
            FSHead3.grid(row = 3, column = 4+(3*int(i)) , sticky = 'W')
            dict_cols[i].append(FSHead1)
            dict_cols[i].append(FSHead2)
            dict_cols[i].append(FSHead3)

        def CalcButton():
            #### clear Fund 1 calcs
            for i in n_maxrows:
                if dict_rows[i][0].get() != 'Generic':
                    dict_tickers[i][2].delete(0, tk.END)
                    dict_tickers[i][3].delete(0, tk.END)
            
            #### clear all funds  aum
            for i in n_maxcols:
                dict_cols[i][1].delete(0, tk.END)
                dict_cols[i][2].delete(0, tk.END)
                dict_cols[i][3].delete(0, tk.END)
                dict_cols[i][4].delete(0, tk.END)
            
            for i in n_maxcols:
                fund1 = dict_cols[i][0].get()
                if fund1 == '':
                    fa1 = ''
                    dict_cols[i][1].insert(0, fa1)
                elif fund1 == 'L-OFIM01':
                    fa1 = con.ref('ALFIMEA LN EQUITY','FUND_TOTAL_ASSETS')['value'][0]
                    dict_cols[i][1].insert(0, np.round(fa1,1))
                elif fund1 == 'L-FIML':
                    fa1 = con.ref('ALFIMWG LX EQUITY','FUND_TOTAL_ASSETS')['value'][0]
                    dict_cols[i][1].insert(0, np.round(fa1,1))
                elif fund1 == 'Y-C59':
                    fa1 = con.ref('APSTRNC LN EQUITY','FUND_TOTAL_ASSETS')['value'][0]
                    dict_cols[i][1].insert(0, np.round(fa1,1))
                elif fund1 == 'L-STRAB':
                    fa1 = con.ref('ALASBWG LX EQUITY','FUND_TOTAL_ASSETS')['value'][0]
                    dict_cols[i][1].insert(0, np.round(fa1,1))
                    fa1 = fa1/con.ref('GBPUSD Curncy','PX_LAST')['value'][0]
                elif fund1 == 'Y-C58':
                    fa1 = con.ref('DRGTYCI LN EQUITY','FUND_TOTAL_ASSETS')['value'][0]
                    dict_cols[i][1].insert(0, np.round(fa1,1))
                elif fund1 == 'L-OILG01':
                    fa1 = con.ref('ALILGWA LN EQUITY','FUND_TOTAL_ASSETS')['value'][0]
                    dict_cols[i][1].insert(0, np.round(fa1,1))
            
            for i in n_maxcols:
                fund1 = dict_cols[i][0].get()
                if fund1 != '':
                    if FSHeading.get() == 'FX':
                        dict_cols[i][2].insert(0, 'FX1 [mm])')
                        dict_cols[i][3].insert(0, 'FX2 [mm]')
                        dict_cols[i][4].insert(0, '% fund')
                    elif FSHeading.get() == 'Bond Futures':
                        dict_cols[i][2].insert(0, '# cnts')
                        dict_cols[i][3].insert(0, 'bp01 [local]')
                        dict_cols[i][4].insert(0, 'fund dur')
                    elif FSHeading.get() == 'Index Futures':
                        dict_cols[i][2].insert(0, '# cnts')
                        dict_cols[i][3].insert(0, 'not [gbp]')
                        dict_cols[i][4].insert(0, '% fund')
                    elif FSHeading.get() == 'Bonds':
                        dict_cols[i][2].insert(0, 'Not [mm]')
                        dict_cols[i][3].insert(0, 'bp01 [local]')
                        dict_cols[i][4].insert(0, 'fund dur')
                    elif FSHeading.get() == 'Options':
                        dict_cols[i][2].insert(0, '[# cnts, px]')
                        dict_cols[i][3].insert(0, 'prem [gbp]')
                        dict_cols[i][4].insert(0, 'bps fund')
                    elif FSHeading.get() == 'Generic':
                        dict_cols[i][2].insert(0, 'x1')
                        dict_cols[i][3].insert(0, 'x2')
                        dict_cols[i][4].insert(0, 'x3')
                        
            dict_subtickers = dict([(key, []) for key in n_maxrows ])
            for i in n_maxcols[1:]:
                fund1 = dict_cols[i][0].get()
                if fund1 != '':
                    for j in n_maxrows:
                        c1 = tk.Entry(self, width=10, name = 'c1_'+i+'_'+j , relief = 'flat', border = 2)
                        c1.grid(row= 5+int(j), column=2+(3*int(i)), sticky='W')
                        dict_subtickers[j].append(c1)
                        
                        c2 = tk.Entry(self, width=10, name = 'c2_'+i+'_'+j , relief = 'flat', border = 2)
                        c2.grid(row= 5+int(j), column=3+3*int(i), sticky='W')
                        dict_subtickers[j].append(c2)
            
                        c3 = tk.Entry(self, width=10, name = 'c3_'+i+'_'+j , bg='light blue', relief = 'flat', border = 2)
                        c3.grid(row= 5+int(j), column=4+3*int(i), sticky='W')
                        dict_subtickers[j].append(c3)
                    
            for i in n_maxrows:
                a1 = dict_rows[i][0].get()
                if a1 == 'FX':
                    fx = con.ref(dict_tickers[i][0].get()+' Curncy','PX_LAST')['value'][0]
                    if dict_tickers[i][0].get()[:3] == 'GBP':
                        fx_gbp = 1.0
                    else:
                        fx_gbp = con.ref('GBP'+dict_tickers[i][0].get()[:3]+' Curncy','PX_LAST')['value'][0]
                    fx1 = np.float(dict_tickers[i][1].get())
                    fx2 = fx*fx1
                    dict_tickers[i][2].insert(0,np.round(fx2,1))
                    fx_fund = (fx1/fx_gbp)/(np.float(dict_cols['0'][1].get())/100)
                    dict_tickers[i][3].insert(0,np.round(fx_fund,2))
                
                if a1 == 'Bond Futures':
                    bp01 = con.ref(dict_tickers[i][0].get(),'CONVENTIONAL_CTD_FORWARD_FRSK')['value'][0]
                    fx = con.ref(dict_tickers[i][0].get(),'CRNCY')['value'][0]
                    if fx == 'GBP':
                        fx_gbp = 1.0
                    else:
                        fx_gbp = con.ref('GBP'+fx+' Curncy','PX_LAST')['value'][0]
                        
                    num_cnts = np.float(dict_tickers[i][1].get())
                    dict_tickers[i][2].insert(0,int(10*num_cnts*bp01))
                    risk_gbp = 10*num_cnts*bp01/fx_gbp
                    dict_tickers[i][3].insert(0,np.round(risk_gbp/(np.float(dict_cols['0'][1].get())*100) ,2))
                    
                if a1 == 'Index Futures':
                    tick_s = con.ref(dict_tickers[i][0].get(),'FUT_TICK_SIZE')['value'][0]
                    tick_v = con.ref(dict_tickers[i][0].get(),'FUT_TICK_VAL')['value'][0]
                    px = con.ref(dict_tickers[i][0].get(),'PX_LAST')['value'][0]
                    
                    fx = con.ref(dict_tickers[i][0].get(),'CRNCY')['value'][0]
                    if fx == 'GBP':
                        fx_gbp = 1.0
                    else:
                        fx_gbp = con.ref('GBP'+fx+' Curncy','PX_LAST')['value'][0]
                        
                    num_cnts = np.float(dict_tickers[i][1].get())
                    eq_val = ((px/tick_s)*tick_v*num_cnts)/1000000
                    dict_tickers[i][2].insert(0,np.round( eq_val/fx_gbp,2 ))
                    
                    dict_tickers[i][3].insert(0,  np.round((eq_val/fx_gbp)/(np.float(dict_cols['0'][1].get())/100),2))
                    
                if a1 == 'Bonds':
                    bp01 = con.ref(dict_tickers[i][0].get(),'YAS_RISK')['value'][0]
                    
                    fx = con.ref(dict_tickers[i][0].get(),'CRNCY')['value'][0]
                    if fx == 'GBP':
                        fx_gbp = 1.0
                    else:
                        fx_gbp = con.ref('GBP'+fx+' Curncy','PX_LAST')['value'][0]
                        
                    not1 = np.float(dict_tickers[i][1].get())
                    dict_tickers[i][2].insert(0,int(100*not1*bp01))
                    risk_gbp = 100*not1*bp01/fx_gbp
                    dict_tickers[i][3].insert(0,np.round(risk_gbp/(np.float(dict_cols['0'][1].get())*100) ,2))
                
                if a1 == 'Options':
                    tick_s = con.ref(dict_tickers[i][0].get(),'FUT_TICK_SIZE')['value'][0]
                    tick_v = con.ref(dict_tickers[i][0].get(),'OPT_TICK_VAL')['value'][0]
                    
                    a1 = dict_tickers[i][1].get()
                    a2 = [ np.float(d) for d in re.findall(r"[-+]?\d*\.\d+|\d+", a1) ]
                    
                    num_cnts = a2[0]
                    if len(a2) == 1:
                        px = con.ref(dict_tickers[i][0].get(),'PX_LAST')['value'][0]
                    else:
                        px = a2[1]
                    
                    fx = con.ref(dict_tickers[i][0].get(),'CRNCY')['value'][0]
                    if fx == 'GBP':
                        fx_gbp = 1.0
                    else:
                        fx_gbp = con.ref('GBP'+fx+' Curncy','PX_LAST')['value'][0]
                        
                    opt_prem = ((px/tick_s)*tick_v*num_cnts)
                    dict_tickers[i][2].insert(0,int( opt_prem/fx_gbp ))
                    dict_tickers[i][3].insert(0,  np.round((opt_prem/fx_gbp)/(np.float(dict_cols['0'][1].get())*100),2))
                
                    
            
            g1 = [dict_cols[i][0].get() != '' for i in n_maxcols]
            g2 = np.where(np.array(g1) == True)[0]
            
            n_funds = [str(i) for i in np.arange(np.sum(g1))]
            for i in n_funds[1:]:
                i2 = str(g2[int(i)])
                fund1 = dict_cols[i2][0].get()
                if fund1 != '':
                    r1 = np.float(dict_cols[i2][1].get()) / np.float(dict_cols['0'][1].get())
                    for j in n_maxrows:
                        a1 = dict_rows[j][0].get()
                        if any(x == a1 for x in ['FX','Bond Futures','Index Futures','Bonds']):
                            dict_subtickers[j][-3+3*int(i)].insert(0, np.round(np.float(dict_tickers[j][1].get())*r1,1)   )
                            dict_subtickers[j][-2+3*int(i)].insert(0, np.round(np.float(dict_tickers[j][2].get())*r1,1)   )
                            dict_subtickers[j][-1+3*int(i)].insert(0, np.float(dict_tickers[j][3].get())   )
                        elif a1 == 'Options':
                            b1 = dict_tickers[j][1].get()
                            b2 = [ np.float(d) for d in re.findall(r"[-+]?\d*\.\d+|\d+", b1) ]
                            
                            dict_subtickers[j][-3+3*int(i)].insert(0, np.round(b2[0]*r1,1) )
                            dict_subtickers[j][-2+3*int(i)].insert(0, int(np.float(dict_tickers[j][2].get())*r1)   )
                            dict_subtickers[j][-1+3*int(i)].insert(0, np.float(dict_tickers[j][3].get()) )
                        elif a1 == 'Generic':
                            dict_subtickers[j][-3+3*int(i)].insert(0, np.round(np.float(dict_tickers[j][1].get())*r1,1)   )
                            if dict_tickers[j][2].get() != '':
                                dict_subtickers[j][-2+3*int(i)].insert(0, np.round(np.float(dict_tickers[j][2].get())*r1,1)   )
                            if dict_tickers[j][3].get() != '':
                                dict_subtickers[j][-1+3*int(i)].insert(0, np.round(np.float(dict_tickers[j][3].get())*r1,1)   )
                            
                            
        calc_button = ttk.Button(self, text="Calc", width = 16, command = CalcButton )
        calc_button.grid(column=1, row=1, columnspan = 2, rowspan = 2, sticky=tk.W,  pady=5)

class SwapMon1(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)
        
        label_tab = tk.Label(self, text = "Swaps Monitor", font = LARGE_FONT, bg="light grey", fg = 'blue')
        label_tab.grid(row = 0, column = 0, columnspan = 5, sticky = 'W')
        
        CurveLabel = ttk.Label(self, text = 'Curve: ')
        CurveLabel.grid(row = 2, column = 0 )
        CurveEntry = ttk.Entry(self, width = 15)
        CurveEntry.insert(0, "SOFR_DC")
        CurveEntry.grid(row = 2, column = 1 , sticky = 'W')
        
        CurveDateLabel = ttk.Label(self, text = 'Curve Date: ')
        CurveDateLabel.grid(row = 3, column = 0, padx = 10)
        CurveDateEntry = ttk.Entry(self, width = 10)
        CurveDateEntry.insert(0, 0)
        CurveDateEntry.grid(row = 3, column = 1,  sticky = 'W')

        OffsetDaysLabel = ttk.Label(self, text = 'Offsets: ')
        OffsetDaysLabel.grid(row = 4, column = 0, padx = 10)
        OffsetDaysEntry = ttk.Entry(self, width = 10)
        OffsetDaysEntry.insert(0, "-1, -10")
        OffsetDaysEntry.grid(row = 4, column = 1,  sticky = 'W')
        
        Msg_Build = ttk.Label(self, text = '')
        Msg_Build.grid(row = 2, column = 3,  sticky = 'E' )
        

        def BuildButton():
            f = ttk.Frame(self)
            f.grid(column=2, row=5, columnspan = 8, padx=5, pady=5,  sticky = 'nsew')
            tb_width = f.winfo_screenwidth() * 0.4
            tb_height = f.winfo_screenheight() * 0.3
            a1 = str(CurveEntry.get())
            a2 = [item.strip() for item in a1.split(',')]
            
            if len(CurveDateEntry.get()) < 4:
                a3 = int(CurveDateEntry.get())
            else:
                a3 = CurveDateEntry.get()
            
            a4 = str(OffsetDaysEntry.get())
            a5 = [item.strip() for item in a4.split(',')]
            a6 = []
            for i in a5:
                if len(i) < 4:
                    a6 = a6 + [int(i)]
                else:
                    a6 = a6 + [i]
            
            today = ql.Date(datetime.datetime.now().day,datetime.datetime.now().month,datetime.datetime.now().year)
            now = datetime.datetime.now()
            current_time = now.strftime("%H:%M:%S")
            c = ccy(a2[0],today)
            
            if c.ois_trigger == 0:
                crv = swap_build(a2[0], b = a3)
            else:
                crv = ois_dc_build(a2[0], b = a3)
            crv_tab = swap_table(crv, offset = a6)
            df = crv_tab.table
            
            pt = Table(f, dataframe=df, showtoolbar=True, height = tb_height, width = tb_width, showstatusbar=True)
            pt.setColumnColors(cols=[1,4], clr='#d4ebf2')
            pt.show()
            Msg_Build['text'] = "Done @"+current_time
            
        calc_button = ttk.Button(self, text="Build", width = 14, command = BuildButton )
        calc_button.grid(column=1, row=1, rowspan = 1, columnspan = 2, sticky=tk.W, pady=5)

class SwapFwds(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)
        
        label_tab = tk.Label(self, text = "Swaps: Changes in Fwds Space", font = LARGE_FONT, bg="light grey", fg = 'blue')
        label_tab.grid(row = 0, column = 0, columnspan = 5, sticky = 'W')
        
#        m = tk.StringVar()
#        m.set('SOFR_DC FED_DC ESTER_DC EONIA_DC SONIA_DC CAD_OIS_DC AONIA_DC NZD_OIS_DC CHF_OIS_DC SEK_OIS_DC TONAR_DC RUONIA_DC EUR_3M EUR_6M CAD_3M CHF_6M SEK_3M NOK_3M NOK_6M JPY_6M AUD_3M AUD_6M NZD_3M KRW_3M PLN_3M PLN_6M CZK_3M CZK_6M HUF_3M HUF_6M ZAR_3M ILS_3M RUB_3M COP_OIS_DC MXN_TIIE')
        curve_lstbox = tk.Listbox(self,  selectmode='multiple', width=18, height=60)
        curve_lstbox.grid(column=0, row=2, rowspan = 150, columnspan=1, sticky = 'W', padx=5)
        m = ["SOFR_DC", "FED_DC", "ESTER_DC", "EONIA_DC", "SONIA_DC", "CAD_OIS_DC", "AONIA_DC", "NZD_OIS_DC", "CHF_OIS_DC", "SEK_OIS_DC", "TONAR_DC", "RUONIA_DC", "EUR_3M", "EUR_6M", "CAD_3M", "CHF_6M", "SEK_3M", "NOK_3M", "NOK_6M", "JPY_6M", "AUD_3M", "AUD_6M", "NZD_3M", "KRW_3M", "PLN_3M", "PLN_6M", "CZK_3M", "CZK_6M", "HUF_3M", "HUF_6M", "ZAR_3M", "ILS_3M", "RUB_3M", "COP_OIS_DC", "MXN_TIIE"]
        for index, element in enumerate(m):
            curve_lstbox.insert(index, element)
        
        CurvesLabel = ttk.Label(self, text = 'Curves: ')
        CurvesLabel.grid(row = 2, column = 1 , sticky = 'E')
        CurvesEntry = tk.Entry(self, width = 30, fg='dark blue')
        CurvesEntry.grid(row = 2, column = 2 , sticky = 'W')

        OffsetDaysLabel = ttk.Label(self, text = 'Offsets: ')
        OffsetDaysLabel.grid(row = 3, column = 1, padx = 0,  sticky = 'E')
        OffsetDaysEntry = ttk.Entry(self, width = 30)
        OffsetDaysEntry.insert(0, "0, -30")
        OffsetDaysEntry.grid(row = 3, column = 2,  sticky = 'W')

        max_tenorLabel = ttk.Label(self, text = 'Max Tenor: ')
        max_tenorLabel.grid(row = 4, column = 1, padx = 0,  sticky = 'E')
        max_tenorEntry = ttk.Entry(self, width = 5)
        max_tenorEntry.insert(0, 30)
        max_tenorEntry.grid(row = 4, column = 2,  sticky = 'W')
       
        ChangesLabel = ttk.Label(self, text = 'Changes: ')
        ChangesLabel.grid(row = 5, column = 1, padx = 0,  sticky = 'E')
        ChangesEntry = ttk.Entry(self, width = 5)
        ChangesEntry.insert(0, 1)
        ChangesEntry.grid(row = 5, column = 2,  sticky = 'W')
        
        SpreadsLabel = ttk.Label(self, text = 'Spreads: ')
        SpreadsLabel.grid(row = 6, column = 1, padx = 0, sticky = 'E')
        SpreadsEntry = ttk.Entry(self, width = 5)
        SpreadsEntry.insert(0, 0)
        SpreadsEntry.grid(row = 6, column = 2,  sticky = 'W')
  
        Fwd_tenorLabel = ttk.Label(self, text = 'Fwd Tenor: ')
        Fwd_tenorLabel.grid(row = 7, column = 1, padx = 0, sticky = 'E')
        Fwd_tenorEntry = ttk.Entry(self, width = 3)
        Fwd_tenorEntry.insert(0, "1y")
        Fwd_tenorEntry.grid(row = 7, column = 2,  sticky = 'W')
  
        Interval_tenorLabel = ttk.Label(self, text = 'Internal Tenor: ')
        Interval_tenorLabel.grid(row = 8, column = 1, padx = 0, sticky = 'E')
        Interval_tenorEntry = ttk.Entry(self, width = 3)
        Interval_tenorEntry.insert(0, "1y")
        Interval_tenorEntry.grid(row = 8, column = 2,  sticky = 'W')
        
        
        def CalcButton():
            CurvesEntry.delete(0, tk.END)
            a2 = [curve_lstbox.get(i) for i in curve_lstbox.curselection()]
            CurvesEntry.insert(0, a2)
            a3 = str(OffsetDaysEntry.get())
            a4 = [item.strip() for item in a3.split(',')]
            a5 = []
            for i in a4:
                if len(i) < 4:
                    a5 = a5 + [int(i)]
                else:
                    a5 = a5 + [i]
 
            f = plt_ois_curve(c1 = a2, h1 = a5, max_tenor=int(max_tenorEntry.get()), bar_chg=int(ChangesEntry.get()), sprd=int(SpreadsEntry.get()), fwd_tenor = str(Fwd_tenorEntry.get()),int_tenor = str(Interval_tenorEntry.get()));
            
            canvas = FigureCanvasTkAgg(f, self)
            mplcursors.cursor()
            canvas.draw()
            canvas.get_tk_widget().grid(row=10, column=2, columnspan = 10, sticky = 'nsew', padx=10, pady=10)

            # navigation toolbar
            toolbarFrame = tk.Frame(self)
            toolbarFrame.grid(row=11,column=2)
            toolbar = NavigationToolbar2Tk(canvas, toolbarFrame)
            
        calc_button = ttk.Button(self, text="Calc", width = 29, command = CalcButton )
        calc_button.grid(column=2, row=1, rowspan = 1, columnspan = 2, sticky=tk.W, pady=5)


class SwapCrvs(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)
        
        label_tab = tk.Label(self, text = "Swaps: Changes in Fwds Space", font = LARGE_FONT, bg="light grey", fg = 'blue')
        label_tab.grid(row = 0, column = 0, columnspan = 5, sticky = 'W')
        
#        m = tk.StringVar()
#        m.set('SOFR_DC FED_DC ESTER_DC EONIA_DC SONIA_DC CAD_OIS_DC AONIA_DC NZD_OIS_DC CHF_OIS_DC SEK_OIS_DC TONAR_DC RUONIA_DC EUR_3M EUR_6M CAD_3M CHF_6M SEK_3M NOK_3M NOK_6M JPY_6M AUD_3M AUD_6M NZD_3M KRW_3M PLN_3M PLN_6M CZK_3M CZK_6M HUF_3M HUF_6M ZAR_3M ILS_3M RUB_3M COP_OIS_DC MXN_TIIE')
        curve_lstbox = tk.Listbox(self, selectmode='multiple', width=18, height=60)
        curve_lstbox.grid(column=0, row=2, rowspan = 150, columnspan=1, sticky = 'W', padx=5)
        m = ["SOFR_DC", "FED_DC", "ESTER_DC", "EONIA_DC", "SONIA_DC", "CAD_OIS_DC", "AONIA_DC", "NZD_OIS_DC",
             "CHF_OIS_DC", "SEK_OIS_DC", "TONAR_DC", "RUONIA_DC", "EUR_3M", "EUR_6M", "CAD_3M", "CHF_6M", "SEK_3M",
             "NOK_3M", "NOK_6M", "JPY_6M", "AUD_3M", "AUD_6M", "NZD_3M", "KRW_3M", "PLN_3M", "PLN_6M", "CZK_3M",
             "CZK_6M", "HUF_3M", "HUF_6M", "ZAR_3M", "ILS_3M", "RUB_3M", "COP_OIS_DC", "MXN_TIIE"]
        for index, element in enumerate(m):
            curve_lstbox.insert(index, element)
        
        CurvesLabel = ttk.Label(self, text = 'Curves: ')
        CurvesLabel.grid(row = 2, column = 1 , sticky = 'E')
        CurvesEntry = tk.Entry(self, width = 30, fg='dark blue')
        CurvesEntry.grid(row = 2, column = 2 , sticky = 'W')

        OffsetDaysLabel = ttk.Label(self, text = 'Offsets: ')
        OffsetDaysLabel.grid(row = 3, column = 1, padx = 0,  sticky = 'E')
        OffsetDaysEntry = ttk.Entry(self, width = 30)
        OffsetDaysEntry.insert(0, "0")
        OffsetDaysEntry.grid(row = 3, column = 2,  sticky = 'W')

        max_tenorLabel = ttk.Label(self, text = 'Max Tenor: ')
        max_tenorLabel.grid(row = 4, column = 1, padx = 0,  sticky = 'E')
        max_tenorEntry = ttk.Entry(self, width = 5)
        max_tenorEntry.insert(0, 30)
        max_tenorEntry.grid(row = 4, column = 2,  sticky = 'W')
       
        ChangesLabel = ttk.Label(self, text = 'Changes: ')
        ChangesLabel.grid(row = 5, column = 1, padx = 0,  sticky = 'E')
        ChangesEntry = ttk.Entry(self, width = 5)
        ChangesEntry.insert(0, 0)
        ChangesEntry.grid(row = 5, column = 2,  sticky = 'W')
        
        SpreadsLabel = ttk.Label(self, text = 'Spreads: ')
        SpreadsLabel.grid(row = 6, column = 1, padx = 0, sticky = 'E')
        SpreadsEntry = ttk.Entry(self, width = 5)
        SpreadsEntry.insert(0, 0)
        SpreadsEntry.grid(row = 6, column = 2,  sticky = 'W')
  
        Fwd_tenorLabel = ttk.Label(self, text = 'Fwd Tenor: ')
        Fwd_tenorLabel.grid(row = 7, column = 1, padx = 0, sticky = 'E')
        Fwd_tenorEntry = ttk.Entry(self, width = 3)
        Fwd_tenorEntry.insert(0, "1d")
        Fwd_tenorEntry.grid(row = 7, column = 2,  sticky = 'W')
  
        Interval_tenorLabel = ttk.Label(self, text = 'Internal Tenor: ')
        Interval_tenorLabel.grid(row = 8, column = 1, padx = 0, sticky = 'E')
        Interval_tenorEntry = ttk.Entry(self, width = 3)
        Interval_tenorEntry.insert(0, "3m")
        Interval_tenorEntry.grid(row = 8, column = 2,  sticky = 'W')
        
        Curve_FillLabel = ttk.Label(self, text = 'Curve Fill: ')
        Curve_FillLabel.grid(row = 9, column = 1, padx = 0, sticky = 'E')
        Curve_FillEntry = ttk.Entry(self, width = 20)
        Curve_FillEntry.insert(0, "0y2y, 0y5y, 0y10y")
        Curve_FillEntry.grid(row = 9, column = 2,  sticky = 'W')
        
        
        
        def CalcButton():
            CurvesEntry.delete(0, tk.END)
            a2 = [curve_lstbox.get(i) for i in curve_lstbox.curselection()]
            CurvesEntry.insert(0, a2)
            a3 = str(OffsetDaysEntry.get())
            a4 = [item.strip() for item in a3.split(',')]
            a5 = []
            for i in a4:
                if len(i) < 4:
                    a5 = a5 + [int(i)]
                else:
                    a5 = a5 + [i]
                    
            a6 = str(Curve_FillEntry.get())
            a7 = [item.strip() for item in str(a6).split(',')]
            a8 = [ [int(d) for d in re.findall(r'-?\d+', a7[i])] for i in np.arange(len(a7)) ]
            
            for i in np.arange(len(a8)):
                a8[i][1] = a8[i][0] + a8[i][1] 

            f = plt_ois_curve(c1 = a2, h1 = a5, max_tenor=int(max_tenorEntry.get()), bar_chg=int(ChangesEntry.get()), sprd=int(SpreadsEntry.get()), fwd_tenor = str(Fwd_tenorEntry.get()),int_tenor = str(Interval_tenorEntry.get()), curve_fill= a8   );
            
            canvas = FigureCanvasTkAgg(f, self)
            mplcursors.cursor()
            canvas.draw()
            canvas.get_tk_widget().grid(row=10, column=2, columnspan = 10, sticky = 'nsew', padx=10, pady=10)

            # navigation toolbar
            toolbarFrame = tk.Frame(self)
            toolbarFrame.grid(row=11,column=2)
            toolbar = NavigationToolbar2Tk(canvas, toolbarFrame)
            
        calc_button = ttk.Button(self, text="Calc", width = 29, command = CalcButton )
        calc_button.grid(column=2, row=1, rowspan = 1, columnspan = 2, sticky=tk.W, pady=5)


#a6 = "0y2y, 0y5y, 0y10y"
#str(a6)
#a7 = [item.strip() for item in str(a6).split(',')]
#a8 = [ [int(d) for d in re.findall(r'-?\d+', a7[i])] for i in np.arange(len(a7)) ]


######### ADD load and save capabilities
class OptStrat(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)        
        
        label_tab = tk.Label(self, text = "Option Strategies", font = LARGE_FONT, bg = 'light grey', fg = 'green')
        label_tab.grid(row = 0, column = 0, columnspan = 5, sticky = 'W')
        
        today = ql.Date(datetime.datetime.now().day,datetime.datetime.now().month,datetime.datetime.now().year)
        FUT_CT = {'1': 'F', '2': 'G', '3': 'H', '4': 'J','5': 'K','6': 'M','7': 'N','8': 'Q','9': 'U','10': 'V','11': 'X','12': 'Z'}   
        FUT_M = pd.DataFrame()
        d1 = ql.Date(15,today.month(),today.year())
        s1 = pd.Series([d1+ql.Period(i,ql.Months) for i in range(12) ])
        a2 = s1.tolist()[(3-d1.month()%3)%3]
        s2 = s1.append(pd.Series([a2+ql.Period(3*i,ql.Months) for i in range(1,12) ]))
    
        FUT_M['Date'] = pd.Series(s1.tolist())
        FUT_M['TickerMonth'] = pd.Series([FUT_CT[str(FUT_M['Date'][i].month())]+str(FUT_M['Date'][i].year())[-1:] for i in range(len(FUT_M))])
        FUT_M['BondMonth'] =  pd.Series([True, True, True] + [any(x == FUT_M['TickerMonth'][i][0] for x in ['H','M','U','Z']) for i in np.arange(3,len(FUT_M))] )
        t1 = [FUT_M['TickerMonth'][i] for i in np.arange(len(FUT_M))]
        ticker_list_bonds = ['FV','TY','US','WN','1I','2I','3I','4I','5I','1M','2M','3M','4M','5M','1C','2C','3C','4C','5C','1J','2J','3J','4J','5J','DU','OE','RX','UB']
        ticker_list_stir =  ['ED','0E','2E','3E','4E','ER','0R','2R','3R','4R','SFI','0N','2N','3N','4N']
        
        t1_lst = tk.Listbox(self, width=7, height=60, exportselection=0, selectbackground='dark blue')
        t1_lst.grid(column=0, row=2, rowspan = 150, columnspan=1, sticky = 'W', padx=5)
        m = ticker_list_bonds+ticker_list_stir
        for index, element in enumerate(m):
            t1_lst.insert(index, element)
        
        t2_lst = tk.Listbox(self,  width=7, height=60, exportselection=0, selectbackground='dark green')
        t2_lst.grid(column=1, row=2, rowspan = 150, columnspan=1, sticky = 'W', padx=5)
        for index, element in enumerate(t1):
            t2_lst.insert(index, element)


        ChainLabel = ttk.Label(self, text = 'Opt Chain: ')
        ChainLabel.grid(row = 2, column = 2 , sticky = 'E')
        ChainEntry = tk.Entry(self, width = 30, fg = 'dark blue')
#        ChainEntry.insert(0, "2CF2")
        ChainEntry.grid(row = 2, column = 3 , sticky = 'W')

        OptionTypeLabel = ttk.Label(self, text = 'Opt Type: ')
        OptionTypeLabel.grid(row = 3, column = 2, padx = 0, sticky = 'E')
        OptionTypeEntry = ttk.Entry(self, width = 30)
        OptionTypeEntry.insert(0, "P, P")
        OptionTypeEntry.grid(row = 3, column = 3,  sticky = 'W')

        OptionStrkLabel = ttk.Label(self, text = 'Opt Strikes: ')
        OptionStrkLabel.grid(row = 4, column = 2, padx = 0, sticky = 'E')
        OptionStrkEntry = ttk.Entry(self, width = 30)
        OptionStrkEntry.insert(0, "160, 158")
        OptionStrkEntry.grid(row = 4, column = 3,  sticky = 'W')
        
        OptionWgtLabel = ttk.Label(self, text = 'Opt Weights: ')
        OptionWgtLabel.grid(row = 5, column = 2, padx = 0, sticky = 'E')
        OptionWgtEntry = ttk.Entry(self, width = 10)
        OptionWgtEntry.insert(0, "1, -2")
        OptionWgtEntry.grid(row = 5, column = 3,  sticky = 'W')

        SimRangeLabel = ttk.Label(self, text = 'Sim_Range: ')
        SimRangeLabel.grid(row = 6, column = 2, padx = 0, sticky = 'E')
        SimRangeEntry = ttk.Entry(self, width = 10)
        SimRangeEntry.insert(0, "-4, 2")
        SimRangeEntry.grid(row = 6, column = 3,  sticky = 'W')
        
        IcrmentLabel = ttk.Label(self, text = 'Inc: ')
        IcrmentLabel.grid(row = 7, column = 2, padx = 0, sticky = 'E')
        IcrmentEntry = ttk.Entry(self, width = 5)
        IcrmentEntry.insert(0, 1.0)
        IcrmentEntry.grid(row = 7, column = 3,  sticky = 'W')
  
        ChainLenLabel = ttk.Label(self, text = 'Chain Len: ')
        ChainLenLabel.grid(row = 8, column = 2, padx = 0, sticky = 'E')
        ChainLenEntry = ttk.Entry(self, width = 10)
        ChainLenEntry.insert(0, "12, 12")
        ChainLenEntry.grid(row = 8, column = 3,  sticky = 'W')
        
        
        def CalcButton():
            ChainEntry.delete(0, tk.END)
            a1 = str(t1_lst.get(t1_lst.curselection()[0]))+str(t2_lst.get(t2_lst.curselection()[0]))
            ChainEntry.insert(0, a1)
            
#            a1 = str(ChainEntry.get())
            a2 = [item.strip() for item in a1.split(',')]
            a3 = str(OptionTypeEntry.get())
            a4 = [item.strip() for item in a3.split(',')]
            a5 = str(OptionStrkEntry.get())
            a6 = [np.float(item.strip()) for item in a5.split(',')]
            a7 = str(OptionWgtEntry.get())
            a8 = [int(d) for d in re.findall(r'-?\d+', a7)]
            a9 = str(SimRangeEntry.get())
            a10 = [ np.float(item.strip()) for item in a9.split(',')]
            a12 = str(ChainLenEntry.get())
            a13 = [int(d) for d in re.findall(r'-?\d+', a12)]
            print(a2, a4, a6, a8, a10, a13)
            
            try:
                bfo_str = bond_fut_opt_strat(a2, a4, a6, a8, s_range = a10, increm = np.float(IcrmentEntry.get()), chain_len = a13)
                f = plt_opt_strat(bfo_str);
            except:
                bfo_str = stir_opt_strat(a2, a4, a6, a8, s_range = a10, increm = np.float(IcrmentEntry.get()), chain_len = a13)
                f = plt_stir_opt_strat(bfo_str);

            canvas = FigureCanvasTkAgg(f, self)
            mplcursors.cursor()
            canvas.draw()
            canvas.get_tk_widget().grid(row=10, column=3, columnspan = 5, sticky = 'nsew', padx=10, pady=10)
            # navigation toolbar
            toolbarFrame = tk.Frame(self)
            toolbarFrame.grid(row=11,column=3)
            toolbar = NavigationToolbar2Tk(canvas, toolbarFrame)
            
        calc_button = ttk.Button(self, text="Calc", width = 29, command = CalcButton )
        calc_button.grid(column=3, row=1, rowspan = 1, columnspan = 2, sticky=tk.W, pady=5)

class SwapHM(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)               
        
        label_tab = tk.Label(self, text = "Swaps Heatmap", font = LARGE_FONT, bg ='light grey', fg = 'blue')
        label_tab.grid(row = 0, column = 0, columnspan = 5, sticky = 'W')
        
#        m = tk.StringVar()
#        m.set('SOFR_DC FED_DC ESTER_DC EONIA_DC SONIA_DC CAD_OIS_DC AONIA_DC NZD_OIS_DC CHF_OIS_DC SEK_OIS_DC TONAR_DC RUONIA_DC EUR_3M EUR_6M CAD_3M CHF_6M SEK_3M NOK_3M NOK_6M JPY_6M AUD_3M AUD_6M NZD_3M KRW_3M PLN_3M PLN_6M CZK_3M CZK_6M HUF_3M HUF_6M ZAR_3M ILS_3M RUB_3M COP_OIS_DC MXN_TIIE')
        curve_lstbox = tk.Listbox(self, selectmode='multiple', width=18, height=60)
        curve_lstbox.grid(column=0, row=2, rowspan = 150, columnspan=1, sticky = 'W', padx=5)
        m = ["SOFR_DC", "FED_DC", "ESTER_DC", "EONIA_DC", "SONIA_DC", "CAD_OIS_DC", "AONIA_DC", "NZD_OIS_DC",
             "CHF_OIS_DC", "SEK_OIS_DC", "TONAR_DC", "RUONIA_DC", "EUR_3M", "EUR_6M", "CAD_3M", "CHF_6M", "SEK_3M",
             "NOK_3M", "NOK_6M", "JPY_6M", "AUD_3M", "AUD_6M", "NZD_3M", "KRW_3M", "PLN_3M", "PLN_6M", "CZK_3M",
             "CZK_6M", "HUF_3M", "HUF_6M", "ZAR_3M", "ILS_3M", "RUB_3M", "COP_OIS_DC", "MXN_TIIE"]
        for index, element in enumerate(m):
            curve_lstbox.insert(index, element)
        
        OutrightFlagLabel = ttk.Label(self, text = 'Outright [1] or Curve [0]: ')
        OutrightFlagLabel.grid(row = 3, column = 1 , sticky = 'E')
        OutrightFlagEntry = ttk.Entry(self, width = 5)
        OutrightFlagEntry.insert(0, 1)
        OutrightFlagEntry.grid(row = 3, column = 2 , sticky = 'W')
        
        CurvesHMLabel = ttk.Label(self, text = 'Curves: ')
        CurvesHMLabel.grid(row = 2, column = 1,  sticky = 'E' )
        CurvesHMEntry = tk.Entry(self, width = 80, fg = 'dark blue')
        CurvesHMEntry.grid(row = 2, column = 2 , sticky = 'W')

        CurveDateHMLabel = ttk.Label(self, text = 'Curve Date: ')
        CurveDateHMLabel.grid(row = 4, column = 1, padx = 0, sticky = 'E')
        CurveDateHMEntry = ttk.Entry(self, width = 10)
        CurveDateHMEntry.insert(0, 0)
        CurveDateHMEntry.grid(row = 4, column = 2,  sticky = 'W')

        OffsetDaysHMLabel = ttk.Label(self, text = 'Offset: ')
        OffsetDaysHMLabel.grid(row = 5, column = 1, padx = 0, sticky = 'E')
        OffsetDaysHMEntry = ttk.Entry(self, width = 10)
        OffsetDaysHMEntry.insert(0, -1)
        OffsetDaysHMEntry.grid(row = 5, column = 2,  sticky = 'W')
        
        OISFlagHMLabel = ttk.Label(self, text = 'OIS Flag: ')
        OISFlagHMLabel.grid(row = 6, column = 1, padx = 0, sticky = 'E')
        OISFlagHMEntry = ttk.Entry(self, width = 5)
        OISFlagHMEntry.insert(0, 1)
        OISFlagHMEntry.grid(row = 6, column = 2,  sticky = 'W')
        
        Z_offsetLabel = ttk.Label(self, text = 'Z_Offset: ')
        Z_offsetLabel.grid(row = 7, column = 1, padx = 0, sticky = 'E')
        Z_offsetEntry = ttk.Entry(self, width = 5)
        Z_offsetEntry.insert(0, 0)
        Z_offsetEntry.grid(row = 7, column = 2,  sticky = 'W')
        
        RollLabel = ttk.Label(self, text = 'Roll: ')
        RollLabel.grid(row = 8, column = 1, padx = 0, sticky = 'E')
        RollEntry = ttk.Entry(self, width = 10)
        RollEntry.insert(0, "3M, 6M")
        RollEntry.grid(row = 8, column = 2,  sticky = 'W')
  
       
        def CalcButton():
            CurvesHMEntry.delete(0, tk.END)
            a2 = [curve_lstbox.get(i) for i in curve_lstbox.curselection()]
            CurvesHMEntry.insert(0, a2)
            a5 = str(RollEntry.get())
            a6 = [item.strip() for item in a5.split(',')]
            
            if len(OffsetDaysHMEntry.get()) < 4:
                a3 = str(OffsetDaysHMEntry.get())
                a4 = [int(d) for d in re.findall(r'-?\d+', a3)]
            else:
                a3 = OffsetDaysHMEntry.get()
                a4 = [item.strip() for item in a3.split(',')]
            
            if len(CurveDateHMEntry.get()) < 4:
                a7 = int(CurveDateHMEntry.get())
            else:
                a7 = CurveDateHMEntry.get()
#            print(a7, a4, a6)
                        
            if int(OutrightFlagEntry.get()) == 1:
                f = rates_hm(a2, b = a7, offset = a4, ois_flag = int(OISFlagHMEntry.get()), z_offset = int(Z_offsetEntry.get()));
            else:
                f = curve_hm(a2, b = a7, offset = a4, ois_flag = int(OISFlagHMEntry.get()), z_roll = a6);
            
            canvas = FigureCanvasTkAgg(f, self)
            mplcursors.cursor()
            canvas.draw()
            canvas.get_tk_widget().grid(row=10, column=2, sticky = 'nsew', padx=10, pady=10)

        # navigation toolbar
            toolbarFrame = tk.Frame(self)
            toolbarFrame.grid(row=11,column=2)
            toolbar = NavigationToolbar2Tk(canvas, toolbarFrame)
            
        calc_button = ttk.Button(self, text="Calc", width = 79, command = CalcButton )
        calc_button.grid(column=2, row=1, sticky=tk.W, pady=5)

class SwaptionCurve(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)                 
        
        label_tab = tk.Label(self, text = "Swaption Implied Curve", font = LARGE_FONT, bg = 'light grey', fg = 'dark blue')
        label_tab.grid(row = 0, column = 0, columnspan = 5, sticky = 'W')
        
        CurveSWCLabel = ttk.Label(self, text = 'Curve: ')
        CurveSWCLabel.grid(row = 2, column = 0 )
        CurveSWCEntry = ttk.Entry(self, width = 15)
        CurveSWCEntry.insert(0, "SOFR_DC")
        CurveSWCEntry.grid(row = 2, column = 1 , sticky = 'W')
        
        TailsLabel = ttk.Label(self, text = 'Tails: ')
        TailsLabel.grid(row = 3, column = 0, padx = 10)
        TailsEntry = ttk.Entry(self, width = 10)
        TailsEntry.insert(0, '2, 10')
        TailsEntry.grid(row = 3, column = 1,  sticky = 'W')

        def CalcButton():
            a1 = str(CurveSWCEntry.get())
            a2 = [item.strip() for item in a1.split(',')]
            a3 = TailsEntry.get()
            a4 = [int(d) for d in re.findall(r'-?\d+', a3)]
                       
            f = Swaption_Curve(a2[0], tails = a4);
            
            canvas = FigureCanvasTkAgg(f, self)
            mplcursors.cursor()
            canvas.draw()
            canvas.get_tk_widget().grid(row=5, column=1, columnspan = 5,sticky = 'nsew', padx=10, pady=10)
            # navigation toolbar
            toolbarFrame = tk.Frame(self)
            toolbarFrame.grid(row=6,column=1)
            toolbar = NavigationToolbar2Tk(canvas, toolbarFrame)
            
        calc_button = ttk.Button(self, text="Calc", width = 14, command = CalcButton )
        calc_button.grid(column=1, row=1, sticky=tk.W,  pady=5)

class SwaptionPricer(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)
        
        label_tab = tk.Label(self, text = "Swaption Pricer", font = LARGE_FONT, bg = 'light grey', fg = 'dark blue')
        label_tab.grid(row = 0, column = 0, columnspan = 5, sticky = 'W')
        
        CurveSWPLabel = ttk.Label(self, text = 'Curve: ')
        CurveSWPLabel.grid(row = 2, column = 0 )
        CurveSWPEntry = ttk.Entry(self, width = 20)
        CurveSWPEntry.insert(0, "SOFR_DC")
        CurveSWPEntry.grid(row = 2, column = 1 , sticky = 'W')
        
        OptionTypeSWPLabel = ttk.Label(self, text = 'Option(s) Type: ')
        OptionTypeSWPLabel.grid(row = 3, column = 0, padx = 10)
        OptionTypeSWPEntry = ttk.Entry(self, width = 20)
        OptionTypeSWPEntry.insert(0, 'P')
        OptionTypeSWPEntry.grid(row = 3, column = 1,  sticky = 'W')
        
        NotionalSWPLabel = ttk.Label(self, text = 'Notional (mm): ')
        NotionalSWPLabel.grid(row = 4, column = 0, padx = 10)
        NotionalSWPEntry = ttk.Entry(self, width = 20)
        NotionalSWPEntry.insert(0, '100')
        NotionalSWPEntry.grid(row = 4, column = 1,  sticky = 'W')
        
        OptionExpSWPLabel = ttk.Label(self, text = 'Option(s) Expiry')
        OptionExpSWPLabel.grid(row = 5, column = 0, padx = 10)
        OptionExpSWPEntry = ttk.Entry(self, width = 20)
        OptionExpSWPEntry.insert(0, '6m')
        OptionExpSWPEntry.grid(row = 5, column = 1,  sticky = 'W')
        
        OptionDetsSWPLabel = ttk.Label(self, text = 'Option(s) Details')
        OptionDetsSWPLabel.grid(row = 6, column = 0, padx = 10)
        OptionDetsSWPEntry = ttk.Entry(self, width = 20)
        OptionDetsSWPEntry.insert(0, '[5,1.3]')
        OptionDetsSWPEntry.grid(row = 6, column = 1,  sticky = 'W')
        
        RollSWPLabel = ttk.Label(self, text = 'Roll: ')
        RollSWPLabel.grid(row = 7, column = 0, padx = 10)
        RollSWPEntry = ttk.Entry(self, width = 20)
        RollSWPEntry.insert(0, "-1m,-2m,-3m")
        RollSWPEntry.grid(row = 7, column = 1,  sticky = 'W')
        
        Strat_TagSWPLabel = ttk.Label(self, text = 'Strat_Tag: ')
        Strat_TagSWPLabel.grid(row = 8, column = 0, padx = 10)
        Strat_TagSWPEntry = ttk.Entry(self, width = 10)
        Strat_TagSWPEntry.insert(0, 1)
        Strat_TagSWPEntry.grid(row = 8, column = 1,  sticky = 'W')
        

        def CalcButton():
            a1 = str(CurveSWPEntry.get())
            a2 = [item.strip() for item in a1.split(',')]
            a3 = str(OptionTypeSWPEntry.get())
            a4 = [item.strip() for item in a3.split(',')]
            a5 = NotionalSWPEntry.get()
            a6 = [int(d) for d in re.findall(r'-?\d+', a5)]
            a7 = str(RollSWPEntry.get())
            a8 = [item.strip() for item in a7.split(',')]
            a9 = "6m"
            a10 = [item.strip() for item in str(a9).split(',')]
            a11 = []

            for i in a10:
                if len(i) > 1:
                    a11 = a11 + [i]
                else:
                    a11 = a11 + [int(i)]

            a12 = OptionDetsSWPEntry.get()
            a13 = [ np.float(d) for d in re.findall(r"[-+]?\d*\.\d+|\d+", a12) ] 
            a14 = np.array(a13).reshape((int(len(a13) / 2), 2))
            a15 = [list(a14[i]) for i in np.arange(len(a14))]

            for i in np.arange(len(a15)):
                if len(a11) == 1:
                    a15[i] = [a11[0]] + a15[i]
                else:
                    a15[i] = [a11[i]] + a15[i]           
            print(a2, a4, a6, a8, a11, a15, len(a15), type(a15))
            
            swop_out = Swaption_Pricer(a2[0] ,option_type = a4, notional = a6, t = a15, roll = a8, strat_tag = int(Strat_TagSWPEntry.get()));
            df1 = swop_out.table
            df2 = swop_out.roll
            
            text = tk.Text(self, width = 150, height=10, font=('Consolas', 8) )
            text.insert(tk.END, str(tabulate(df1, headers='keys', tablefmt='github', showindex=False )))
            text.grid(row=9, column=1, sticky = 'nsew', padx=5, pady=5)
            
            text = tk.Text(self, width = 150, height=10, font=('Consolas', 8) )
            text.insert(tk.END, str(tabulate(df2, headers='keys', tablefmt='github', showindex=False )))
            text.grid(row=10, column=1, sticky = 'nsew', padx=5, pady=5)
            print(swop_out.table, swop_out.roll)
            
#            canvas = FigureCanvasTkAgg(f, self)
#            mplcursors.cursor()
#            canvas.draw()
#            canvas.get_tk_widget().grid(row=8, column=1, sticky = 'nsew', padx=10, pady=10)

        # navigation toolbar
#            toolbarFrame = tk.Frame(self)
#            toolbarFrame.grid(row=9,column=1)
#            toolbar = NavigationToolbar2Tk(canvas, toolbarFrame)
            
        calc_button = ttk.Button(self, text="Calc", width = 19, command = CalcButton )
        calc_button.grid(column=1, row=1, sticky=tk.W,  pady=5)

class SwapPricer(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)
        
        label_tab = tk.Label(self, text = "Swaps Pricer ", font = LARGE_FONT, bg ='light grey', fg = 'blue')
        label_tab.grid(row = 0, column = 0, columnspan = 5, sticky = 'W')
        
        curve_lstbox = tk.Listbox(self, selectmode='multiple', width=18, height=60)
        curve_lstbox.grid(column=0, row=4, rowspan = 150, columnspan=1, sticky = 'W', padx=5)
        m = ["SOFR_DC", "FED_DC", "ESTER_DC", "EONIA_DC", "SONIA_DC", "CAD_OIS_DC", "AONIA_DC", "NZD_OIS_DC",
             "CHF_OIS_DC", "SEK_OIS_DC", "TONAR_DC", "RUONIA_DC", "EUR_3M", "EUR_6M", "CAD_3M", "CHF_6M", "SEK_3M",
             "NOK_3M", "NOK_6M", "JPY_6M", "AUD_3M", "AUD_6M", "NZD_3M", "KRW_3M", "PLN_3M", "PLN_6M", "CZK_3M",
             "CZK_6M", "HUF_3M", "HUF_6M", "ZAR_3M", "ILS_3M", "RUB_3M", "COP_OIS_DC", "MXN_TIIE"]
        for index, element in enumerate(m):
            curve_lstbox.insert(index, element)

        CurveLabel = ttk.Label(self, text = 'Curve: ')
        CurveLabel.grid(row = 2, column = 1,  sticky = 'E' )
        CurveDateLabel = ttk.Label(self, text = 'Curve Date: ')
        CurveDateLabel.grid(row = 3, column = 1, padx = 10, sticky = 'E')
        CurveSelectLabel = ttk.Label(self, text = 'Curve: ')
        CurveSelectLabel.grid(row = 4, column = 1,  sticky = 'E' )
        
        Swap = ttk.Label(self, text = 'Swap:    ')
        Swap.grid(row = 5, column = 1 , sticky = 'E')
        StartDate_Label = ttk.Label(self, text = 'Start Date: ')
        StartDate_Label.grid(row = 6, column = 1, padx = 10, sticky = 'E')
        Tenor_Label = ttk.Label(self, text = 'Tenor: ')
        Tenor_Label.grid(row = 7, column = 1, padx = 10, sticky = 'E')
        Rate = ttk.Label(self, text = 'Rate:    ')
        Rate.grid(row = 8, column = 1 , sticky = 'E')
        BP01 = ttk.Label(self, text = 'BP01:    ')
        BP01.grid(row = 9, column = 1 , sticky = 'E')
        Not_Label = ttk.Label(self, text = 'Notional (mm): ')
        Not_Label.grid(row = 10, column = 1, padx = 10, sticky = 'E')
        RiskL = ttk.Label(self, text = 'Risk (Native):    ')
        RiskL.grid(row = 11, column = 1 , sticky = 'E')
        RiskGBP = ttk.Label(self, text = 'Risk (GBP):    ')
        RiskGBP.grid(row = 12, column = 1 , sticky = 'E')
        Fixing = ttk.Label(self, text = 'Fixing:    ')
        Fixing.grid(row = 13, column = 1 , sticky = 'E')
        FixF = ttk.Label(self, text = 'Fix Freq:    ')
        FixF.grid(row = 14, column = 1 , sticky = 'E')
        FltF = ttk.Label(self, text = 'Flt Freq:    ')
        FltF.grid(row = 15, column = 1 , sticky = 'E')
        Strat = ttk.Label(self, text = 'Strategy:    ')
        Strat.grid(row = 16, column = 1 , sticky = 'E')
        Weights = ttk.Label(self, text = 'Weights:    ')
        Weights.grid(row = 17, column = 1 , sticky = 'E')
        Spreads = ttk.Label(self, text = 'Spread / Fly:    ')
        Spreads.grid(row = 18, column = 1 , sticky = 'E')
        
        ###### build curve
        CurveEntry = tk.Entry(self, width = 50, fg = 'dark blue')
        CurveEntry.grid(row = 2, column = 2 , columnspan=5, sticky = 'W')
        
        CurveDateEntry = ttk.Entry(self, width = 10)
        CurveDateEntry.insert(0, 0)
        CurveDateEntry.grid(row = 3, column = 2,  sticky = 'W')
        
        Msg_Build = ttk.Label(self, text = '')
        Msg_Build.grid(row = 2, column = 9,  sticky = 'E' )
        
        ###### pricing swaps
        n_max = 9
        n_max = [str(i) for i in np.arange(n_max)]
        dict_curves = dict([(key, []) for key in n_max ])
        for i in n_max:
            m = tk.StringVar(self)
            curveselect = ttk.Combobox(self, width = 10, textvariable = m, name = 'curveselect'+'_'+i )
 #           curveselect['values'] = tuple([str(a2[i]) for i in np.arange(len(a2))])
            curveselect.grid(row = 4, column = 2+int(i), padx = 2)
            dict_curves[i].append(curveselect)
        
        n = 9 # number of "active swaps" to be price
        n = [str(i) for i in np.arange(n)]
        dict_swap = dict([(key, []) for key in ['swapentry','startdate','tenor','swaprate','bp01','not','risk_l','risk_gbp','fix','fixf','fltf','strategy','weights','spread']])
        
        for j1, j2 in enumerate(dict_swap.keys()):
            for i1, i2 in enumerate(n):
                if any(x == j2 for x in ['swapentry','bp01','risk_l','risk_gbp']):
                    e = tk.Entry(self, width=10, name = j2+'_'+i2 , bg='light blue', relief = 'flat', border = 2)
                elif any(x == j2 for x in ['fix','fixf','fltf']):
                    e = tk.Entry(self, width=10, name = j2+'_'+i2 , bg='beige', relief = 'flat', border = 2)
                elif j2 == 'swaprate':
                    e = tk.Entry(self, width=10, name = j2+'_'+i2 , bg='light blue', relief = 'flat', border = 2, fg = 'red')
                elif j2 == 'not':
                    e = tk.Entry(self, width=10, name = j2+'_'+i2)
                    e.insert(0, 100)
                elif j2 == 'tenor':
                    e = tk.Entry(self, width=10, name = j2+'_'+i2)
                    e.insert(0, 5)
                elif j2 == 'startdate':
                    e = tk.Entry(self, width=10, name = j2+'_'+i2)
                    e.insert(0, '3m')
                elif j2 == 'strategy':
                    e = tk.Entry(self, width=10, name = j2+'_'+i2 , bg='light green', relief = 'flat', border = 2)
                elif j2 == 'weights':
                    e = tk.Entry(self, width=10, name = j2+'_'+i2 , bg='light green', relief = 'flat', border = 2)
                    e.insert(0, 0)
                elif j2 == 'spread':
                    e = tk.Entry(self, width=10, name = j2+'_'+i2 , bg='light green', relief = 'flat', border = 2, fg = 'red')

                e.grid(row=5+j1, column=2+i1, sticky='NWSE', padx = 2)
                dict_swap[j2].append(e)

        def BuildButton():
            CurveEntry.delete(0, tk.END)
            a2 = [curve_lstbox.get(i) for i in curve_lstbox.curselection()]
            CurveEntry.insert(0, a2)
            if len(CurveDateEntry.get()) < 4:
                a3 = int(CurveDateEntry.get())
            else:
                a3 = CurveDateEntry.get()
            
            print(tuple([str(a2[i]) for i in np.arange(len(a2))]))
            ###### pricing swaps
            for i in n_max:
                self.children['curveselect'+'_'+i]['values'] = tuple([str(a2[i]) for i in np.arange(len(a2))])

            today = ql.Date(datetime.datetime.now().day,datetime.datetime.now().month,datetime.datetime.now().year)
            now = datetime.datetime.now()
            current_time = now.strftime("%H:%M:%S")
            
            global crv
            crv = dict([(key, []) for key in a2])
            for i in np.arange(len(a2)):
                c = ccy(a2[i],today)
                if c.ois_trigger == 0:
                    crv[a2[i]] = swap_build(a2[i], b = a3)
                else:
                    crv[a2[i]] = ois_dc_build(a2[i], b = a3)
            
            print(crv)
            Msg_Build['text'] = "Done @"+current_time

        build_button = ttk.Button(self, text="Build", width = 20, command = BuildButton )
        build_button.grid(column=7, row=2, columnspan=2, sticky=tk.W, padx=5, pady=5)
        
        def CalcButton():
            today = ql.Date(datetime.datetime.now().day,datetime.datetime.now().month,datetime.datetime.now().year)
            ###### deleting old values upon re-CALC
            for i in dict_swap.keys():
                if any(x == i for x in ['swapentry','swaprate','bp01','risk_l','risk_gbp','fix','fixf','fltf','spread']):
                    for j in np.arange(len(n)):
                        dict_swap[i][j].delete(0, tk.END)
                    
            d1 = []
            w1 = []
            r1 = []
            
            for i1, i2 in enumerate(dict_curves.keys()):
                a1 = str(dict_curves[i2][0].get())
                if a1 != '':
                    a2 = str(dict_swap['startdate'][i1].get())
                
                    if  any(   (x == '-') or (x == 'm') or (x == 'w') or (x == 'd') for x in a2):
                        a3 = dict_swap['startdate'][i1].get()
                    else:
                        a3 = int(dict_swap['startdate'][i1].get())
                
                    a4 = str(dict_swap['tenor'][i1].get())
                    if  any(   (x == '-') or (x == 'm') or (x == 'w') or (x == 'd') for x in a4):
                        a5 = dict_swap['tenor'][i1].get()
                    else:
                        a5 = int(dict_swap['tenor'][i1].get())
                    
                    a6 = np.float(dict_swap['not'][i1].get())*1000000
                
                    f1 = Swap_Pricer([[crv[a1],a3,a5,a6]])
                    if str(crv[a1].ccy) == 'GBP':
                        fx = 1.0
                    else:
                        fx = con.ref('GBP'+str(crv[a1].ccy)+' Curncy','PX_LAST')['value'][0]

                    dict_swap['swapentry'][i1].insert(0, dict_swap['tenor'][i1].get())
                    dict_swap['swaprate'][i1].insert(0, np.round(np.float(f1.rate[0]),4))
                    dict_swap['bp01'][i1].insert(0, np.round(np.float(f1.dv01[0]),2))
                    dict_swap['risk_l'][i1].insert(0, int(f1.risk[0]))
                    dict_swap['risk_gbp'][i1].insert(0, int(np.float(dict_swap['risk_l'][i1].get())/fx))
                    dict_swap['fix'][i1].insert(0, ccy(a1,today).fixing )
                    dict_swap['fixf'][i1].insert(0, str(ccy(a1,today).fixed[0]) )
                    dict_swap['fltf'][i1].insert(0, str(ccy(a1,today).floating[0]) )
        
                    d1.append(dict_swap['strategy'][i1].get())
                    w1.append(np.float(dict_swap['weights'][i1].get()))
                    r1.append(np.float(dict_swap['swaprate'][i1].get()))
                else:
                    d1.append("")
                    w1.append(0.0)
                    r1.append(0.0)
                    
            d1 = np.array(d1)
            w1 = np.array(w1)
            r1 = np.array(r1)
            d_uniq, d_count = np.unique(d1, return_counts = True)
            for i in d_uniq:
                if i != '':
                    d_index = list(np.where(d1 == i)[0])
                    d_weights = np.array(w1[d_index])
                    d_rates = r1[d_index]
                    d_spreads = 100*np.dot(d_weights, d_rates)
                    dict_swap['spread'][d_index[1]].insert(0, np.round(d_spreads,1))
                    
        
        calc_button = ttk.Button(self, text="Calc", width = 20, command = CalcButton )
        calc_button.grid(column=7, row=3, columnspan=2, sticky=tk.W, padx=5, pady=5)

class BFStrikes(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)
        
        label_tab = tk.Label(self, text = "Bond Futures Strike", font = LARGE_FONT, bg='light grey', fg='green')
        label_tab.grid(row = 0, column = 0, columnspan = 5, sticky = 'W')
        
        Fut_label = ttk.Label(self, text = 'Futures')
        Fut_label.grid(row = 1, column = 1 , sticky = 'W')
        Fut_px = ttk.Label(self, text = 'Live PX')
        Fut_px.grid(row = 1, column = 2 , sticky = 'W')
        K1_label = ttk.Label(self, text = 'K1')
        K1_label.grid(row = 1, column = 3 , sticky = 'W')
        D1_label = ttk.Label(self, text = 'D1')
        D1_label.grid(row = 1, column = 4 , sticky = 'W')
        K2_label = ttk.Label(self, text = 'K2')
        K2_label.grid(row = 1, column = 5 , sticky = 'W')
        D2_label = ttk.Label(self, text = 'D1')
        D2_label.grid(row = 1, column = 6 , sticky = 'W')
        Dist_label = ttk.Label(self, text = 'D2-D1')
        Dist_label.grid(row = 1, column = 7 , sticky = 'W')
        
        n_maxrows = 5
        n_maxrows = [str(i) for i in np.arange(n_maxrows)]
        dict_tickers = dict([(key, []) for key in n_maxrows ])
        
        for i in n_maxrows:
            e0 = tk.Entry(self, width=10, name = 'ticker_'+i , bg='beige', relief = 'flat', border = 2)
            e0.grid(row= 2+int(i), column=1, sticky='W')
            dict_tickers[i].append(e0)
            
            e1 = tk.Entry(self, width=10, name = 'fut_px_'+i , bg='light blue', relief = 'flat', border = 2)
            e1.grid(row= 2+int(i), column=2, sticky='W')
            dict_tickers[i].append(e1)
            
            e2 = tk.Entry(self, width=10, name = 'k1_'+i ,  bg='beige', relief = 'flat', border = 2)
            e2.grid(row= 2+int(i), column=3, sticky='W')
            dict_tickers[i].append(e2)
            
            e3 = tk.Entry(self, width=10, name = 'd1_'+i , relief = 'flat', border = 2)
            e3.grid(row= 2+int(i), column=4, sticky='W')
            dict_tickers[i].append(e3)
            
            e4 = tk.Entry(self, width=10, name = 'k2_'+i ,  bg='beige', relief = 'flat', border = 2)
            e4.grid(row= 2+int(i), column=5, sticky='W')
            dict_tickers[i].append(e4)
            
            e5 = tk.Entry(self, width=10, name = 'd2_'+i , relief = 'flat', border = 2)
            e5.grid(row= 2+int(i), column=6, sticky='W')
            dict_tickers[i].append(e5)
            
            e6 = tk.Entry(self, width=10, name = 'dist_'+i , relief = 'flat', border = 2)
            e6.grid(row= 2+int(i), column=7, sticky='W')
            dict_tickers[i].append(e6)
        
        def CalcButton():
            for i in n_maxrows:
                dict_tickers[i][1].delete(0, tk.END)
                dict_tickers[i][3].delete(0, tk.END)
                dict_tickers[i][5].delete(0, tk.END)
                dict_tickers[i][6].delete(0, tk.END)
            
            for i in n_maxrows:
                t1 =  str(dict_tickers[i][0].get())
                if t1 != '':
                    k1 = dict_tickers[i][2].get()
                    k2 = dict_tickers[i][4].get()
                    if k2 == '':
                        tab1 = bond_fut_yield(t1,[np.float(k1)])
                    else:
                        tab1 = bond_fut_yield(t1,[np.float(k1),np.float(k2)])
                        dict_tickers[i][5].insert(0, np.round(tab1['K_Dist'][1],1))
                        dict_tickers[i][6].insert(0, np.round(tab1['K_Dist'][1]-tab1['K_Dist'][0],1))

                    dict_tickers[i][1].insert(0, tab1['Fut_Px'][0])
                    dict_tickers[i][3].insert(0, np.round(tab1['K_Dist'][0],1))
            
        calc_button = ttk.Button(self, text="Calc", width = 20, command = CalcButton )
        calc_button.grid(column=8, row=1, columnspan=2, sticky=tk.W, padx=5, pady=5)

class InfFix(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)        
        
        label_tab = tk.Label(self, text = "Inflation Fixings", font = LARGE_FONT, bg = 'light grey', fg = 'purple')
        label_tab.grid(row = 0, column = 0, columnspan = 5, sticky = 'W')
        
        uscpi_label = ttk.Label(self, text = 'USCPI')
        uscpi_label.grid(row = 1, column = 2 , columnspan = 3, sticky = 'W')
        ukrpi_label = ttk.Label(self, text = 'UKRPI')
        ukrpi_label.grid(row = 1, column = 5 , columnspan = 3, sticky = 'W')
        hicpxt_label = ttk.Label(self, text = 'HICPxT')
        hicpxt_label.grid(row = 1, column = 8 , columnspan = 3, sticky = 'W')

        FixMonth = ttk.Label(self, text = 'Month')
        FixMonth.grid(row = 2, column = 1 , sticky = 'W')
        
        uscpi_seas = ttk.Label(self, text = 'Seas')
        uscpi_seas.grid(row = 2, column = 2 , sticky = 'W')
        uscpi_mkt = ttk.Label(self, text = 'Mkt')
        uscpi_mkt.grid(row = 2, column = 3 , sticky = 'W')
        uscpi_barx = ttk.Label(self, text = 'Barx')
        uscpi_barx.grid(row = 2, column = 4 , sticky = 'W')
        
        ukrpi_seas = ttk.Label(self, text = 'Seas')
        ukrpi_seas.grid(row = 2, column = 5 , sticky = 'W')
        ukrpi_mkt = ttk.Label(self, text = 'Mkt')
        ukrpi_mkt.grid(row = 2, column = 6 , sticky = 'W')
        ukrpi_barx = ttk.Label(self, text = 'Barx')
        ukrpi_barx.grid(row = 2, column = 7 , sticky = 'W')

        hicpxt_seas = ttk.Label(self, text = 'Seas')
        hicpxt_seas.grid(row = 2, column = 8 , sticky = 'W')
        hicpxt_mkt = ttk.Label(self, text = 'Mkt')
        hicpxt_mkt.grid(row = 2, column = 9 , sticky = 'W')
        hicpxt_barx = ttk.Label(self, text = 'Barx')
        hicpxt_barx.grid(row = 2, column = 10 , sticky = 'W')
        
        n_maxrows = 13
        n_maxrows = [str(i) for i in np.arange(n_maxrows)]
        dict_tickers = dict([(key, []) for key in n_maxrows ])
        
        time_today = datetime.datetime.now()
        
        for i in n_maxrows:
            e0 = tk.Entry(self, width=10, name = 'fixmonth_'+i , bg='light grey', relief = 'flat', border = 2)
            e0.grid(row= 3+int(i), column=1, sticky='E')
            dict_tickers[i].append(e0)
            m1 = time_today - datetime.timedelta(30*(2-int(i)))
            m2 = ql.Date(1,m1.month,m1.year)
            dict_tickers[i].append(m2)
            dict_tickers[i][0].insert(0, m1.strftime("%b-%y"))
            
            e1 = tk.Entry(self, width=10, name = 'uscpi_seas_'+i , relief = 'flat', border = 2)
            e1.grid(row= 3+int(i), column=2, sticky='W')
            dict_tickers[i].append(e1)
            e2 = tk.Entry(self, width=10, name = 'uscpi_mkt_'+i , bg='light blue', relief = 'flat', border = 2)
            e2.grid(row= 3+int(i), column=3, sticky='W')
            dict_tickers[i].append(e2)
            e3 = tk.Entry(self, width=10, name = 'uscpi_barx_'+i,  bg='beige', relief = 'flat', border = 2)
            e3.grid(row= 3+int(i), column=4, sticky='W')
            dict_tickers[i].append(e3)
            
            e4 = tk.Entry(self, width=10, name = 'ukrpi_seas_'+i , relief = 'flat', border = 2)
            e4.grid(row= 3+int(i), column=5, sticky='W')
            dict_tickers[i].append(e4)
            e5 = tk.Entry(self, width=10, name = 'ukrpi_mkt_'+i , bg='light blue', relief = 'flat', border = 2)
            e5.grid(row= 3+int(i), column=6, sticky='W')
            dict_tickers[i].append(e5)
            e6 = tk.Entry(self, width=10, name = 'ukrpi_barx_'+i, bg='beige', relief = 'flat', border = 2)
            e6.grid(row= 3+int(i), column=7, sticky='W')
            dict_tickers[i].append(e6)
            
            e7 = tk.Entry(self, width=10, name = 'hicpxt_seas_'+i , relief = 'flat', border = 2)
            e7.grid(row= 3+int(i), column=8, sticky='W')
            dict_tickers[i].append(e7)
            e8 = tk.Entry(self, width=10, name = 'hicpxt_mkt_'+i , bg='light blue', relief = 'flat', border = 2)
            e8.grid(row= 3+int(i), column=9, sticky='W')
            dict_tickers[i].append(e8)
            e9 = tk.Entry(self, width=10, name = 'hicpxt_barx_'+i, bg='beige', relief = 'flat', border = 2)
            e9.grid(row= 3+int(i), column=10, sticky='W')
            dict_tickers[i].append(e9)
            
            
        def CalcButton():
            for i in n_maxrows:
                for j in np.arange(3):
                    dict_tickers[i][2+(3*j)].delete(0, tk.END )
                    dict_tickers[i][3+(3*j)].delete(0, tk.END )
                    dict_tickers[i][4+(3*j)].delete(0, tk.END )
            
            inf_ticker = ['USCPI','UKRPI','HICPxT']
            inf_fixings =  dict([(key, []) for key in inf_ticker ])
            for i1 in inf_ticker:
                print(i1)
                try:
                    inf_h = infl_zc_swap_build(i1,b=0)
                except: 
                    inf_h = infl_zc_swap_build(i1,b=-1)
                for i2 in np.arange(3):
                    inf_crv = inf_h.curve[i2]
                    inf_crv['yoy'] = 100*inf_crv['index'].pct_change(periods = 12)
                    inf_fixings[i1].append(inf_crv)
            
            for i in n_maxrows[:8]:
                for j1, j2 in enumerate(inf_ticker):
                    dict_tickers[i][2+(3*j1)].insert(0, np.round( inf_fixings[j2][0][inf_fixings[j2][0]['months'] ==  dict_tickers[i][1] ]['yoy'].tolist()[0], 2) )
                    dict_tickers[i][3+(3*j1)].insert(0, np.round( inf_fixings[j2][1][inf_fixings[j2][1]['months'] == dict_tickers[i][1] ]['yoy'].tolist()[0], 2) )
                    dict_tickers[i][4+(3*j1)].insert(0, np.round( inf_fixings[j2][2][inf_fixings[j2][2]['months'] == dict_tickers[i][1] ]['yoy'].tolist()[0], 2) )
                    
            for i in n_maxrows[8:]:
                for j1, j2 in enumerate(inf_ticker):
                    dict_tickers[i][2+(3*j1)].insert(0, np.round( inf_fixings[j2][0][inf_fixings[j2][0]['months'] ==  dict_tickers[i][1] ]['yoy'].tolist()[0], 2) )
                    dict_tickers[i][3+(3*j1)].insert(0, np.round( inf_fixings[j2][1][inf_fixings[j2][1]['months'] == dict_tickers[i][1] ]['yoy'].tolist()[0], 2) )
            
        calc_button = ttk.Button(self, text="Calc", width = 20, command = CalcButton )
        calc_button.grid(column=15, row=1, columnspan=2, sticky=tk.W, padx=5, pady=5)

class InfSwapPricer(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)            
        
        label_tab = tk.Label(self, text = "Inflation Swaps ZC Pricer ", font = LARGE_FONT, bg = 'light grey', fg='purple')
        label_tab.grid(row = 0, column = 0,  columnspan = 5, sticky = 'W')
        
        InfCurveLabel = ttk.Label(self, text = 'Infl Curve: ')
        InfCurveLabel.grid(row = 2, column = 0,  sticky = 'E' )
        InfCurveDateLabel = ttk.Label(self, text = 'Curve Date: ')
        InfCurveDateLabel.grid(row = 3, column = 0, padx = 10, sticky = 'E')
        InfCurveSelectLabel = ttk.Label(self, text = 'Curve: ')            ####### big name changes when class -ed
        InfCurveSelectLabel.grid(row = 4, column = 0,  sticky = 'E' )
        InfFixingCurveLabel = ttk.Label(self, text = 'Fixing Curve: ')     ####### big name changes when class -ed
        InfFixingCurveLabel.grid(row = 5, column = 0,  sticky = 'E' )
        
        InfSwap = ttk.Label(self, text = 'ZC Swap:    ')
        InfSwap.grid(row = 6, column = 0 , sticky = 'E')
        InfStartDate_Label = ttk.Label(self, text = 'Start Date/ Base: ')
        InfStartDate_Label.grid(row = 7, column = 0, padx = 10, sticky = 'E')
        InfLag_Label = ttk.Label(self, text = 'Lag: ')
        InfLag_Label.grid(row = 8, column = 0, padx = 10, sticky = 'E')
        InfTenor_Label = ttk.Label(self, text = 'Tenor: ')
        InfTenor_Label.grid(row = 9, column = 0, padx = 10, sticky = 'E')
        InfBaseMonth_Label = ttk.Label(self, text = 'Base Month: ')
        InfBaseMonth_Label.grid(row = 10, column = 0, padx = 10, sticky = 'E')
        InfBaseFix_Label = ttk.Label(self, text = 'Base Fix: ')
        InfBaseFix_Label.grid(row = 11, column = 0, padx = 10, sticky = 'E')
        InfRate = ttk.Label(self, text = 'ZC Rate:    ')
        InfRate.grid(row = 12, column = 0 , sticky = 'E')
        Inf01 = ttk.Label(self, text = 'Inf01:    ')
        Inf01.grid(row = 13, column = 0 , sticky = 'E')
        InfNot_Label = ttk.Label(self, text = 'Notional (mm): ')
        InfNot_Label.grid(row = 14, column = 0, padx = 10, sticky = 'E')
        InfRiskL = ttk.Label(self, text = 'Risk (Native):    ')
        InfRiskL.grid(row = 15, column = 0 , sticky = 'E')
        InfRiskGBP = ttk.Label(self, text = 'Risk (GBP):    ')
        InfRiskGBP.grid(row = 16, column = 0 , sticky = 'E')
        InfFixing = ttk.Label(self, text = 'Fixing:    ')
        InfFixing.grid(row = 17, column = 0 , sticky = 'E')
        InfLFM = ttk.Label(self, text = 'Last Fixing Month:    ')
        InfLFM.grid(row = 18, column = 0 , sticky = 'E')
        InfInterp = ttk.Label(self, text = 'Interp:    ')
        InfInterp.grid(row = 19, column = 0 , sticky = 'E')
        InfStrat = ttk.Label(self, text = 'Strategy:    ')
        InfStrat.grid(row = 20, column = 0 , sticky = 'E')
        InfWeights = ttk.Label(self, text = 'Weights:    ')
        InfWeights.grid(row = 21, column = 0 , sticky = 'E')
        InfSpreads = ttk.Label(self, text = 'Spread / Fly:    ')
        InfSpreads.grid(row = 22, column = 0 , sticky = 'E')
        
        ###### build curve
        InfCurveEntry = ttk.Entry(self, width = 50)
        InfCurveEntry.insert(0, "UKRPI")
        InfCurveEntry.grid(row = 2, column = 1 , columnspan=5, sticky = 'W')
        
        InfCurveDateEntry = ttk.Entry(self, width = 10)
        InfCurveDateEntry.insert(0, 0)
        InfCurveDateEntry.grid(row = 3, column = 1,  sticky = 'W')
        
        Msg_Build = ttk.Label(self, text = '')
        Msg_Build.grid(row = 2, column = 8,  sticky = 'E' )
        
        
        ###### pricing swaps
        n_max = 9
        n_max = [str(i) for i in np.arange(n_max)]
        dict_infcurves = dict([(key, []) for key in n_max ])
        for i in n_max:
            m1 = tk.StringVar(self)
            infcurveselect = ttk.Combobox(self, width = 10, textvariable = m1, name = 'infcurveselect'+'_'+i )
            infcurveselect['values'] = ('UKRPI', 'HICPxT', 'FRCPI', 'USCPI')
            infcurveselect.grid(row = 4, column = 1+int(i))
            dict_infcurves[i].append(infcurveselect)
            
            m2 = tk.StringVar(self)
            infsubcurveselect = ttk.Combobox(self, width = 10, textvariable = m2, name = 'infsubcurveselect'+'_'+i )
            infsubcurveselect['values'] = ('Seasonals', 'Market', 'BARX')
            infsubcurveselect.grid(row = 5, column = 1+int(i))
            dict_infcurves[i].append(infsubcurveselect)
            
        n = 9 # number of "active swaps" to be price
        n = [str(i) for i in np.arange(n)]
        dict_infswap = dict([(key, []) for key in ['swapentry','startdate','lag','tenor','base_month','base_fix','zc_rate','inf01','not','risk_l','risk_gbp','fix','last_fm','interp','strategy','weights','spread']])
        
        for j1, j2 in enumerate(dict_infswap.keys()):
            for i1, i2 in enumerate(n):
                if any(x == j2 for x in ['swapentry','base_month','base_fix','inf01','risk_l','risk_gbp']):
                    e = tk.Entry(self, width=10, name = j2+'_'+i2 , bg='light blue', relief = 'flat', border = 2)
                elif any(x == j2 for x in ['fix','last_fm','interp']):
                    e = tk.Entry(self, width=10, name = j2+'_'+i2 , bg='beige', relief = 'flat', border = 2)
                elif j2 == 'zc_rate':
                    e = tk.Entry(self, width=10, name = j2+'_'+i2 , bg='light blue', relief = 'flat', border = 2, fg = 'red')
                elif j2 == 'lag':
                    e = tk.Entry(self, width=10, name = j2+'_'+i2)
                    e.insert(0, 3)
                elif j2 == 'not':
                    e = tk.Entry(self, width=10, name = j2+'_'+i2)
                    e.insert(0, 100)
                elif j2 == 'tenor':
                    e = tk.Entry(self, width=10, name = j2+'_'+i2)
                    e.insert(0, 5)
                elif j2 == 'startdate':
                    e = tk.Entry(self, width=10, name = j2+'_'+i2)
                    e.insert(0, '3m')
                elif j2 == 'strategy':
                    e = tk.Entry(self, width=10, name = j2+'_'+i2 , bg='light green', relief = 'flat', border = 2)
                elif j2 == 'weights':
                    e = tk.Entry(self, width=10, name = j2+'_'+i2 , bg='light green', relief = 'flat', border = 2)
                    e.insert(0, 0)
                elif j2 == 'spread':
                    e = tk.Entry(self, width=10, name = j2+'_'+i2 , bg='light green', relief = 'flat', border = 2, fg = 'red')
                    
                e.grid(row=6+j1, column=1+i1, sticky='W')
                dict_infswap[j2].append(e)
                

        def BuildButton():
            a1 = str(InfCurveEntry.get())
            a2 = [item.strip() for item in a1.split(',')]
            
            if len(InfCurveDateEntry.get()) < 4:
                a3 = int(InfCurveDateEntry.get())
            else:
                a3 = InfCurveDateEntry.get()
            
            today = ql.Date(datetime.datetime.now().day,datetime.datetime.now().month,datetime.datetime.now().year)
            now = datetime.datetime.now()
            current_time = now.strftime("%H:%M:%S")
            
            global inf_crv
            inf_crv = dict([(key, []) for key in a2])
            for i in np.arange(len(a2)):
                inf_crv[a2[i]] = infl_zc_swap_build(a2[i], b = a3)
            
            print(inf_crv)
            Msg_Build['text'] = "Done @"+current_time

        build_button = ttk.Button(self, text="Build", width = 20, command = BuildButton )
        build_button.grid(column=6, row=2, columnspan=2, sticky=tk.W, padx=5, pady=5)
        
        def CalcButton():
            today = ql.Date(datetime.datetime.now().day,datetime.datetime.now().month,datetime.datetime.now().year)
            ###### deleting old values upon re-CALC
            for i in dict_infswap.keys():
                if any(x == i for x in ['swapentry','base_month','base_fix','zc_rate','inf01','risk_l','risk_gbp','fix','last_fm','interp','spread']):
                    for j in np.arange(len(n)):
                        dict_infswap[i][j].delete(0, tk.END)
                    
            inf_d1 = []
            inf_w1 = []
            inf_r1 = []
            
            for i1, i2 in enumerate(dict_infcurves.keys()):
                a1 = str(dict_infcurves[i2][0].get())
                if a1 != '':
                    a2 = str(dict_infswap['startdate'][i1].get())
                
                    if  any(   (x == '-') or (x == 'm') or (x == 'w') or (x == 'd') for x in a2):
                        a3 = dict_infswap['startdate'][i1].get()
                    else:
                        a3 = int(dict_infswap['startdate'][i1].get())
                
                    a4 = int(dict_infswap['tenor'][i1].get())
                    a5 = int(dict_infswap['lag'][i1].get())
                    
                    a6 = np.float(dict_infswap['not'][i1].get())
                    
                    a7=0
                    a8=0
                    if str(dict_infcurves[i2][1].get()) == 'Market':
                        a7 = 1
                    if str(dict_infcurves[i2][1].get()) == 'BARX':
                        a8 = 1
                
                    f1 = Infl_ZC_Pricer(inf_crv[a1], a3, a4, lag = a5, not1 = a6 , use_forecast = a8, use_mkt_fixing = a7)
                    
                    if str(inf_crv[a1].ccy) == 'GBP':
                        fx = 1.0
                    else:
                        fx = con.ref('GBP'+str(inf_crv[a1].ccy)+' Curncy','PX_LAST')['value'][0]

                    dict_infswap['swapentry'][i1].insert(0, dict_infswap['tenor'][i1].get())
                    dict_infswap['base_month'][i1].insert(0, ql_to_datetime(f1.base).strftime("%b-%y") )
                    dict_infswap['base_fix'][i1].insert(0, np.round(f1.base_fixing,2))
                    dict_infswap['zc_rate'][i1].insert(0,  np.round(f1.zc_rate,3))
                    dict_infswap['inf01'][i1].insert(0,  f1.inf01)
                    dict_infswap['risk_l'][i1].insert(0,  f1.risk)
                    dict_infswap['risk_gbp'][i1].insert(0,  int(np.float(f1.risk)/fx))
                    dict_infswap['fix'][i1].insert(0, f1.index)
                    dict_infswap['last_fm'][i1].insert(0, ql_to_datetime(f1.last_fm).strftime("%b-%y") )
                    dict_infswap['interp'][i1].insert(0, f1.interp)
        
                    inf_d1.append(dict_infswap['strategy'][i1].get())
                    inf_w1.append(np.float(dict_infswap['weights'][i1].get()))
                    inf_r1.append(np.float(dict_infswap['zc_rate'][i1].get()))
                
                else:
                    inf_d1.append("")
                    inf_w1.append(0.0)
                    inf_r1.append(0.0)
                    
            inf_d1 = np.array(inf_d1)
            inf_w1 = np.array(inf_w1)
            inf_r1 = np.array(inf_r1)
            d_uniq_inf, d_count_ifn = np.unique(inf_d1, return_counts = True)
            for i in d_uniq_inf:
                if i != '':
                    d_index = list(np.where(inf_d1 == i)[0])
                    d_weights = np.array(inf_w1[d_index])
                    d_zcrates = inf_r1[d_index]
                    d_spreads = 100*np.dot(d_weights, d_zcrates)
                    dict_infswap['spread'][d_index[1]].insert(0, np.round(d_spreads,1))
                    
        
        calc_button = ttk.Button(self, text="Calc", width = 20, command = CalcButton )
        calc_button.grid(column=6, row=3, columnspan=2, sticky=tk.W, padx=5, pady=5)

class InfMon1(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)
        
        label_tab = tk.Label(self, text = "Linker Monitor", font = LARGE_FONT, bg="light grey", fg = 'purple')
        label_tab.grid(row = 0, column = 0, columnspan = 5, sticky = 'W')
        
        LinkerDBLabel = ttk.Label(self, text = 'Linker DB: ')
        LinkerDBLabel.grid(row = 2, column = 0 )
        m = tk.StringVar(self)
        LinkerDB = ttk.Combobox(self, width = 15, textvariable = m, name = 'infdbselect')
        LinkerDB['values'] = ('tips','euro_linker','ukti')
        LinkerDB.grid(row = 2, column = 1)
        
        DateLabel = ttk.Label(self, text = 'As of Date: ')
        DateLabel.grid(row = 3, column = 0, padx = 10)
        DateEntry = ttk.Entry(self, width = 10)
        DateEntry.insert(0, 0)
        DateEntry.grid(row = 3, column = 1,  sticky = 'W')

        OffsetDaysLabel = ttk.Label(self, text = 'Offsets: ')
        OffsetDaysLabel.grid(row = 4, column = 0, padx = 10)
        OffsetDaysEntry = ttk.Entry(self, width = 10)
        OffsetDaysEntry.insert(0, "-1")
        OffsetDaysEntry.grid(row = 4, column = 1,  sticky = 'W')
        
        RepoLabel = ttk.Label(self, text = 'Repo: ')
        RepoLabel.grid(row = 5, column = 0, padx = 10)
        RepoEntry = ttk.Entry(self, width = 10)
        RepoEntry.insert(0, -0.5)
        RepoEntry.grid(row = 5, column = 1,  sticky = 'W')
        
        FixCrvSelectLabel = ttk.Label(self, text = 'Fixing Curve: ')
        FixCrvSelectLabel.grid(row = 6, column = 0 )
        m1 = tk.StringVar(self)
        FixCrvSelect = ttk.Combobox(self, width = 15, textvariable = m1, name = 'fixing_curve_selct')
        FixCrvSelect['values'] = ('BARX','Market','Seasonals')
        FixCrvSelect.grid(row = 6, column = 1)
        
        CountryFiltLabel = ttk.Label(self, text = 'Country: ')
        CountryFiltLabel.grid(row = 7, column = 0, padx = 10)
        CountryFiltEntry = ttk.Entry(self, width = 10)
        CountryFiltEntry.grid(row = 7, column = 1,  sticky = 'W')
        
        IdxFiltLabel = ttk.Label(self, text = 'Index: ')
        IdxFiltLabel.grid(row = 8, column = 0, padx = 10)
        IdxFiltEntry = ttk.Entry(self, width = 10)
        IdxFiltEntry.grid(row = 8, column = 1,  sticky = 'W')
       
        Msg_Build = ttk.Label(self, text = '')
        Msg_Build.grid(row = 2, column = 3,  sticky = 'E' )

        def BuildButton():
            f = ttk.Frame(self)
            f.grid(column=2, row=10, columnspan = 8, padx=5, pady=5,  sticky = 'nsew')
            tb_width = f.winfo_screenwidth() * 0.4
            tb_height = f.winfo_screenheight() * 0.6

            a1 = str(LinkerDB.get())
            if a1 == 'tips':
                a2 = 'SOFR_DC'
            elif a1 == 'euro_linker':
                a2 = 'ESTER_DC'
            elif a1 == 'ukti':
                a2 = 'SONIA_DC'
            
            os.chdir('C:\\Users\A00007579\OneDrive - Allianz Global Investors\Documents\Python archive\DataLake') 
            db = pd.read_pickle(a1)
            os.chdir('C:\\Users\A00007579\OneDrive - Allianz Global Investors\Documents\Python archive\Swaps') 

            if len(DateEntry.get()) < 4:
                a3 = int(DateEntry.get())
            else:
                a3 = DateEntry.get()
                
            if len(OffsetDaysEntry.get()) < 4:
                a4 = int(OffsetDaysEntry.get())
            else:
                a4 = OffsetDaysEntry.get()
            
            today = ql.Date(datetime.datetime.now().day,datetime.datetime.now().month,datetime.datetime.now().year)
            now = datetime.datetime.now()
            current_time = now.strftime("%H:%M:%S")

            df = linker_table(a2, db, repo_rate = np.float(RepoEntry.get()), b=a3, chg=a4, country_filter = CountryFiltEntry.get(), index_filter = IdxFiltEntry.get(), fixing_curve = 'BARX')
            df = df.round({'Px': 2, 'Yield': 3, 'Δ_adj': 1, 'BEI': 1, 'Δ_BEI_adj': 1, 'Nom_Yld': 3, 'Δ_Nom': 1})
            
            pt = Table(f, dataframe=df, showtoolbar=True, height = tb_height, width = tb_width, showstatusbar=True)
            pt.setColumnColors(cols=[1], clr='#f5f5dc')
            pt.setColumnColors(cols=[5,6], clr='#d4ebf2')
            pt.show()
            Msg_Build['text'] = "Done @"+current_time
            
        calc_button = ttk.Button(self, text="Build", width = 14, command = BuildButton )
        calc_button.grid(column=1, row=1, rowspan = 1, columnspan = 2, sticky=tk.W, pady=5)

class OptChain(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)             
        
        label_tab = tk.Label(self, text = "Options Chain", font = LARGE_FONT, bg = 'light grey', fg='green')
        label_tab.grid(row = 0, column = 0, columnspan = 5, sticky = 'W')
        
        today = ql.Date(datetime.datetime.now().day,datetime.datetime.now().month,datetime.datetime.now().year)
        FUT_CT = {'1': 'F', '2': 'G', '3': 'H', '4': 'J','5': 'K','6': 'M','7': 'N','8': 'Q','9': 'U','10': 'V','11': 'X','12': 'Z'}   
        FUT_M = pd.DataFrame()
        d1 = ql.Date(15,today.month(),today.year())
        s1 = pd.Series([d1+ql.Period(i,ql.Months) for i in range(12) ])
        a2 = s1.tolist()[(3-d1.month()%3)%3]
        s2 = s1.append(pd.Series([a2+ql.Period(3*i,ql.Months) for i in range(1,12) ]))
    
        FUT_M['Date'] = pd.Series(s1.tolist())
        FUT_M['TickerMonth'] = pd.Series([FUT_CT[str(FUT_M['Date'][i].month())]+str(FUT_M['Date'][i].year())[-1:] for i in range(len(FUT_M))])
        FUT_M['BondMonth'] =  pd.Series([True, True, True] + [any(x == FUT_M['TickerMonth'][i][0] for x in ['H','M','U','Z']) for i in np.arange(3,len(FUT_M))] )
        t1 = [FUT_M['TickerMonth'][i] for i in np.arange(len(FUT_M))]
        ticker_list_bonds = ['FV','TY','US','WN','1I','2I','3I','4I','5I','1M','2M','3M','4M','5M','1C','2C','3C','4C','5C','1J','2J','3J','4J','5J','DU','OE','RX','UB']
        ticker_list_stir =  ['ED','0E','2E','3E','4E','ER','0R','2R','3R','4R','SFI','0N','2N','3N','4N']
        strikes_list = [119,128,158,188] + flat_lst([[i]*5 for i in [119,128,158,188]]) + [112, 133, 170, 204] + flat_lst([[i]*5 for i in [99,100,99]])
        
        t1_lst = tk.Listbox(self, width=7, height=60, exportselection=0, selectbackground='dark blue')
        t1_lst.grid(column=0, row=2, rowspan = 150, columnspan=1, sticky = 'W', padx=5)
        m = ticker_list_bonds + ticker_list_stir
        for index, element in enumerate(m):
            t1_lst.insert(index, element)
        
        t2_lst = tk.Listbox(self, width=7, height=60, exportselection=0, selectbackground='dark green')
        t2_lst.grid(column=1, row=2, rowspan = 150, columnspan=1, sticky = 'W', padx=5)
        for index, element in enumerate(t1):
            t2_lst.insert(index, element)
        
        OptChainLabel = ttk.Label(self, text = 'Option Chain: ')
        OptChainLabel.grid(row = 2, column = 2 , sticky = 'E')
        OptChainEntry = tk.Entry(self, width = 20, fg='dark blue')
#        OptChainEntry.insert(0, "TYH2P 129")
        OptChainEntry.grid(row = 2, column = 3 , sticky = 'W')
        
        ChLenLabel = ttk.Label(self, text = 'Chain Length: ')
        ChLenLabel.grid(row = 3, column = 2, sticky = 'E')
        ChLenEntry = ttk.Entry(self, width = 10)
        ChLenEntry.insert(0, "12, 12")
        ChLenEntry.grid(row = 3, column = 3,  sticky = 'W')

        OptChainDateLabel = ttk.Label(self, text = 'Date / Offset: ')
        OptChainDateLabel.grid(row = 4, column = 2, sticky = 'E')
        OptChainDateEntry = ttk.Entry(self, width = 10)
        OptChainDateEntry.insert(0, 0)
        OptChainDateEntry.grid(row = 4, column = 3,  sticky = 'W')
        
        SpotPxLabel = ttk.Label(self, text = 'Fut Px: ')
        SpotPxLabel.grid(row = 5, column = 2, sticky = 'E')
        SpotPxEntry = ttk.Entry(self, width = 10)
        SpotPxEntry.grid(row = 5, column = 3,  sticky = 'W')

        ExpDtLabel = ttk.Label(self, text = 'Expiry Date: ')
        ExpDtLabel.grid(row = 6, column = 2, sticky = 'E')
        ExpDtEntry = ttk.Entry(self, width = 20)
        ExpDtEntry.grid(row = 6, column = 3,  sticky = 'W')
        
        FakeLabel = ttk.Label(self, text = '')
        FakeLabel.grid(row = 7, column = 2, sticky = 'E')


        def CalcButton():
            f = tk.Frame(self)
            f.grid(column=3, row=8, sticky = 'nsew')
            tb_width = f.winfo_screenwidth() * 0.5
            tb_height = f.winfo_screenheight() * 0.59
            
            SpotPxEntry.delete(0, tk.END)
            ExpDtEntry.delete(0, tk.END)
            OptChainEntry.delete(0, tk.END)
            a1 = str(t1_lst.get(t1_lst.curselection()[0]))+str(t2_lst.get(t2_lst.curselection()[0]))+'P '+str(strikes_list[t1_lst.curselection()[0]] )
            OptChainEntry.insert(0, a1)

            a2 = [item.strip() for item in a1.split(',')]
            a3 = str(ChLenEntry.get())
            a4 = [int(d) for d in re.findall(r'-?\d+', a3)]
            a5 = str(OptChainDateEntry.get())
            a6 = [item.strip() for item in a5.split(',')]
            a7 = []
            for i in a6:
                if len(i) < 4:
                    a7 = a7 + [int(i)]
                else:
                    a7 = a7 + [i]
            try:
                v1 = build_vol_surf(a2, chain_len=a4, b = a7[0])
                SpotPxEntry.insert(0, v1.spot_px_fmt)

            except:
                v1 = build_stir_vol_surf(a2, chain_len=a4, b = a7[0])
                SpotPxEntry.insert(0, v1.spot_px)
            df = v1.tab
            ExpDtEntry.insert(0, v1.expiry_dt)

            df = df.round({'px': 2, 'Yld': 3, 'ATM_K': 1, 'bs_px': 2, 'iv': 2, 'delta': 1, 'gamma': 2, 'theta': 1, 'vega': 1})
            
            pt = Table(f, dataframe=df, showtoolbar=True, height = tb_height, width = tb_width, showstatusbar=True)
            pt.setColumnColors(cols=[4], clr='#d4ebf2')
            pt.show()

#            text = tk.Text(self, width = 150, height=70, font=('Consolas', 8) )
#            text.insert(tk.END, str(tabulate(df, headers='keys', tablefmt='github', showindex=False )))
#            text.grid(row=7, column=2, columnspan = 12  ,sticky = 'nsew', padx=5, pady=5)
            
        calc_button = ttk.Button(self, text="Calc", width = 19, command = CalcButton )
        calc_button.grid(column=3, row=1, rowspan = 1, columnspan = 1, sticky=tk.W,  pady=5)

class OptVol(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)
        
        label_tab1 = tk.Label(self, text = "Options Vol", font = LARGE_FONT, bg = 'light grey', fg = 'green')
        label_tab1.grid(row = 0, column = 0, columnspan = 5, sticky = 'W')
        
        today = ql.Date(datetime.datetime.now().day,datetime.datetime.now().month,datetime.datetime.now().year)
        FUT_CT = {'1': 'F', '2': 'G', '3': 'H', '4': 'J','5': 'K','6': 'M','7': 'N','8': 'Q','9': 'U','10': 'V','11': 'X','12': 'Z'}   
        FUT_M = pd.DataFrame()
        d1 = ql.Date(15,today.month(),today.year())
        s1 = pd.Series([d1+ql.Period(i,ql.Months) for i in range(12) ])
        a2 = s1.tolist()[(3-d1.month()%3)%3]
        s2 = s1.append(pd.Series([a2+ql.Period(3*i,ql.Months) for i in range(1,12) ]))
    
        FUT_M['Date'] = pd.Series(s1.tolist())
        FUT_M['TickerMonth'] = pd.Series([FUT_CT[str(FUT_M['Date'][i].month())]+str(FUT_M['Date'][i].year())[-1:] for i in range(len(FUT_M))])
        FUT_M['BondMonth'] =  pd.Series([True, True, True] + [any(x == FUT_M['TickerMonth'][i][0] for x in ['H','M','U','Z']) for i in np.arange(3,len(FUT_M))] )
        t1 = [FUT_M['TickerMonth'][i] for i in np.arange(len(FUT_M))]
        ticker_list_bonds = ['FV','TY','US','WN','1I','2I','3I','4I','5I','1M','2M','3M','4M','5M','1C','2C','3C','4C','5C','1J','2J','3J','4J','5J','DU','OE','RX','UB']
        ticker_list_stir =  ['ED','0E','2E','3E','4E','ER','0R','2R','3R','4R','SFI','0N','2N','3N','4N']

        strikes_list = [119,128,158,188] + flat_lst([[i]*5 for i in [119,128,158,188]]) + [112, 133, 170, 204] + flat_lst([[i]*5 for i in [99,100,99]])

        t1_lst = tk.Listbox(self, width=7, height=60, exportselection=0, selectbackground='dark blue')
        t1_lst.grid(column=0, row=2, rowspan = 150, columnspan=1, sticky = 'W', padx=5)
        m = ticker_list_bonds + ticker_list_stir
        for index, element in enumerate(m):
            t1_lst.insert(index, element)
        
        t2_lst = tk.Listbox(self, width=7, height=60, exportselection=0, selectbackground='dark green')
        t2_lst.grid(column=1, row=2, rowspan = 150, columnspan=1, sticky = 'W', padx=5)
        for index, element in enumerate(t1):
            t2_lst.insert(index, element)
        
        OptChainLabel = ttk.Label(self, text = 'Option Chain: ')
        OptChainLabel.grid(row = 2, column = 2, sticky = 'E' )
        OptChainEntry = ttk.Entry(self, width = 20)
#        OptChainEntry.insert(0, "TYH2P 129")
        OptChainEntry.grid(row = 2, column = 3 , sticky = 'W')
        
        ChLenLabel = ttk.Label(self, text = 'Chain Length: ')
        ChLenLabel.grid(row = 3, column = 2, sticky = 'E')
        ChLenEntry = ttk.Entry(self, width = 10)
        ChLenEntry.insert(0, "10, 10")
        ChLenEntry.grid(row = 3, column = 3,  sticky = 'W')

        OptChainDateLabel = ttk.Label(self, text = 'Date / Offset: ')
        OptChainDateLabel.grid(row = 4, column = 2, sticky = 'E')
        OptChainDateEntry = ttk.Entry(self, width = 20)
        OptChainDateEntry.insert(0, '0, -1')
        OptChainDateEntry.grid(row = 4, column = 3,  sticky = 'W')
        
        OptTypeLabel = ttk.Label(self, text = 'Opt Type: ')
        OptTypeLabel.grid(row = 5, column = 2, sticky = 'E')
        OptTypeEntry = ttk.Entry(self, width = 10)
        OptTypeEntry.insert(0, 'P')
        OptTypeEntry.grid(row = 5, column = 3,  sticky = 'W')
        
        AxLabel = ttk.Label(self, text = 'K / Delta: ')
        AxLabel.grid(row = 6, column = 2,  sticky = 'E' )
        m = tk.StringVar(self)
        ax1select = ttk.Combobox(self, width = 10, textvariable = m, name = 'opt_vol_ax_select' )
        ax1select['values'] = ('delta', 'strikes')
        ax1select.grid(row = 6, column = 3,  sticky = 'W')
            
        ExpDtLabel = ttk.Label(self, text = 'Expiry Date: ')
        ExpDtLabel.grid(row = 7, column = 2, sticky = 'E')
        ExpDtEntry = ttk.Entry(self, width = 20)
        ExpDtEntry.grid(row = 7, column = 3,  sticky = 'W')


        def CalcButton():
            ExpDtEntry.delete(0, tk.END)
            OptChainEntry.delete(0, tk.END)
            a1 = str(t1_lst.get(t1_lst.curselection()[0]))+str(t2_lst.get(t2_lst.curselection()[0]))+'P '+str(strikes_list[t1_lst.curselection()[0]] )
            OptChainEntry.insert(0, a1)
            
            a2 = [item.strip() for item in a1.split(',')]
            a3 = str(ChLenEntry.get())
            a4 = [int(d) for d in re.findall(r'-?\d+', a3)]
            a5 = str(OptChainDateEntry.get())
            a6 = [item.strip() for item in a5.split(',')]
            a7 = []
            for i in a6:
                if len(i) < 4:
                    a7 = a7 + [int(i)]
                else:
                    a7 = a7 + [i]
            
            vol_surf = []
            for i in a7:
                try:
                    v1 = build_vol_surf(a2, chain_len=a4, b = i)
                except:
                    v1 = build_stir_vol_surf(a2, chain_len=a4, b = i)
                vol_surf = vol_surf + [v1]
                
            ExpDtEntry.insert(0, vol_surf[0].expiry_dt)
            
            f = plot_opt_vol_surf(vol_surf, opt_type = OptTypeEntry.get(), x_ax = ax1select.get() );
            
            canvas = FigureCanvasTkAgg(f, self)
            mplcursors.cursor()
            canvas.draw()
            canvas.get_tk_widget().grid(row=9, column=3, sticky = 'nsew', padx=10, pady=10)
            # navigation toolbar
            toolbarFrame = tk.Frame(self)
            toolbarFrame.grid(row=10,column=3)
            toolbar = NavigationToolbar2Tk(canvas, toolbarFrame)
            
        calc_button = ttk.Button(self, text="Calc", width = 19, command = CalcButton )
        calc_button.grid(column=3, row=1, rowspan = 1, columnspan = 1, sticky=tk.W, pady=5)

class SwapRV(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)
        
        label_tab = tk.Label(self, text = "Swaps RV", font = LARGE_FONT, bg = 'light grey', fg='blue')
        label_tab.grid(row = 0, column = 0, columnspan = 5, sticky = 'W')
        
        CurveLabel = ttk.Label(self, text = 'Curve: ')
        CurveLabel.grid(row = 2, column = 0,  sticky = 'E' )
        CurveDateLabel = ttk.Label(self, text = 'Curve Date: ')
        CurveDateLabel.grid(row = 3, column = 0, padx = 10, sticky = 'E')
        MaxTenorLabel = ttk.Label(self, text = 'Max Tenor: ')
        MaxTenorLabel.grid(row = 4, column = 0, padx = 10, sticky = 'E')
        
        SpotFwd = ttk.Label(self, text = 'Spot/Fwd: ')
        SpotFwd.grid(row = 5, column = 0,  sticky = 'E' )
        
        SwapSt = ttk.Label(self, text = 'Strategy:    ')
        SwapSt.grid(row = 6, column = 0 , sticky = 'E')
        
        StratRate = ttk.Label(self, text = 'Rate:    ')
        StratRate.grid(row = 7, column = 0 , sticky = 'E')
        
        SwapRoll1_Label = ttk.Label(self, text = 'Roll: ')
        SwapRoll1_Label.grid(row = 8, column = 0,  padx = 10, sticky = 'E')        
        SwapRoll2_Label = ttk.Label(self, text = 'Roll: ')
        SwapRoll2_Label.grid(row = 9, column = 0, padx = 10, sticky = 'E')
        SwapRoll3_Label = ttk.Label(self, text = 'Roll: ')
        SwapRoll3_Label.grid(row = 10, column = 0, padx = 10, sticky = 'E')
        SwapRoll4_Label = ttk.Label(self, text = 'Roll: ')
        SwapRoll4_Label.grid(row = 11, column = 0, padx = 10, sticky = 'E')
        
        ###### build curve
        CurveEntry = ttk.Entry(self, width = 20)
        CurveEntry.insert(0, "SOFR_DC")
        CurveEntry.grid(row = 2, column = 1 , columnspan=2, sticky = 'W')
        
        CurveDateEntry = ttk.Entry(self, width = 10)
        CurveDateEntry.insert(0, 0)
        CurveDateEntry.grid(row = 3, column = 1,  sticky = 'W')
        
        MaxTenorEntry = ttk.Entry(self, width = 10)
        MaxTenorEntry.insert(0, 30)
        MaxTenorEntry.grid(row = 4, column = 1,  sticky = 'W')
        
        Msg_Build = ttk.Label(self, text = '')
        Msg_Build.grid(row = 2, column = 8,  sticky = 'E' )
        
        
        ###### rolls entry
        n_rolls = ['1m','3m','6m','12m']
        dict_rolls = dict([(key, []) for key in n_rolls ])
        for i1, i2 in enumerate(n_rolls):
            e_roll = tk.Entry(self, width=5, name = 'roll_'+i2 , bg='beige', relief = 'flat', border = 2)
            e_roll.grid(row = 8+i1 , column = 1)
            e_roll.insert(0,list(dict_rolls.keys())[i1])
            dict_rolls[i2].append(e_roll)
        
        n = 6 # number of "active strats" to be priced
        n = [str(i) for i in np.arange(n)]
        dict_strats = dict([(key, []) for key in ['spotfwd','strategy','rate','roll1_rate','roll2_rate','roll3_rate','roll4_rate']])
        
        for j1, j2 in enumerate(dict_strats.keys()):
            for i1, i2 in enumerate(n):
                if any(x == j2 for x in ['roll1_rate','roll2_rate','roll3_rate','roll4_rate']):
                    e = tk.Entry(self, width=15, name = j2+'_'+i2 , bg='beige', relief = 'flat', border = 2)
                elif j2 == 'rate':
                    e = tk.Entry(self, width=10, name = j2+'_'+i2 , bg='light blue', relief = 'flat', border = 2, fg = 'red')
                elif j2 == 'spotfwd':
                    e = tk.Entry(self, width=10, name = j2+'_'+i2)
                    e.insert(0, 0)
                elif j2 == 'strategy':
                    e = tk.Entry(self, width=30, name = j2+'_'+i2)
                    
                e.grid(row=5+j1, column=2+i1, sticky='W')
                dict_strats[j2].append(e)
                
         
        def BuildButton():
            a1 = [str(CurveEntry.get())]
            if len(CurveDateEntry.get()) < 4:
                a2 = int(CurveDateEntry.get())
            else:
                a2 = CurveDateEntry.get()
            
            today = ql.Date(datetime.datetime.now().day,datetime.datetime.now().month,datetime.datetime.now().year)
            now = datetime.datetime.now()
            current_time = now.strftime("%H:%M:%S")
            
            global crv2
            c = ccy(a1[0],today)
            if c.ois_trigger == 0:
                crv2 = swap_build(a1[0], b = a2)
            else:
                crv2 = ois_dc_build(a1[0], b = a2)
                
            g = plt_ois_curve(c1 = a1, h1 = [a2], max_tenor=int(MaxTenorEntry.get()), bar_chg=0, sprd=0, fwd_tenor = '1y',int_tenor = '1y');
            
            canvas = FigureCanvasTkAgg(g, self)
            mplcursors.cursor()
            canvas.draw()
            canvas.get_tk_widget().grid(row=12, column=2, columnspan = 10, sticky = 'nsew', padx=10, pady=10)
            
            print(crv2)
            Msg_Build['text'] = "Done @"+current_time

        build_button = ttk.Button(self, text="Build", width = 20, command = BuildButton )
        build_button.grid(column=6, row=2, columnspan=2, sticky=tk.W, padx=5, pady=5)
        
        def CalcButton():            
            today = ql.Date(datetime.datetime.now().day,datetime.datetime.now().month,datetime.datetime.now().year)            
            ###### deleting old values upon re-CALC
            for i in dict_strats.keys():
                if any(x == i for x in ['rate','roll1_rate','roll2_rate','roll3_rate','roll4_rate']):
                    for j in np.arange(len(n)):
                        dict_strats[i][j].delete(0, tk.END)
                    
            
            for i1, i2 in enumerate(n):
                a1 = str(dict_strats['strategy'][i1].get())
                if a1 != '':
                    a2 = [item.strip() for item in a1.split(',')]
                    a3 = [ [int(d) for d in re.findall(r'-?\d+', a2[i])] for i in np.arange(len(a2)) ]
                    
                    if dict_strats['spotfwd'][i1].get() == '0':
                        st1 = int(dict_strats['spotfwd'][i1].get())
                    else:
                        st1 = str(dict_strats['spotfwd'][i1].get())
                    
                    if len(a3[0]) == 1:
                        a4 = [[crv2] + [st1] + a3[i] for i in np.arange(len(a3))]
                    else:
                        a4 = [[crv2] + a3[i] for i in np.arange(len(a3))]
                        
#                    print(a4)

                    f1 = Swap_Pricer(a4)
                    if len(a4) == 2:
                        dict_strats['rate'][i1].insert(0, f1.spread)
                    else:
                        dict_strats['rate'][i1].insert(0, f1.fly)
                        
                        
                    if ((len(a3[0]) > 1) or (st1 != 0)):
                        for j1, j2 in enumerate(dict_rolls.keys()):
                            d1 =  [ crv2.cal.advance( f1.dates['Start'].tolist()[i], ql.Period('-'+dict_rolls[j2][0].get() )) for i in np.arange(len(a4)) ]
                            d2 = [ str(d1[i].dayOfMonth())+'-'+str(d1[i].month())+'-'+str(d1[i].year()) for i in np.arange(len(d1)) ]
                            for i in np.arange(len(a4)):
                                a4[i][1] = d2[i]
                            f2 = Swap_Pricer(a4)
                            if len(a4) == 2:
                                dict_strats[ list(dict_strats.keys())[3+j1]   ][i1].insert(0, str(f2.spread)+'    /    '+str( np.round(f2.spread-f1.spread,1)))
                            else:
                                dict_strats[ list(dict_strats.keys())[3+j1]   ][i1].insert(0, str(f2.fly)+'    /    '+str(  np.round(f2.fly-f1.fly,1)))
                    else:
                        for j1, j2 in enumerate(dict_rolls.keys()):
                            d1 =  [ crv2.cal.advance( f1.dates['Start'].tolist()[i], ql.Period(dict_rolls[j2][0].get())) for i in np.arange(len(a4)) ]
                            d2 = [ str(d1[i].dayOfMonth())+'-'+str(d1[i].month())+'-'+str(d1[i].year()) for i in np.arange(len(d1)) ]
                            d3 = f1.dates['End'].tolist()
                            d4 = [ str(d3[i].dayOfMonth())+'-'+str(d3[i].month())+'-'+str(d3[i].year()) for i in np.arange(len(d3)) ]

                            for i in np.arange(len(a4)):
                                a4[i][1] = d2[i]
                                a4[i][2] = d4[i]
                            f2 = Swap_Pricer(a4)
                            if len(a4) == 2:
                                dict_strats[ list(dict_strats.keys())[3+j1]   ][i1].insert(0, str(f2.spread)+'    /    '+str( np.round(f2.spread-f1.spread,1)))
                            else:
                                dict_strats[ list(dict_strats.keys())[3+j1]   ][i1].insert(0, str(f2.fly)+'    /    '+str(  np.round(f2.fly-f1.fly,1)))
                        
        
        calc_button = ttk.Button(self, text="Calc", width = 20, command = CalcButton )
        calc_button.grid(column=6, row=3, columnspan=2, sticky=tk.W, padx=5, pady=5)

class BondCurves(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)               
        
        label_tab = tk.Label(self, text = "Bond Curve", font = LARGE_FONT, bg ='light grey', fg = 'red')
        label_tab.grid(row = 0, column = 0, columnspan = 5, sticky = 'W')
        
        bond_db_lstbox = tk.Listbox(self, selectmode='multiple', width=40, height=50)
        bond_db_lstbox.grid(column=0, row=7, rowspan = 25, columnspan=2, sticky = 'W', padx=5)
        m = ["GERMANY_NOM", "FRANCE_NOM", "UK_NOM", "ITALY_NOM", "SPAIN_NOM", "PORTUGAL_NOM", "IRELAND_NOM", "AUSTRALIA_NOM",
             "CANADA_NOM", "SWEDEN_NOM", "NORWAY_NOM", "POLAND_NOM", "HUNGARY_NOM", "COLOMBIA_NOM_LCL", "MEXICO_NOM_LCL", "PERU_NOM_LCL", "SOUTH_AFRICA_NOM_LCL"]
        for index, element in enumerate(m):
            bond_db_lstbox.insert(index, element)

        CurveDateAndOffsetsLabel = ttk.Label(self, text = 'Curve Date & Offsets: ')
        CurveDateAndOffsetsLabel.grid(row = 2, column = 0, padx = 0, sticky = 'E')
        CurveDateAndOffsetsEntry = ttk.Entry(self, width = 20)
        CurveDateAndOffsetsEntry.insert(0, "0, -1")
        CurveDateAndOffsetsEntry.grid(row = 2, column = 1,  sticky = 'W')

        FwdDatesLabel = ttk.Label(self, text = 'Fwd Dates : ')
        FwdDatesLabel.grid(row = 3, column = 0, padx = 0, sticky = 'E')
        FwdDatesEntry = ttk.Entry(self, width = 20)
        FwdDatesEntry.insert(0, "1M, 3M")
        FwdDatesEntry.grid(row = 3, column = 1,  sticky = 'W')
        
        RepoLabel = ttk.Label(self, text = 'Repo: ')
        RepoLabel.grid(row = 4, column = 0, padx = 0, sticky = 'E')
        RepoEntry = ttk.Entry(self, width = 10)
        RepoEntry.insert(0, 0)
        RepoEntry.grid(row = 4, column = 1,  sticky = 'W')
        
        FwdRepoLabel = ttk.Label(self, text = 'Fwd Repo: ')
        FwdRepoLabel.grid(row = 5, column = 0, padx = 0, sticky = 'E')
        FwdRepoEntry = ttk.Entry(self, width = 10)
        FwdRepoEntry.insert(0, 0)
        FwdRepoEntry.grid(row = 5, column = 1,  sticky = 'W')
        
        fakeLabel = ttk.Label(self, text = '')
        fakeLabel.grid(row = 6, column = 0, padx = 5, sticky = 'E')
               
        def CalcButton():
            a1 =  str(CurveDateAndOffsetsEntry.get())
            a2 = [item.strip() for item in a1.split(',')]
            for i in np.arange(len(a2)):
                if any(x in a2[i] for x in ['m','w','d','M','W','D']) or len(a2[i]) > 4:
                    pass
                else:
                    a2[i] = int(a2[i])
            
            a3 =  str(FwdDatesEntry.get())
            a4 = [item.strip() for item in a3.split(',')]
            for i in np.arange(len(a4)):
                if any(x in a4[i] for x in ['m','w','d','M','W','D']) or len(a4[i]) > 4:
                    pass
                else:
                    a4[i] = int(a4[i])
            print(a2,a4)
            
            a5 = [bond_db_lstbox.get(i) for i in bond_db_lstbox.curselection()]
            print(a5)

            df, g = bond_curve_build(a5, a2, a4, np.float(RepoEntry.get()), np.float(FwdRepoEntry.get()))
           
            for k in np.arange(len(a5)):
                canvas = FigureCanvasTkAgg(g[k], self)
                mplcursors.cursor()
                canvas.draw()
                canvas.get_tk_widget().grid(row=1+(11*k), column=4, rowspan = 10, padx=5, pady=5)
                # navigation toolbar
                toolbarFrame = tk.Frame(self)
                toolbarFrame.grid(row=11+(11*k),column=4)
                toolbar = NavigationToolbar2Tk(canvas, toolbarFrame)
                
                f = ttk.Frame(self)
                f.grid(column=5, row=1+(11*k), columnspan = 8, rowspan = 10, padx=5, pady=5,  sticky = 'nsew')
                tb_width = f.winfo_screenwidth() * 0.25
                tb_height = f.winfo_screenheight() * 0.2
            
                pt = Table(f, dataframe = df[a5[k]][0], showtoolbar=False, height = tb_height, width = tb_width, showstatusbar=False)
                pt.setColumnColors(cols=[1,4], clr='#d4ebf2')
                pt.show()
                
        calc_button = ttk.Button(self, text="Calc", width = 19, command = CalcButton )
        calc_button.grid(column=1, row=1, sticky=tk.W, pady = 5)

class SwapMon(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)
        
        label_tab = tk.Label(self, text = "Swaps Monitor", font = LARGE_FONT, bg="light grey", fg = 'blue')
        label_tab.grid(row = 0, column = 0, columnspan = 5, sticky = 'W')
        
        curve_lstbox = tk.Listbox(self, width=18, height=60)
        curve_lstbox.grid(column=0, row=5, rowspan = 150, columnspan=1, sticky = 'W', padx=5)
        m = ["SOFR_DC", "FED_DC", "ESTER_DC", "EONIA_DC", "SONIA_DC", "CAD_OIS_DC", "AONIA_DC", "NZD_OIS_DC",
             "CHF_OIS_DC", "SEK_OIS_DC", "TONAR_DC", "RUONIA_DC", "EUR_3M", "EUR_6M", "CAD_3M", "CHF_6M", "SEK_3M",
             "NOK_3M", "NOK_6M", "JPY_6M", "AUD_3M", "AUD_6M", "NZD_3M", "KRW_3M", "PLN_3M", "PLN_6M", "CZK_3M",
             "CZK_6M", "HUF_3M", "HUF_6M", "ZAR_3M", "ILS_3M", "RUB_3M", "COP_OIS_DC", "MXN_TIIE"]
        for index, element in enumerate(m):
            curve_lstbox.insert(index, element)
        
        CurveLabel = ttk.Label(self, text = 'Curve: ')
        CurveLabel.grid(row = 2, column = 0 , sticky = 'E')
        CurveEntry = tk.Entry(self, width = 15, bg = 'light yellow', fg = 'dark blue')        
        CurveEntry.grid(row = 2, column = 1 , sticky = 'W')
        
        CurveDateLabel = ttk.Label(self, text = 'Curve Date: ')
        CurveDateLabel.grid(row = 3, column = 0, sticky = 'E')
        CurveDateEntry = ttk.Entry(self, width = 10)
        CurveDateEntry.insert(0, 0)
        CurveDateEntry.grid(row = 3, column = 1,  sticky = 'W')

        OffsetDaysLabel = ttk.Label(self, text = 'Offsets: ')
        OffsetDaysLabel.grid(row = 4, column = 0,  sticky = 'E')
        OffsetDaysEntry = ttk.Entry(self, width = 10)
        OffsetDaysEntry.insert(0, "-1")
        OffsetDaysEntry.grid(row = 4, column = 1,  sticky = 'W')
        
        Msg_Build = ttk.Label(self, text = '')
        Msg_Build.grid(row = 1, column = 3,  sticky = 'E' )
        
        def BuildButton():
            for widget in self.winfo_children()[12:]:
                 widget.grid_forget()
            
            CurveEntry.delete(0, tk.END)
            a1 = str(curve_lstbox.get(curve_lstbox.curselection()[0]))
            a2 = [item.strip() for item in a1.split(',')]
            CurveEntry.insert(0, a2[0])
            
            if len(CurveDateEntry.get()) < 4:
                a3 = int(CurveDateEntry.get())
            else:
                a3 = CurveDateEntry.get()
            
            a4 = str(OffsetDaysEntry.get())
            a5 = [item.strip() for item in a4.split(',')]
            a6 = [a3]
            for i in a5:
                if len(i) < 4:
                    a6 = a6 + [int(i)]
                else:
                    a6 = a6 + [i]
            
            today = ql.Date(datetime.datetime.now().day,datetime.datetime.now().month,datetime.datetime.now().year)
            now = datetime.datetime.now()
            current_time = now.strftime("%H:%M:%S")
            c = ccy(a2[0],today)
            
            global crv
            if c.ois_trigger == 0:
                crv = [ swap_build(a2[0], b = a6[i]) for i in np.arange(len(a6)) ]
            else:
                crv = [ ois_dc_build(a2[0], b = a6[i]) for i in np.arange(len(a6)) ]
            
            fix1 = ttk.Label(self, text = 'Fixing: '+str(crv[0].ref_fix))
            fix1.grid(row = 2, column = 2 , sticky = 'E')
            Dat1 = ttk.Label(self, text = str(crv[0].trade_date))
            Dat1.grid(row = 3, column = 2 , sticky = 'E')
            Dat2 = ttk.Label(self, text = str(crv[1].trade_date))
            Dat2.grid(row = 4, column = 2 , sticky = 'E')
            
            max_tenor = int((crv[0].nodes[-1][0]-crv[0].ref_date)/365)
            
            ### std outputs
            outright_rates = [1,2,3,4,5,6,7,8,9,10,12,15,20,25,30,40,50]
            fwd_rates = [(1,1), (2,1), (3,1), (4,1), (2,2), (3,2), (5,5), (10,5), (10,10), (15,15) ]
            curve_rates = [(2,3), (2,5), (2,10), (5,10), (5,30), (10,30)]
            fly_rates = [(2,3,5), (2,5,10), (3,5,7), (5,10,30)]

            fra_rates = FUT_CT_Q(crv[0].ref_date)[:13]
            outright_rates = [i for i in outright_rates if i <= max_tenor]
            fwd_rates = [(i,j) for i,j in fwd_rates if i+j <= max_tenor]
            curve_rates = [(i,j) for i,j in curve_rates if j <= max_tenor]
            fly_rates = [(i,j,k) for i,j,k in fly_rates if k <= max_tenor]
            
            tab = swap_table2(crv, outright_rates, fwd_rates, curve_rates, fly_rates)
            
            
            f1 = tk.Label(self, text = 'FRAs', fg = "dark blue", bg = "light grey" )
            f1.grid(row = 6, column = 2)
            f1a = tk.Label(self, text = 'Rate', fg = "dark blue", bg = "light grey")
            f1a.grid(row = 6, column = 3)
            f1b = tk.Label(self, text = 'Δ', fg = "dark blue", bg = "light grey")
            f1b.grid(row = 6, column = 4)
            f1c = tk.Label(self, text = '', width = 5, bg = "light grey")
            f1c.grid(row = 6, column = 5)
            
            stir_colour = ["white","red","green","blue"]
            chg_colour = ["red","green"]
            
            for i in np.arange(len(fra_rates)):
                f2 = tk.Label(self, text = str(fra_rates['TickerMonth'][i]), width = 5, bg = stir_colour[int(np.floor(i/4))] )
                f2.grid(row = 7+i, column = 2)
                
                f3 = ttk.Entry(self, width = 7)
                f3.insert(0, np.round(tab.fra[i*2],3))
                f3.grid(row = 7+i, column = 3)
                
                f4 = ttk.Entry(self, width = 5)
                f4.insert(0, np.round(tab.fra[(2*i)+1][0],1))
                f4.grid(row = 7+i, column = 4)
                f4.configure({"foreground": chg_colour[int(np.max([np.sign(  tab.fra[(2*i)+1][0]  ),0]))] })
           
            p1 = tk.Label(self, text = 'Par', fg = "dark blue", bg = "light grey")
            p1.grid(row = 8+len(fra_rates), column = 2)
            
            p1a = tk.Label(self, text = 'Rate', fg = "dark blue", bg = "light grey")
            p1a.grid(row = 8+len(fra_rates), column = 3)
            p1b = tk.Label(self, text = 'Δ', fg = "dark blue", bg = "light grey")
            p1b.grid(row = 8+len(fra_rates), column = 4)

            
            for i in np.arange(len(outright_rates)):
                p2 = ttk.Label(self, text = str(outright_rates[i]))
                p2.grid(row = 9+len(fra_rates)+i, column = 2)
                
                p3 = ttk.Entry(self, width = 7)
                p3.insert(0, np.round(tab.par[i*2],3))
                p3.grid(row = 9+len(fra_rates)+i, column = 3)
                
                p4 = ttk.Entry(self, width = 5)
                p4.insert(0, np.round(tab.par[(2*i)+1][0],1))
                p4.grid(row = 9+len(fra_rates)+i, column = 4)
                p4.configure({"foreground": chg_colour[int(np.max([np.sign(  tab.par[(2*i)+1][0]  ),0]))] })

            
            fwd1 = tk.Label(self, text = 'Fwds', fg = "dark blue", bg = "light grey")
            fwd1.grid(row = 6, column = 6)
            
            fwd1a = tk.Label(self, text = 'Rate', fg = "dark blue",  bg = "light grey")
            fwd1a.grid(row = 6, column = 8)
            fwd1b = tk.Label(self, text = 'Δ', fg = "dark blue",  bg = "light grey")
            fwd1b.grid(row = 6, column = 9)
            fwd1c = ttk.Label(self, text = '', width = 5)
            fwd1c.grid(row = 6, column = 11)

            for i in np.arange(len(fwd_rates)):
                fwd2 = tk.Entry(self, width = 5, name = 'fwd_leg1_'+str(i), bg = "light green")
                fwd2.insert(0, fwd_rates[i][0])
                fwd3 = tk.Entry(self, width = 5,  name = 'fwd_leg2_'+str(i), bg = "light green")
                fwd3.insert(0, fwd_rates[i][1])
                fwd2.grid(row = 7+i, column = 6)
                fwd3.grid(row = 7+i, column = 7)
                
                fwd4 = ttk.Entry(self, width = 7, name = 'fwd_'+str(i) )
                fwd4.insert(0, np.round(tab.fwds[i*2],3))
                fwd4.grid(row =  7+i, column = 8 )
                
                fwd5 = tk.Entry(self, width = 5, name = 'fwd_chg'+str(i) )
                fwd5.insert(0, np.round(tab.fwds[(2*i)+1][0],1) )
                fwd5.grid(row =  7+i, column = 9)
                fwd5.configure({"foreground": chg_colour[int(np.max([np.sign(  tab.fwds[(2*i)+1][0]  ),0]))] })
                
            c1 = tk.Label(self, text = 'Curves', fg = "dark blue", bg = "light grey")
            c1.grid(row = 8+len(fra_rates), column = 6)
            
            c1a = tk.Label(self, text = '0d', fg = "dark blue", bg = "light grey")
            c1a.grid(row = 8+len(fra_rates), column = 9)
            c1b = tk.Label(self, text = 'Δ', fg = "dark blue", bg = "light grey")
            c1b.grid(row = 8+len(fra_rates), column = 10)
            c1c = tk.Entry(self, width = 7, name = 'fwd1', bg = "light grey", fg = "dark blue")
            c1c.insert(0, '1m')
            c1c.grid(row = 8+len(fra_rates), column = 12)
            c1d = tk.Entry(self, width = 7, name = 'fwd2', bg = "light grey", fg = "dark blue")
            c1d.insert(0, '3m')
            c1d.grid(row = 8+len(fra_rates), column = 13)
            c1e = tk.Entry(self, width = 7, name = 'fwd3', bg = "light grey", fg = "dark blue")
            c1e.insert(0, '6m')
            c1e.grid(row = 8+len(fra_rates), column = 14)
            c1f = tk.Entry(self, width = 7, name = 'fwd4', bg = "light grey", fg = "dark blue")
            c1f.insert(0, '1y')
            c1f.grid(row = 8+len(fra_rates), column = 15)
            
            for i in np.arange(len(curve_rates)):
                c2 = tk.Entry(self, width = 5, name = 'curve_leg1_'+str(i), bg = "beige")
                c2.insert(0, curve_rates[i][0])
                c3 = tk.Entry(self, width = 5,  name = 'curve_leg2_'+str(i), bg = "beige")
                c3.insert(0, curve_rates[i][1])
                c2.grid(row = 9+len(fra_rates)+i, column = 6)
                c3.grid(row = 9+len(fra_rates)+i, column = 7)
                
                c7 = ttk.Entry(self, width = 7, name = 'curve_'+str(i) )
                c7.insert(0, np.round(tab.curve[i*3],3))
                c7.grid(row =  9+len(fra_rates)+i, column = 9)
                
                c8 = ttk.Entry(self, width = 5, name = 'curve_chg'+str(i))
                c8.insert(0, np.round(tab.curve[(3*i)+1][0],1))
                c8.grid(row =  9+len(fra_rates)+i, column = 10)
                c8.configure({"foreground": chg_colour[int(np.max([np.sign(  tab.curve[(3*i)+1][0]  ),0]))] })
                
                
                for j in np.arange(4):
                    c9 = ttk.Entry(self, width = 7, name = 'curve_'+str(j)+'_'+str(i), justify = "right" )
                    c9.insert(0, np.round(tab.curve[(3*i)+2][j],1))
                    c9.grid(row =  9+len(fra_rates)+i, column = 12+j)
                
                
                
            for i in np.arange(len(fly_rates)):
                c4 = tk.Entry(self, width = 5, name = 'fly_leg1_'+str(i), bg = "light blue")
                c4.insert(0, fly_rates[i][0])
                c5 = tk.Entry(self, width = 5, name = 'fly_leg2_'+str(i), bg = "light blue")
                c5.insert(0, fly_rates[i][1])
                c6 = tk.Entry(self, width = 5, name = 'fly_leg3_'+str(i), bg = "light blue")
                c6.insert(0, fly_rates[i][2])
                c4.grid(row = 9+len(fra_rates)+len(curve_rates)+i, column = 6)
                c5.grid(row = 9+len(fra_rates)+len(curve_rates)+i, column = 7)
                c6.grid(row = 9+len(fra_rates)+len(curve_rates)+i, column = 8)
                
                c10 = ttk.Entry(self, width = 7, name = 'fly_'+str(i))
                c10.insert(0, np.round(tab.fly[i*3],3))
                c10.grid(row =  9+len(fra_rates)+len(curve_rates)+i, column = 9)
                
                c11 = ttk.Entry(self, width = 5, name = 'fly_chg'+str(i))
                c11.insert(0, np.round(tab.fly[(3*i)+1][0],1))
                c11.grid(row =  9+len(fra_rates)+len(curve_rates)+i, column = 10)
                c11.configure({"foreground": chg_colour[int(np.max([np.sign(  tab.fly[(3*i)+1][0]  ),0]))] })
                
                for j in np.arange(4):
                    c9 = ttk.Entry(self, width = 7, name = 'fly_'+str(j)+'_'+str(i), justify = "right")
                    c9.insert(0, np.round(tab.fly[(3*i)+2][j],1))
                    c9.grid(row =  9+len(fra_rates)+len(curve_rates)+i, column = 12+j, sticky = 'E')
            
#            for widget in self.winfo_children()[9:]:
#                 print(widget)
            Msg_Build['text'] = "Done @"+current_time
            
        build_button = ttk.Button(self, text="Build", width = 14, command = BuildButton )
        build_button.grid(column=1, row=1, rowspan = 1, columnspan = 2, sticky=tk.W, pady=5)
        
        
        def ReCalcButton():
            ### std outputs
            fwd_rates = [(1,1), (2,1), (3,1), (4,1), (2,2), (3,2), (5,5), (10,5), (10,10), (15,15) ]
            curve_rates = [(2,3), (2,5), (2,10), (5,10), (5,30), (10,30)]
            fly_rates = [(2,3,5), (2,5,10), (3,5,7), (5,10,30)]
    
            max_tenor = int((crv[0].nodes[-1][0]-crv[0].ref_date)/365)
            fwd_rates = [(i,j) for i,j in fwd_rates if i+j <= max_tenor]
            curve_rates = [(i,j) for i,j in curve_rates if j <= max_tenor]
            fly_rates = [(i,j,k) for i,j,k in fly_rates if k <= max_tenor]

            fwd_rates =  [ ( int(self.children['fwd_leg1_'+str(i)].get()), int(self.children['fwd_leg2_'+str(i)].get())) for i in np.arange(len(fwd_rates)) ]
            curve_rates =  [ ( int(self.children['curve_leg1_'+str(i)].get()), int(self.children['curve_leg2_'+str(i)].get())) for i in np.arange(len(curve_rates)) ]
            fly_rates =  [ ( int(self.children['fly_leg1_'+str(i)].get()), int(self.children['fly_leg2_'+str(i)].get()), int(self.children['fly_leg3_'+str(i)].get())   ) for i in np.arange(len(fly_rates)) ]
            
            fwd_shift = [0] + [self.children['fwd'+str(i)].get() for i in np.arange(1,5) ]
            chg_colour = ["red","green"]
            
            tab = swap_table2(crv, [], fwd_rates, curve_rates, fly_rates,  shift = fwd_shift, price_nodes = 0)
            
            for i in np.arange(len(fwd_rates)):
                self.children['fwd_'+str(i)].delete(0, tk.END)
                self.children['fwd_chg'+str(i)].delete(0, tk.END)
                self.children['fwd_'+str(i)].insert(0, np.round(tab.fwds[i*2],3))
                self.children['fwd_chg'+str(i)].insert(0, np.round(tab.fwds[(2*i)+1][0],1) )
                self.children['fwd_chg'+str(i)].configure({"foreground": chg_colour[int(np.max([np.sign(  tab.fwds[(2*i)+1][0]  ),0]))] })
            
            for i in np.arange(len(curve_rates)):
                self.children['curve_'+str(i)].delete(0, tk.END)
                self.children['curve_chg'+str(i)].delete(0, tk.END)
                self.children['curve_'+str(i)].insert(0, np.round(tab.curve[i*3],3))
                self.children['curve_chg'+str(i)].insert(0, np.round(tab.curve[(3*i)+1][0],1))
                self.children['curve_chg'+str(i)].configure({"foreground": chg_colour[int(np.max([np.sign(  tab.curve[(3*i)+1][0]  ),0]))] })
                for j in np.arange(4):
                    self.children['curve_'+str(j)+'_'+str(i)].delete(0, tk.END)
                    self.children['curve_'+str(j)+'_'+str(i)].insert(0, np.round(tab.curve[(3*i)+2][j],1))
                    
                    
            for i in np.arange(len(fly_rates)):
                self.children['fly_'+str(i)].delete(0, tk.END)
                self.children['fly_chg'+str(i)].delete(0, tk.END)
                self.children['fly_'+str(i)].insert(0, np.round(tab.fly[i*3],3))
                self.children['fly_chg'+str(i)].insert(0, np.round(tab.fly[(3*i)+1][0],1))
                self.children['fly_chg'+str(i)].configure({"foreground": chg_colour[int(np.max([np.sign(  tab.fly[(3*i)+1][0]  ),0]))] })
                for j in np.arange(4):
                    self.children['fly_'+str(j)+'_'+str(i)].delete(0, tk.END)
                    self.children['fly_'+str(j)+'_'+str(i)].insert(0, np.round(tab.fly[(3*i)+2][j],1))

        calc_button = ttk.Button(self, text="Re-Calc", width = 14, command = ReCalcButton )
        calc_button.grid(column=2, row=1, rowspan = 1, columnspan=2, sticky=tk.W, pady=5)

class InfSwapMon(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)
        
        label_tab = tk.Label(self, text = "Inflation Swaps Monitor", font = LARGE_FONT, bg="light grey", fg = 'purple')
        label_tab.grid(row = 0, column = 0, columnspan = 5, sticky = 'W')
        
        curve_lstbox = tk.Listbox(self, width=18, height=50)
        curve_lstbox.grid(column=0, row=7, rowspan = 100, columnspan=1, sticky = 'W', padx=5)
        m = ["UKRPI", "HICPxT", "FRCPI", "USCPI"]
        for index, element in enumerate(m):
            curve_lstbox.insert(index, element)
        
        CurveLabel = ttk.Label(self, text = 'Curve: ')
        CurveLabel.grid(row = 2, column = 0 , sticky = 'E')
        CurveEntry = tk.Entry(self, width = 15, bg = 'light yellow', fg = 'dark blue')        
        CurveEntry.grid(row = 2, column = 1 , sticky = 'W')
        
        CurveDateLabel = ttk.Label(self, text = 'Curve Date: ')
        CurveDateLabel.grid(row = 3, column = 0, sticky = 'E')
        CurveDateEntry = ttk.Entry(self, width = 10)
        CurveDateEntry.insert(0, 0)
        CurveDateEntry.grid(row = 3, column = 1,  sticky = 'W')

        OffsetDaysLabel = ttk.Label(self, text = 'Offsets: ')
        OffsetDaysLabel.grid(row = 4, column = 0,  sticky = 'E')
        OffsetDaysEntry = ttk.Entry(self, width = 10)
        OffsetDaysEntry.insert(0, "-1")
        OffsetDaysEntry.grid(row = 4, column = 1,  sticky = 'W')
        
        LagLabel = ttk.Label(self, text = 'Lag: ')
        LagLabel.grid(row = 5, column = 0,  sticky = 'E')
        LagEntry = ttk.Entry(self, width = 10)
        LagEntry.insert(0, 3)
        LagEntry.grid(row = 5, column = 1,  sticky = 'W')
        
        SubCrvLabel = ttk.Label(self, text = 'Fixing Curve: ')
        SubCrvLabel.grid(row = 6, column = 0,  sticky = 'E')
        m2 = tk.StringVar(self)
        infsubcurveselect = ttk.Combobox(self, width = 10, textvariable = m2, name = 'infsubcurveselect')
        infsubcurveselect['values'] = ('Seasonals', 'Market', 'BARX')
        infsubcurveselect.grid(row = 6, column = 1, sticky = 'W')
               
#        Msg_Build = ttk.Label(self, text = '')
#        Msg_Build.grid(row = 1, column = 3,  sticky = 'E' )
        
        def BuildButton():
#            for widget in self.winfo_children()[12:]:
#                 widget.grid_forget()
            
            CurveEntry.delete(0, tk.END)
            a1 = str(curve_lstbox.get(curve_lstbox.curselection()[0]))
            a2 = [item.strip() for item in a1.split(',')]
            CurveEntry.insert(0, a2[0])
            
            if len(CurveDateEntry.get()) < 4:
                a3 = int(CurveDateEntry.get())
            else:
                a3 = CurveDateEntry.get()
            
            a4 = str(OffsetDaysEntry.get())
            a5 = [item.strip() for item in a4.split(',')]
            a6 = [a3]
            for i in a5:
                if len(i) < 4:
                    a6 = a6 + [int(i)]
                else:
                    a6 = a6 + [i]
            a7=0
            a8=0
            if str(infsubcurveselect.get()) == 'Market':
                a7 = 1
            if str(infsubcurveselect.get()) == 'BARX':
                a8 = 1
                        
            today = ql.Date(datetime.datetime.now().day,datetime.datetime.now().month,datetime.datetime.now().year)
            now = datetime.datetime.now()
            current_time = now.strftime("%H:%M:%S")
            c = ccy_infl(a2[0],today)
            
            global infcrv
            infcrv = [ infl_zc_swap_build(a2[0], b=a6[i]) for i in np.arange(len(a6)) ]
            
            a9 = LagEntry.get()
            a10 = [int(item.strip()) for item in a9.split(',')]
            if len(a10) == 1:
                lag = a10*len(infcrv)
            else:
                lag = a10
            
            Dat1 = ttk.Label(self, text = str(infcrv[0].ref_date))
            Dat1.grid(row = 3, column = 2 , sticky = 'E')
            Base1 = ttk.Label(self, text = ql_to_datetime(infcrv[0].base_month).strftime("%b-%y"))
            Base1.grid(row = 3, column = 3 , sticky = 'E')
            BaseFix1 = ttk.Label(self, text = str(infcrv[0].base_index) )
            BaseFix1.grid(row = 3, column = 4 , sticky = 'E')

            Dat2 = ttk.Label(self, text = str(infcrv[1].ref_date))
            Dat2.grid(row = 4, column = 2 , sticky = 'E')
            Base2 = ttk.Label(self, text = ql_to_datetime(infcrv[1].base_month).strftime("%b-%y"))
            Base2.grid(row = 4, column = 3 , sticky = 'E')
            BaseFix2 = ttk.Label(self, text = str(infcrv[1].base_index) )
            BaseFix2.grid(row = 4, column = 4 , sticky = 'E')
            
            max_tenor = int(( infcrv[0].curve[0]['months'][-1:].tolist()[0] - infcrv[0].ref_date  )/365) +1
            
            ### std outputs
            outright_rates = [1,2,3,4,5,6,7,8,9,10,12,15,20,25,30]
            fwd_rates = [(1,1), (2,1), (3,1), (4,1), (2,2), (3,2), (5,5), (10,5), (10,10), (15,15) ]
            curve_rates = [(2,3), (2,5), (2,10), (5,10), (5,30), (10,30)]
            fly_rates = [(2,3,5), (2,5,10), (3,5,7), (5,10,30)]

            x_fixing = [infcrv[0].last_pm + ql.Period(str(i)+"M") for i in np.arange(13)]
            outright_rates = [i for i in outright_rates if i <= max_tenor]
            fwd_rates = [(i,j) for i,j in fwd_rates if i+j <= max_tenor]
            curve_rates = [(i,j) for i,j in curve_rates if j <= max_tenor]
            fly_rates = [(i,j,k) for i,j,k in fly_rates if k <= max_tenor]
            
            tab = inf_swap_table(infcrv, lag, outright_rates, fwd_rates, curve_rates, fly_rates, use_forecast = a8, use_mkt_fixing = a7)
            
            f1 = tk.Label(self, text = 'Fixings', fg = "dark blue", bg = "light grey" )
            f1.grid(row = 7, column = 2)
            f1a = tk.Label(self, text = 'Rate', fg = "dark blue", bg = "light grey")
            f1a.grid(row = 7, column = 3)
            f1b = tk.Label(self, text = 'Δ', fg = "dark blue", bg = "light grey")
            f1b.grid(row = 7, column = 4)
            f1c = tk.Label(self, text = 'BARX', fg = "dark blue", bg = "light grey")
            f1c.grid(row = 7, column = 5)
            f1d = tk.Label(self, text = 'Diff', fg = "dark blue", bg = "light grey")
            f1d.grid(row = 7, column = 6)
            f1e = tk.Label(self, text = '', width = 5, bg = "light grey")
            f1e.grid(row = 7, column = 7)
            
            stir_colour = ["white","red","green","blue"]
            chg_colour = ["red","green"]
            
            for i in np.arange(len(x_fixing)):
                f2 = tk.Label(self, text = ql_to_datetime(x_fixing[i]).strftime("%b-%y"), width = 7, bg = stir_colour[int(np.floor(i/12))] )
                f2.grid(row = 8+i, column = 2)
                
                f3 = ttk.Entry(self, width = 7)
                f3.insert(0, np.round(tab.fixings[i*4],3))
                f3.grid(row = 8+i, column = 3)
                
                f4 = ttk.Entry(self, width = 5)
                f4.insert(0, np.round(tab.fixings[(4*i)+1][0],1))
                f4.grid(row = 8+i, column = 4)
                f4.configure({"foreground": chg_colour[int(np.max([np.sign(  tab.fixings[(4*i)+1][0]  ),0]))] })
                
                f5 = ttk.Entry(self, width = 7)
                f5.insert(0, np.round(tab.fixings[(4*i)+2],3))
                f5.grid(row = 8+i, column = 5)
                f5.configure({"foreground": "blue" })
                
                f6 = ttk.Entry(self, width = 5, justify = "right")
                f6.insert(0, np.round(tab.fixings[(4*i)+3],1))
                f6.grid(row = 8+i, column = 6)
                f6.configure({"foreground": chg_colour[int(np.max([np.sign(  tab.fixings[(4*i)+3] ),0]))] })
           
           
            p1 = tk.Label(self, text = 'ZC', fg = "dark blue", bg = "light grey")
            p1.grid(row = 9+len(x_fixing), column = 2)
            
            p1a = tk.Label(self, text = 'Rate', fg = "dark blue", bg = "light grey")
            p1a.grid(row = 9+len(x_fixing), column = 3)
            p1b = tk.Label(self, text = 'Δ', fg = "dark blue", bg = "light grey")
            p1b.grid(row = 9+len(x_fixing), column = 4)

            
            for i in np.arange(len(outright_rates)):
                p2 = ttk.Label(self, text = str(outright_rates[i]))
                p2.grid(row = 10+len(x_fixing)+i, column = 2)
                
                p3 = ttk.Entry(self, width = 7, name = 'infzc_'+str(i))
                p3.insert(0, np.round(tab.zc[i*2],3))
                p3.grid(row = 10+len(x_fixing)+i, column = 3)
                
                p4 = ttk.Entry(self, width = 5, name = 'infzc_chg'+str(i))
                p4.insert(0, np.round(tab.zc[(2*i)+1][0],1))
                p4.grid(row = 10+len(x_fixing)+i, column = 4)
                p4.configure({"foreground": chg_colour[int(np.max([np.sign(  tab.zc[(2*i)+1][0]  ),0]))] })

            
            fwd1 = tk.Label(self, text = 'Fwds', fg = "dark blue", bg = "light grey")
            fwd1.grid(row = 7, column = 8)
            
            fwd1a = tk.Label(self, text = 'Rate', fg = "dark blue",  bg = "light grey")
            fwd1a.grid(row = 7, column = 10)
            fwd1b = tk.Label(self, text = 'Δ', fg = "dark blue",  bg = "light grey")
            fwd1b.grid(row = 7, column = 11)
            fwd1c = ttk.Label(self, text = '', width = 5)
            fwd1c.grid(row = 7, column = 12)

            for i in np.arange(len(fwd_rates)):
                fwd2 = tk.Entry(self, width = 5, name = 'inffwd_leg1_'+str(i), bg = "light green")
                fwd2.insert(0, fwd_rates[i][0])
                fwd3 = tk.Entry(self, width = 5,  name = 'inffwd_leg2_'+str(i), bg = "light green")
                fwd3.insert(0, fwd_rates[i][1])
                fwd2.grid(row = 8+i, column = 8)
                fwd3.grid(row = 8+i, column = 9)
                
                fwd4 = ttk.Entry(self, width = 7, name = 'inffwd_'+str(i) )
                fwd4.insert(0, np.round(tab.fwds[i*2],3))
                fwd4.grid(row =  8+i, column = 10 )
                
                fwd5 = tk.Entry(self, width = 5, name = 'inffwd_chg'+str(i) )
                fwd5.insert(0, np.round(tab.fwds[(2*i)+1][0],1) )
                fwd5.grid(row =  8+i, column = 11)
                fwd5.configure({"foreground": chg_colour[int(np.max([np.sign(  tab.fwds[(2*i)+1][0]  ),0]))] })
                
            c1 = tk.Label(self, text = 'Curves', fg = "dark blue", bg = "light grey")
            c1.grid(row = 9+len(x_fixing), column = 8)
            
            c1a = tk.Label(self, text = '0d', fg = "dark blue", bg = "light grey")
            c1a.grid(row = 9+len(x_fixing), column = 11)
            c1b = tk.Label(self, text = 'Δ', fg = "dark blue", bg = "light grey")
            c1b.grid(row = 9+len(x_fixing), column = 12)
            c1c = tk.Entry(self, width = 7, name = 'inffwd1', bg = "light grey", fg = "dark blue", justify = "right")
            c1c.insert(0, '1m')
            c1c.grid(row = 9+len(x_fixing), column = 13)
            c1d = tk.Entry(self, width = 7, name = 'inffwd2', bg = "light grey", fg = "dark blue", justify = "right")
            c1d.insert(0, '2m')
            c1d.grid(row = 9+len(x_fixing), column = 14)
            c1e = tk.Entry(self, width = 7, name = 'inffwd3', bg = "light grey", fg = "dark blue", justify = "right")
            c1e.insert(0, '3m')
            c1e.grid(row = 9+len(x_fixing), column = 15)
            
            for j in np.arange(3):
                b1 = ttk.Label(self, text = ql_to_datetime(  infcrv[0].base_month+ql.Period( self.children['inffwd'+str(j+1)].get() )).strftime("%b-%y"), name = "inffwd_base"+str(j+1) )
                b1.grid(row = 8+len(x_fixing), column = 13+j , sticky = 'E')

            
            for i in np.arange(len(curve_rates)):
                c2 = tk.Entry(self, width = 5, name = 'infcurve_leg1_'+str(i), bg = "beige")
                c2.insert(0, curve_rates[i][0])
                c3 = tk.Entry(self, width = 5,  name = 'infcurve_leg2_'+str(i), bg = "beige")
                c3.insert(0, curve_rates[i][1])
                c2.grid(row = 10+len(x_fixing)+i, column = 8)
                c3.grid(row = 10+len(x_fixing)+i, column = 9)
                
                c7 = ttk.Entry(self, width = 7, name = 'infcurve_'+str(i) )
                c7.insert(0, np.round(tab.curve[i*3],3))
                c7.grid(row =  10+len(x_fixing)+i, column = 11)
                
                c8 = ttk.Entry(self, width = 5, name = 'infcurve_chg'+str(i))
                c8.insert(0, np.round(tab.curve[(3*i)+1][0],1))
                c8.grid(row =  10+len(x_fixing)+i, column = 12)
                c8.configure({"foreground": chg_colour[int(np.max([np.sign(  tab.curve[(3*i)+1][0]  ),0]))] })
                
                for j in np.arange(3):                    
                    c9 = ttk.Entry(self, width = 7, name = 'infcurve_'+str(j)+'_'+str(i), justify = "right" )
                    c9.insert(0, np.round(tab.curve[(3*i)+2][j],1))
                    c9.grid(row =  10+len(x_fixing)+i, column = 13+j)
                
               
                
            for i in np.arange(len(fly_rates)):
                c4 = tk.Entry(self, width = 5, name = 'inffly_leg1_'+str(i), bg = "light blue")
                c4.insert(0, fly_rates[i][0])
                c5 = tk.Entry(self, width = 5, name = 'inffly_leg2_'+str(i), bg = "light blue")
                c5.insert(0, fly_rates[i][1])
                c6 = tk.Entry(self, width = 5, name = 'inffly_leg3_'+str(i), bg = "light blue")
                c6.insert(0, fly_rates[i][2])
                c4.grid(row = 10+len(x_fixing)+len(curve_rates)+i, column = 8)
                c5.grid(row = 10+len(x_fixing)+len(curve_rates)+i, column = 9)
                c6.grid(row = 10+len(x_fixing)+len(curve_rates)+i, column = 10)
                
                c10 = ttk.Entry(self, width = 7, name = 'inffly_'+str(i))
                c10.insert(0, np.round(tab.fly[i*3],3))
                c10.grid(row =  10+len(x_fixing)+len(curve_rates)+i, column = 11)
                
                c11 = ttk.Entry(self, width = 5, name = 'inffly_chg'+str(i))
                c11.insert(0, np.round(tab.fly[(3*i)+1][0],1))
                c11.grid(row =  10+len(x_fixing)+len(curve_rates)+i, column = 12)
                c11.configure({"foreground": chg_colour[int(np.max([np.sign(  tab.fly[(3*i)+1][0]  ),0]))] })
                
                for j in np.arange(3):
                    c9 = ttk.Entry(self, width = 7, name = 'inffly_'+str(j)+'_'+str(i), justify = "right")
                    c9.insert(0, np.round(tab.fly[(3*i)+2][j],1))
                    c9.grid(row =  10+len(x_fixing)+len(curve_rates)+i, column = 13+j, sticky = 'E')
            
#            for widget in self.winfo_children()[9:]:
#                 print(widget)
#            Msg_Build['text'] = "Done @"+current_time
            
        build_button = ttk.Button(self, text="Build", width = 14, command = BuildButton )
        build_button.grid(column=1, row=1, rowspan = 1, columnspan = 2, sticky=tk.W, pady=5)
        
        
        def ReCalcButton():
            ### std outputs
            outright_rates = [1,2,3,4,5,6,7,8,9,10,12,15,20,25,30]
            fwd_rates = [(1,1), (2,1), (3,1), (4,1), (2,2), (3,2), (5,5), (10,5), (10,10), (15,15) ]
            curve_rates = [(2,3), (2,5), (2,10), (5,10), (5,30), (10,30)]
            fly_rates = [(2,3,5), (2,5,10), (3,5,7), (5,10,30)]
    
            max_tenor = int(( infcrv[0].curve[0]['months'][-1:].tolist()[0] - infcrv[0].ref_date  )/365) +1
            outright_rates = [i for i in outright_rates if i <= max_tenor]
            fwd_rates = [(i,j) for i,j in fwd_rates if i+j <= max_tenor]
            curve_rates = [(i,j) for i,j in curve_rates if j <= max_tenor]
            fly_rates = [(i,j,k) for i,j,k in fly_rates if k <= max_tenor]

            fwd_rates =  [ ( int(self.children['inffwd_leg1_'+str(i)].get()), int(self.children['inffwd_leg2_'+str(i)].get())) for i in np.arange(len(fwd_rates)) ]
            curve_rates =  [ ( int(self.children['infcurve_leg1_'+str(i)].get()), int(self.children['infcurve_leg2_'+str(i)].get())) for i in np.arange(len(curve_rates)) ]
            fly_rates =  [ ( int(self.children['inffly_leg1_'+str(i)].get()), int(self.children['inffly_leg2_'+str(i)].get()), int(self.children['inffly_leg3_'+str(i)].get())   ) for i in np.arange(len(fly_rates)) ]
            
            fwd_shift = [0] + [self.children['inffwd'+str(i)].get() for i in np.arange(1,4)]
            chg_colour = ["red","green"]
            
            a7=0
            a8=0
            if str(infsubcurveselect.get()) == 'Market':
                a7 = 1
            if str(infsubcurveselect.get()) == 'BARX':
                a8 = 1
                
            a9 = LagEntry.get()
            a10 = [int(item.strip()) for item in a9.split(',')]
            if len(a10) == 1:
                lag = a10*len(infcrv)
            else:
                lag = a10           
            
            tab = inf_swap_table(infcrv, lag, outright_rates, fwd_rates, curve_rates, fly_rates, use_forecast = a8, use_mkt_fixing = a7, shift = fwd_shift, price_nodes = 1)
            print(tab.zc)
            
            b2 = ttk.Label(self, text = ql_to_datetime(Infl_ZC_Pricer(infcrv[0],0,5,lag = a10[0],use_forecast=a8,use_mkt_fixing=a7).base).strftime("%b-%y"))
            b2.grid(row = 9+13, column = 1 , sticky = 'E')
            
            for i in np.arange(len(outright_rates)):
                print(i)
                self.children['infzc_'+str(i)].delete(0, tk.END)
                self.children['infzc_chg'+str(i)].delete(0, tk.END)
                self.children['infzc_'+str(i)].insert(0, np.round(tab.zc[i*2],3))
                self.children['infzc_chg'+str(i)].insert(0, np.round(tab.zc[(2*i)+1][0],1) )
                self.children['infzc_chg'+str(i)].configure({"foreground": chg_colour[int(np.max([np.sign(  tab.zc[(2*i)+1][0] ),0]))] })
            
            for i in np.arange(len(fwd_rates)):
                self.children['inffwd_'+str(i)].delete(0, tk.END)
                self.children['inffwd_chg'+str(i)].delete(0, tk.END)
                self.children['inffwd_'+str(i)].insert(0, np.round(tab.fwds[i*2],3))
                self.children['inffwd_chg'+str(i)].insert(0, np.round(tab.fwds[(2*i)+1][0],1) )
                self.children['inffwd_chg'+str(i)].configure({"foreground": chg_colour[int(np.max([np.sign(  tab.fwds[(2*i)+1][0]  ),0]))] })
            
            for j in np.arange(3):
                    self.children['inffwd_base'+str(j+1)]['text'] = ql_to_datetime(infcrv[0].base_month+ql.Period(self.children['inffwd'+str(j+1)].get() )).strftime("%b-%y")
            
            for i in np.arange(len(curve_rates)):
                self.children['infcurve_'+str(i)].delete(0, tk.END)
                self.children['infcurve_chg'+str(i)].delete(0, tk.END)
                self.children['infcurve_'+str(i)].insert(0, np.round(tab.curve[i*3],3))
                self.children['infcurve_chg'+str(i)].insert(0, np.round(tab.curve[(3*i)+1][0],1))
                self.children['infcurve_chg'+str(i)].configure({"foreground": chg_colour[int(np.max([np.sign(  tab.curve[(3*i)+1][0]  ),0]))] })
                for j in np.arange(3):
                    self.children['infcurve_'+str(j)+'_'+str(i)].delete(0, tk.END)
                    self.children['infcurve_'+str(j)+'_'+str(i)].insert(0, np.round(tab.curve[(3*i)+2][j],1))
                    
                    
            for i in np.arange(len(fly_rates)):
                self.children['inffly_'+str(i)].delete(0, tk.END)
                self.children['inffly_chg'+str(i)].delete(0, tk.END)
                self.children['inffly_'+str(i)].insert(0, np.round(tab.fly[i*3],3))
                self.children['inffly_chg'+str(i)].insert(0, np.round(tab.fly[(3*i)+1][0],1))
                self.children['inffly_chg'+str(i)].configure({"foreground": chg_colour[int(np.max([np.sign(  tab.fly[(3*i)+1][0]  ),0]))] })
                for j in np.arange(3):
                    self.children['inffly_'+str(j)+'_'+str(i)].delete(0, tk.END)
                    self.children['inffly_'+str(j)+'_'+str(i)].insert(0, np.round(tab.fly[(3*i)+2][j],1))

        calc_button = ttk.Button(self, text="Re-Calc", width = 14, command = ReCalcButton )
        calc_button.grid(column=2, row=1, rowspan = 1, columnspan=2, sticky=tk.W, pady=5)


class Plotter(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)
        
        label_tab = tk.Label(self, text = "Plotool", font = LARGE_FONT, bg="light grey", fg = 'blue')
        label_tab.grid(row = 0, column = 0, columnspan = 5, sticky = 'W')
        
        curve_lstbox = tk.Listbox(self, selectmode='multiple', width=14, height=60)
        curve_lstbox.grid(column=0, row=2, rowspan = 150, columnspan=1, sticky = 'W', padx=5)
        m = ["SOFR_DC", "FED_DC", "ESTER_DC", "EONIA_DC", "SONIA_DC", "CAD_OIS_DC", "AONIA_DC", "NZD_OIS_DC",
             "CHF_OIS_DC", "SEK_OIS_DC", "TONAR_DC", "RUONIA_DC", "EUR_3M", "EUR_6M", "CAD_3M", "CHF_6M", "SEK_3M",
             "NOK_3M", "NOK_6M", "JPY_6M", "AUD_3M", "AUD_6M", "NZD_3M", "KRW_3M", "PLN_3M", "PLN_6M", "CZK_3M",
             "CZK_6M", "HUF_3M", "HUF_6M", "ZAR_3M", "ILS_3M", "RUB_3M", "COP_OIS_DC", "MXN_TIIE"]
        for index, element in enumerate(m):
            curve_lstbox.insert(index, element)
        
        curve_lstbox2 = tk.Listbox(self, selectmode='multiple', width=14, height=60)
        curve_lstbox2.grid(column=1, row=2, rowspan = 150, columnspan=1, sticky = 'W', padx=5)
        for index, element in enumerate(m):
            curve_lstbox2.insert(index, element)

               
        CurveLabel = ttk.Label(self, text = 'Curve: ')
        CurveLabel.grid(row = 2, column = 2 , sticky = 'E')
        CurveEntry = tk.Entry(self, width = 25, bg = 'light yellow', fg = 'dark blue')        
        CurveEntry.grid(row = 2, column = 3 , sticky = 'W')
        
        CurveLabel2 = ttk.Label(self, text = 'Curve: ')
        CurveLabel2.grid(row = 4, column = 2 , sticky = 'E')
        CurveEntry2 = tk.Entry(self, width = 25, bg = 'light yellow', fg = 'dark blue')        
        CurveEntry2.grid(row = 4, column = 3 , sticky = 'W')

        StartDateLabel = ttk.Label(self, text = 'Start: ')
        StartDateLabel.grid(row = 2, column = 4, sticky = 'E')
        StartDateEntry = ttk.Entry(self, width = 15)
        StartDateEntry.insert(0, '-1y')
        StartDateEntry.grid(row = 2, column = 5,  sticky = 'W')
        
        StartDateLabel2 = ttk.Label(self, text = 'Start: ')
        StartDateLabel2.grid(row = 4, column = 4, sticky = 'E')
        StartDateEntry2 = ttk.Entry(self, width = 15)
        StartDateEntry2.insert(0, '-1y')
        StartDateEntry2.grid(row = 4, column = 5,  sticky = 'W')

        EndDateLabel = ttk.Label(self, text = 'End: ')
        EndDateLabel.grid(row = 2, column = 6,  sticky = 'E')
        EndDateEntry = ttk.Entry(self, width = 15)
        EndDateEntry.insert(0, "")
        EndDateEntry.grid(row = 2, column = 7,  sticky = 'W')
        
        EndDateLabel2 = ttk.Label(self, text = 'End: ')
        EndDateLabel2.grid(row = 4, column = 6,  sticky = 'E')
        EndDateEntry2 = ttk.Entry(self, width = 15)
        EndDateEntry2.insert(0, "")
        EndDateEntry2.grid(row = 4, column = 7,  sticky = 'W')
        
        TenorsLabel = ttk.Label(self, text = 'Tenors: ')
        TenorsLabel.grid(row = 2, column = 8,  sticky = 'E')
        TenorsEntry = ttk.Entry(self, width = 25)
        TenorsEntry.insert(0, "")
        TenorsEntry.grid(row = 2, column = 9,  sticky = 'W')
        
        TenorsLabel2 = ttk.Label(self, text = 'Tenors: ')
        TenorsLabel2.grid(row = 4, column = 8,  sticky = 'E')
        TenorsEntry2 = ttk.Entry(self, width = 25)
        TenorsEntry2.insert(0, "")
        TenorsEntry2.grid(row = 4, column = 9,  sticky = 'W')
       
        ToggleLabel = ttk.Label(self, text = 'Toggle: ')
        ToggleLabel.grid(row = 2, column = 10,  sticky = 'E')        
        toggle_lstbox = ttk.Combobox(self, width = 8)
        toggle_lstbox['values'] = ('Std','X-Curve')
        toggle_lstbox.set('Std')
        toggle_lstbox.grid(column=11, row=2, sticky = 'W', padx=5)
        
        ToggleLabel2 = ttk.Label(self, text = 'Toggle: ')
        ToggleLabel2.grid(row = 4, column = 10,  sticky = 'E')        
        toggle_lstbox2 = ttk.Combobox(self, width = 8)
        toggle_lstbox2['values'] = ('Std','X-Curve')
        toggle_lstbox2.set('Std')
        toggle_lstbox2.grid(column=11, row=4, sticky = 'W', padx=5)
        
        InstTypeLabel = ttk.Label(self, text = 'Inst Type: ')
        InstTypeLabel.grid(row = 2, column = 12,  sticky = 'E')        
        InstType_lstbox = ttk.Combobox(self, width = 8)
        InstType_lstbox['values'] = ('Par','Fwd','Cash')
        InstType_lstbox.set('Par')
        InstType_lstbox.grid(column=13, row=2, sticky = 'W', padx=5)
        
        InstTypeLabel2 = ttk.Label(self, text = 'Inst Type: ')
        InstTypeLabel2.grid(row = 4, column = 12,  sticky = 'E')        
        InstType_lstbox2 = ttk.Combobox(self, width = 8)
        InstType_lstbox2['values'] = ('Par','Fwd','Cash')
        InstType_lstbox2.set('Fwd')
        InstType_lstbox2.grid(column=13, row=4, sticky = 'W', padx=5)

        StratTypeLabel = ttk.Label(self, text = 'Strat Type: ')
        StratTypeLabel.grid(row = 2, column = 14,  sticky = 'E')        
        StratType_lstbox = ttk.Combobox(self,  width = 8)
        StratType_lstbox['values'] = ('Outright','Spread','Fly')
        StratType_lstbox.set('Outright')
        StratType_lstbox.grid(column=15, row=2, sticky = 'W', padx=5)
        
        StratTypeLabel2 = ttk.Label(self, text = 'Strat Type: ')
        StratTypeLabel2.grid(row = 4, column = 14,  sticky = 'E')        
        StratType_lstbox2 = ttk.Combobox(self,  width = 8)
        StratType_lstbox2['values'] = ('Outright','Spread','Fly')
        StratType_lstbox2.set('Outright')
        StratType_lstbox2.grid(column=15, row=4, sticky = 'W', padx=5)
        
        ChgVar = tk.IntVar()
        chg_check = ttk.Checkbutton(self,text='Change', onvalue=1, offvalue=0, variable=ChgVar)
        chg_check.grid(column=16, row=2, sticky = 'W', padx=5)

        InvertVar = tk.IntVar()
        invert_check = ttk.Checkbutton(self,text='Invert', onvalue=1, offvalue=0, variable=InvertVar)
        invert_check.grid(column=17, row=2, sticky = 'W', padx=5)
        
        ChgVar2 = tk.IntVar()
        chg_check2 = ttk.Checkbutton(self,text='Change', onvalue=1, offvalue=0, variable=ChgVar2)
        chg_check2.grid(column=16, row=4, sticky = 'W', padx=5)

        InvertVar2 = tk.IntVar()
        invert_check2 = ttk.Checkbutton(self,text='Invert', onvalue=1, offvalue=0, variable=InvertVar2)
        invert_check2.grid(column=17, row=4, sticky = 'W', padx=5)


        def PlotButton1():
                 
            CurveEntry.delete(0, tk.END)
            a2 = [curve_lstbox.get(i) for i in curve_lstbox.curselection()]
            CurveEntry.insert(0, a2)
            print(a2)   ### curves
            
            a3 = str(StartDateEntry.get())  ### start date
            a4 = str(EndDateEntry.get())    ### end date
            
            print(a3)  
            print(a4)  
            
            a5 = str(TenorsEntry.get())
            a6 = [item.strip() for item in a5.split(',')]   #### tenors
            a6 = [a6[i].upper() for i in np.arange(len(a6))]
            print(a6)
            
            a7 = toggle_lstbox.get()
            a8 = InstType_lstbox.get()
            a9 = StratType_lstbox.get()
            a10 = ChgVar.get()
            a11 = InvertVar.get()
            
            print(a7, a8, a9, a10, a11)
            
            f =  plotool(a3,a4, a2, a6, a7, a8, a9, a10, a11)
            
            canvas = FigureCanvasTkAgg(f, self)
            mplcursors.cursor()
            canvas.draw()
            canvas.get_tk_widget().grid(row=25, column=3, columnspan = 7, sticky = 'nsew', padx=2, pady=2)

            # navigation toolbar
            toolbarFrame = tk.Frame(self)
            toolbarFrame.grid(row=2,column=18)
            toolbar = NavigationToolbar2Tk(canvas, toolbarFrame)


        plot_button1 = ttk.Button(self, text="Plot1", width = 14, command = PlotButton1)
        plot_button1.grid(column=0, row=1, rowspan = 1, columnspan = 2, sticky=tk.W)
        
        def PlotButton2():
            CurveEntry2.delete(0, tk.END)
            a2 = [curve_lstbox2.get(i) for i in curve_lstbox2.curselection()]
            CurveEntry2.insert(0, a2)
            print(a2)   ### curves
            
            a3 = str(StartDateEntry2.get())  ### start date
            a4 = str(EndDateEntry2.get())    ### end date
            
            print(a3)  
            print(a4)  
            
            a5 = str(TenorsEntry2.get())
            a6 = [item.strip() for item in a5.split(',')]   #### tenors
            a6 = [a6[i].upper() for i in np.arange(len(a6))]
            print(a6)
            
            a7 = toggle_lstbox2.get()
            a8 = InstType_lstbox2.get()
            a9 = StratType_lstbox2.get()
            a10 = ChgVar2.get()
            a11 = InvertVar2.get()
            
            print(a7, a8, a9, a10, a11)
            
            f =  plotool(a3,a4, a2, a6, a7, a8, a9, a10, a11)
            
            canvas = FigureCanvasTkAgg(f, self)
            mplcursors.cursor()
            canvas.draw()
            canvas.get_tk_widget().grid(row=25, column=10, columnspan = 7, sticky = 'nsew', padx=2, pady=2)

            # navigation toolbar
            toolbarFrame = tk.Frame(self)
            toolbarFrame.grid(row=4,column=18)
            toolbar = NavigationToolbar2Tk(canvas, toolbarFrame)


        plot_button2 = ttk.Button(self, text="Plot2", width = 14, command = PlotButton2)
        plot_button2.grid(column=1, row=1, rowspan = 1, columnspan = 2, sticky=tk.W)



        
        def BuildButton():
            for widget in self.winfo_children()[12:]:
                 widget.grid_forget()
            
            CurveEntry.delete(0, tk.END)
            a1 = str(curve_lstbox.get(curve_lstbox.curselection()[0]))
            a2 = [item.strip() for item in a1.split(',')]
            CurveEntry.insert(0, a2[0])
            
            if len(CurveDateEntry.get()) < 4:
                a3 = int(CurveDateEntry.get())
            else:
                a3 = CurveDateEntry.get()
            
            a4 = str(OffsetDaysEntry.get())
            a5 = [item.strip() for item in a4.split(',')]
            a6 = [a3]
            for i in a5:
                if len(i) < 4:
                    a6 = a6 + [int(i)]
                else:
                    a6 = a6 + [i]
            
            today = ql.Date(datetime.datetime.now().day,datetime.datetime.now().month,datetime.datetime.now().year)
            now = datetime.datetime.now()
            current_time = now.strftime("%H:%M:%S")
            c = ccy(a2[0],today)
            
            global crv
            if c.ois_trigger == 0:
                crv = [ swap_build(a2[0], b = a6[i]) for i in np.arange(len(a6)) ]
            else:
                crv = [ ois_dc_build(a2[0], b = a6[i]) for i in np.arange(len(a6)) ]
            
            fix1 = ttk.Label(self, text = 'Fixing: '+str(crv[0].ref_fix))
            fix1.grid(row = 2, column = 2 , sticky = 'E')
            Dat1 = ttk.Label(self, text = str(crv[0].trade_date))
            Dat1.grid(row = 3, column = 2 , sticky = 'E')
            Dat2 = ttk.Label(self, text = str(crv[1].trade_date))
            Dat2.grid(row = 4, column = 2 , sticky = 'E')
            
            max_tenor = int((crv[0].nodes[-1][0]-crv[0].ref_date)/365)
            
            ### std outputs
            outright_rates = [1,2,3,4,5,6,7,8,9,10,12,15,20,25,30,40,50]
            fwd_rates = [(1,1), (2,1), (3,1), (4,1), (2,2), (3,2), (5,5), (10,5), (10,10), (15,15) ]
            curve_rates = [(2,3), (2,5), (2,10), (5,10), (5,30), (10,30)]
            fly_rates = [(2,3,5), (2,5,10), (3,5,7), (5,10,30)]

            fra_rates = FUT_CT_Q(crv[0].ref_date)[:13]
            outright_rates = [i for i in outright_rates if i <= max_tenor]
            fwd_rates = [(i,j) for i,j in fwd_rates if i+j <= max_tenor]
            curve_rates = [(i,j) for i,j in curve_rates if j <= max_tenor]
            fly_rates = [(i,j,k) for i,j,k in fly_rates if k <= max_tenor]
            
            tab = swap_table2(crv, outright_rates, fwd_rates, curve_rates, fly_rates)
            
            
            f1 = tk.Label(self, text = 'FRAs', fg = "dark blue", bg = "light grey" )
            f1.grid(row = 6, column = 2)
            f1a = tk.Label(self, text = 'Rate', fg = "dark blue", bg = "light grey")
            f1a.grid(row = 6, column = 3)
            f1b = tk.Label(self, text = 'Δ', fg = "dark blue", bg = "light grey")
            f1b.grid(row = 6, column = 4)
            f1c = tk.Label(self, text = '', width = 5, bg = "light grey")
            f1c.grid(row = 6, column = 5)
            
            stir_colour = ["white","red","green","blue"]
            chg_colour = ["red","green"]
            
            for i in np.arange(len(fra_rates)):
                f2 = tk.Label(self, text = str(fra_rates['TickerMonth'][i]), width = 5, bg = stir_colour[int(np.floor(i/4))] )
                f2.grid(row = 7+i, column = 2)
                
                f3 = ttk.Entry(self, width = 7)
                f3.insert(0, np.round(tab.fra[i*2],3))
                f3.grid(row = 7+i, column = 3)
                
                f4 = ttk.Entry(self, width = 5)
                f4.insert(0, np.round(tab.fra[(2*i)+1][0],1))
                f4.grid(row = 7+i, column = 4)
                f4.configure({"foreground": chg_colour[int(np.max([np.sign(  tab.fra[(2*i)+1][0]  ),0]))] })
           
            p1 = tk.Label(self, text = 'Par', fg = "dark blue", bg = "light grey")
            p1.grid(row = 8+len(fra_rates), column = 2)
            
            p1a = tk.Label(self, text = 'Rate', fg = "dark blue", bg = "light grey")
            p1a.grid(row = 8+len(fra_rates), column = 3)
            p1b = tk.Label(self, text = 'Δ', fg = "dark blue", bg = "light grey")
            p1b.grid(row = 8+len(fra_rates), column = 4)

            
            for i in np.arange(len(outright_rates)):
                p2 = ttk.Label(self, text = str(outright_rates[i]))
                p2.grid(row = 9+len(fra_rates)+i, column = 2)
                
                p3 = ttk.Entry(self, width = 7)
                p3.insert(0, np.round(tab.par[i*2],3))
                p3.grid(row = 9+len(fra_rates)+i, column = 3)
                
                p4 = ttk.Entry(self, width = 5)
                p4.insert(0, np.round(tab.par[(2*i)+1][0],1))
                p4.grid(row = 9+len(fra_rates)+i, column = 4)
                p4.configure({"foreground": chg_colour[int(np.max([np.sign(  tab.par[(2*i)+1][0]  ),0]))] })

            
            fwd1 = tk.Label(self, text = 'Fwds', fg = "dark blue", bg = "light grey")
            fwd1.grid(row = 6, column = 6)
            
            fwd1a = tk.Label(self, text = 'Rate', fg = "dark blue",  bg = "light grey")
            fwd1a.grid(row = 6, column = 8)
            fwd1b = tk.Label(self, text = 'Δ', fg = "dark blue",  bg = "light grey")
            fwd1b.grid(row = 6, column = 9)
            fwd1c = ttk.Label(self, text = '', width = 5)
            fwd1c.grid(row = 6, column = 11)

            for i in np.arange(len(fwd_rates)):
                fwd2 = tk.Entry(self, width = 5, name = 'fwd_leg1_'+str(i), bg = "light green")
                fwd2.insert(0, fwd_rates[i][0])
                fwd3 = tk.Entry(self, width = 5,  name = 'fwd_leg2_'+str(i), bg = "light green")
                fwd3.insert(0, fwd_rates[i][1])
                fwd2.grid(row = 7+i, column = 6)
                fwd3.grid(row = 7+i, column = 7)
                
                fwd4 = ttk.Entry(self, width = 7, name = 'fwd_'+str(i) )
                fwd4.insert(0, np.round(tab.fwds[i*2],3))
                fwd4.grid(row =  7+i, column = 8 )
                
                fwd5 = tk.Entry(self, width = 5, name = 'fwd_chg'+str(i) )
                fwd5.insert(0, np.round(tab.fwds[(2*i)+1][0],1) )
                fwd5.grid(row =  7+i, column = 9)
                fwd5.configure({"foreground": chg_colour[int(np.max([np.sign(  tab.fwds[(2*i)+1][0]  ),0]))] })
                
            c1 = tk.Label(self, text = 'Curves', fg = "dark blue", bg = "light grey")
            c1.grid(row = 8+len(fra_rates), column = 6)
            
            c1a = tk.Label(self, text = '0d', fg = "dark blue", bg = "light grey")
            c1a.grid(row = 8+len(fra_rates), column = 9)
            c1b = tk.Label(self, text = 'Δ', fg = "dark blue", bg = "light grey")
            c1b.grid(row = 8+len(fra_rates), column = 10)
            c1c = tk.Entry(self, width = 7, name = 'fwd1', bg = "light grey", fg = "dark blue")
            c1c.insert(0, '1m')
            c1c.grid(row = 8+len(fra_rates), column = 12)
            c1d = tk.Entry(self, width = 7, name = 'fwd2', bg = "light grey", fg = "dark blue")
            c1d.insert(0, '3m')
            c1d.grid(row = 8+len(fra_rates), column = 13)
            c1e = tk.Entry(self, width = 7, name = 'fwd3', bg = "light grey", fg = "dark blue")
            c1e.insert(0, '6m')
            c1e.grid(row = 8+len(fra_rates), column = 14)
            c1f = tk.Entry(self, width = 7, name = 'fwd4', bg = "light grey", fg = "dark blue")
            c1f.insert(0, '1y')
            c1f.grid(row = 8+len(fra_rates), column = 15)
            
            for i in np.arange(len(curve_rates)):
                c2 = tk.Entry(self, width = 5, name = 'curve_leg1_'+str(i), bg = "beige")
                c2.insert(0, curve_rates[i][0])
                c3 = tk.Entry(self, width = 5,  name = 'curve_leg2_'+str(i), bg = "beige")
                c3.insert(0, curve_rates[i][1])
                c2.grid(row = 9+len(fra_rates)+i, column = 6)
                c3.grid(row = 9+len(fra_rates)+i, column = 7)
                
                c7 = ttk.Entry(self, width = 7, name = 'curve_'+str(i) )
                c7.insert(0, np.round(tab.curve[i*3],3))
                c7.grid(row =  9+len(fra_rates)+i, column = 9)
                
                c8 = ttk.Entry(self, width = 5, name = 'curve_chg'+str(i))
                c8.insert(0, np.round(tab.curve[(3*i)+1][0],1))
                c8.grid(row =  9+len(fra_rates)+i, column = 10)
                c8.configure({"foreground": chg_colour[int(np.max([np.sign(  tab.curve[(3*i)+1][0]  ),0]))] })
                
                
                for j in np.arange(4):
                    c9 = ttk.Entry(self, width = 7, name = 'curve_'+str(j)+'_'+str(i), justify = "right" )
                    c9.insert(0, np.round(tab.curve[(3*i)+2][j],1))
                    c9.grid(row =  9+len(fra_rates)+i, column = 12+j)
                
                
                
            for i in np.arange(len(fly_rates)):
                c4 = tk.Entry(self, width = 5, name = 'fly_leg1_'+str(i), bg = "light blue")
                c4.insert(0, fly_rates[i][0])
                c5 = tk.Entry(self, width = 5, name = 'fly_leg2_'+str(i), bg = "light blue")
                c5.insert(0, fly_rates[i][1])
                c6 = tk.Entry(self, width = 5, name = 'fly_leg3_'+str(i), bg = "light blue")
                c6.insert(0, fly_rates[i][2])
                c4.grid(row = 9+len(fra_rates)+len(curve_rates)+i, column = 6)
                c5.grid(row = 9+len(fra_rates)+len(curve_rates)+i, column = 7)
                c6.grid(row = 9+len(fra_rates)+len(curve_rates)+i, column = 8)
                
                c10 = ttk.Entry(self, width = 7, name = 'fly_'+str(i))
                c10.insert(0, np.round(tab.fly[i*3],3))
                c10.grid(row =  9+len(fra_rates)+len(curve_rates)+i, column = 9)
                
                c11 = ttk.Entry(self, width = 5, name = 'fly_chg'+str(i))
                c11.insert(0, np.round(tab.fly[(3*i)+1][0],1))
                c11.grid(row =  9+len(fra_rates)+len(curve_rates)+i, column = 10)
                c11.configure({"foreground": chg_colour[int(np.max([np.sign(  tab.fly[(3*i)+1][0]  ),0]))] })
                
                for j in np.arange(4):
                    c9 = ttk.Entry(self, width = 7, name = 'fly_'+str(j)+'_'+str(i), justify = "right")
                    c9.insert(0, np.round(tab.fly[(3*i)+2][j],1))
                    c9.grid(row =  9+len(fra_rates)+len(curve_rates)+i, column = 12+j, sticky = 'E')
            
#            for widget in self.winfo_children()[9:]:
#                 print(widget)
            Msg_Build['text'] = "Done @"+current_time
            
#        build_button = ttk.Button(self, text="Build", width = 14, command = BuildButton )
#        build_button.grid(column=5, row=1, rowspan = 1, columnspan = 2, sticky=tk.W, pady=5)
        
        
        

class Eco(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)
        
        label_tab = tk.Label(self, text = "Eco", font = LARGE_FONT, bg="light grey", fg = 'blue')
        label_tab.grid(row = 0, column = 0, columnspan = 5, sticky = 'W')
        
        ticker_lstbox = tk.Listbox(self, selectmode='multiple', width=14, height=10, exportselection = False)
        ticker_lstbox.grid(column=0, row=2, rowspan = 15, columnspan=1, sticky = 'W', padx=5)
        m = ["GDP", "CPI", "PCE", "Core-PCE", "UNEMP", "FISC"]
        for index, element in enumerate(m):
            ticker_lstbox.insert(index, element)
        
        country_lstbox = tk.Listbox(self, selectmode='multiple', width=14, height=10, exportselection = False)
        country_lstbox.grid(column=1, row=2, rowspan = 20, columnspan=1, sticky = 'W', padx=5)
        m2 = ["US", "EU", "GB", "DE", "FR", "IT", "ES", "CA", "AU", "NZ", "SE", "NO", "CH", "JP", "KR", "CN"]
        for index, element in enumerate(m2):
            country_lstbox.insert(index, element)
        
        yr_lstbox = tk.Listbox(self, selectmode='multiple', width=14, height=10, exportselection = False)
        yr_lstbox.grid(column=2, row=2, rowspan = 15, columnspan=1, sticky = 'W', padx=5)
        m3 = ["2022", "2023", "2024", "2025", "2026"]
        for index, element in enumerate(m3):
            yr_lstbox.insert(index, element)
        
        contrib_lstbox = tk.Listbox(self, selectmode='multiple', width=14, height=10, exportselection = False)
        contrib_lstbox.grid(column=3, row=2, rowspan = 20, columnspan=1, sticky = 'W', padx=5)
        m4 = ["BAR", "BOA", "BNP", "CE", "CIT", "CAG", "CSU", "DNS", "FTC", "GS", "HSB", "IG", "JPM", "MS", "NTX", "NS", "NDA", "PMA", "UBS", "WF", "SCB"]
        for index, element in enumerate(m4):
            contrib_lstbox.insert(index, element)
        
        offi_lstbox = tk.Listbox(self, selectmode='multiple', width=14, height=10, exportselection = False)
        offi_lstbox.grid(column=4, row=2, rowspan = 15, columnspan=1, sticky = 'W', padx=5)
        m5 = ["FED", "ECB", "BOE", "OEC", "IMF", "WB", "EU", "EC", "OBR", "IST", "DBK", "ISE", "BOC", "RBA", "RIK", "NOR", "NPC"]
        for index, element in enumerate(m5):
            offi_lstbox.insert(index, element)

               

        def PlotButton1():
            a1 = [ticker_lstbox.get(i) for i in ticker_lstbox.curselection()]
            a2 = [country_lstbox.get(i) for i in country_lstbox.curselection()]
            a3 = [yr_lstbox.get(i) for i in yr_lstbox.curselection()]
            a4 = [contrib_lstbox.get(i) for i in contrib_lstbox.curselection()]
            a5 = [offi_lstbox.get(i) for i in offi_lstbox.curselection()]
            
            print(a1, a2, a3, a4 ,a5)             
            
            f = ecfc_plot(a1[0], a2[0], a3[0], contrib1 = a4[0], off = a5[0])
            
            canvas = FigureCanvasTkAgg(f, self)
            mplcursors.cursor()
            canvas.draw()
            canvas.get_tk_widget().grid(row=30, column=5, columnspan = 7, sticky = 'nsew', padx=2, pady=2)

            # navigation toolbar
            toolbarFrame = tk.Frame(self)
            toolbarFrame.grid(row=32,column=5)
            toolbar = NavigationToolbar2Tk(canvas, toolbarFrame)

        plot_button1 = ttk.Button(self, text="Plot1", width = 10, command = PlotButton1)
        plot_button1.grid(column=0, row=1, rowspan = 1, columnspan = 1, sticky=tk.W, padx=5)
        
        def PlotButton2():
            a1 = [ticker_lstbox.get(i) for i in ticker_lstbox.curselection()]
            a2 = [country_lstbox.get(i) for i in country_lstbox.curselection()]
            a3 = [yr_lstbox.get(i) for i in yr_lstbox.curselection()]
            a4 = [contrib_lstbox.get(i) for i in contrib_lstbox.curselection()]
            a5 = [offi_lstbox.get(i) for i in offi_lstbox.curselection()]
            
            print(a1, a2, a3, a4 ,a5)             
            
            f = ecfc_plot(a1[0], a2[0], a3[0], contrib1 = a4[0], off = a5[0])
            
            canvas = FigureCanvasTkAgg(f, self)
            mplcursors.cursor()
            canvas.draw()
            canvas.get_tk_widget().grid(row=30, column=13, columnspan = 7, sticky = 'nsew', padx=2, pady=2)

            # navigation toolbar
            toolbarFrame = tk.Frame(self)
            toolbarFrame.grid(row=32,column=13)
            toolbar = NavigationToolbar2Tk(canvas, toolbarFrame)

        plot_button2 = ttk.Button(self, text="Plot2", width = 10, command = PlotButton2)
        plot_button2.grid(column=1, row=1, rowspan = 1, columnspan = 1, sticky=tk.W, padx=5)
        
        def PlotButton3():
            a1 = [ticker_lstbox.get(i) for i in ticker_lstbox.curselection()]
            a2 = [country_lstbox.get(i) for i in country_lstbox.curselection()]
            a3 = [yr_lstbox.get(i) for i in yr_lstbox.curselection()]
            a4 = [contrib_lstbox.get(i) for i in contrib_lstbox.curselection()]
            a5 = [offi_lstbox.get(i) for i in offi_lstbox.curselection()]
            
            print(a1, a2, a3, a4 ,a5)             
            
            f = ecfc_plot(a1[0], a2[0], a3[0], contrib1 = a4[0], off = a5[0])
            
            canvas = FigureCanvasTkAgg(f, self)
            mplcursors.cursor()
            canvas.draw()
            canvas.get_tk_widget().grid(row=45, column=5, columnspan = 7, sticky = 'nsew', padx=2, pady=2)

            # navigation toolbar
            toolbarFrame = tk.Frame(self)
            toolbarFrame.grid(row=46,column=5)
            toolbar = NavigationToolbar2Tk(canvas, toolbarFrame)

        plot_button3 = ttk.Button(self, text="Plot3", width = 10, command = PlotButton3)
        plot_button3.grid(column=2, row=1, rowspan = 1, columnspan = 1, sticky=tk.W, padx=5)

        def PlotButton4():
            a1 = [ticker_lstbox.get(i) for i in ticker_lstbox.curselection()]
            a2 = [country_lstbox.get(i) for i in country_lstbox.curselection()]
            a3 = [yr_lstbox.get(i) for i in yr_lstbox.curselection()]
            a4 = [contrib_lstbox.get(i) for i in contrib_lstbox.curselection()]
            a5 = [offi_lstbox.get(i) for i in offi_lstbox.curselection()]
            
            print(a1, a2, a3, a4 ,a5)             
            
            f = ecfc_plot(a1[0], a2[0], a3[0], contrib1 = a4[0], off = a5[0])
            
            canvas = FigureCanvasTkAgg(f, self)
            mplcursors.cursor()
            canvas.draw()
            canvas.get_tk_widget().grid(row=45, column=13, columnspan = 7, sticky = 'nsew', padx=2, pady=2)

            # navigation toolbar
            toolbarFrame = tk.Frame(self)
            toolbarFrame.grid(row=46,column=13)
            toolbar = NavigationToolbar2Tk(canvas, toolbarFrame)

        plot_button4 = ttk.Button(self, text="Plot4", width = 10, command = PlotButton4)
        plot_button4.grid(column=3, row=1, rowspan = 1, columnspan = 1, sticky=tk.W, padx=5)
        







#app  = Quix()
#app.mainloop()
