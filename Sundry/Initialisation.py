###### initialisation script

globals().clear()

import os
from importlib import reload
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import pandas as pd
import polars as pl
import numpy as np
import math
import datetime
import pdblp
import runpy
import QuantLib as ql
import matplotlib as mpl
#import matplotlib
mpl.get_backend()
import matplotlib.pyplot as plt
plt.interactive(False)
import seaborn as sns
from tabulate import tabulate
from sklearn.preprocessing import minmax_scale
from sklearn.mixture import GaussianMixture
from scipy.stats import zscore
from itertools import accumulate
import pickle
import re
import concurrent.futures
import time

pd.set_option('display.max_columns', 10000)
pd.set_option('display.width', 10000)
pd.options.display.float_format = '{:,}'.format
pd.options.mode.chained_assignment = None

## BBG API
con = pdblp.BCon(debug=False, port=8194, timeout=50000)
con.start()

from Utilities import *
from OIS_DC_BUILD import ois_dc_build, get_wirp, get_wirp_hist, ois_from_nodes
from OIS_MEET_HIST import update_hist,update_swap_hist
update_hist(force_update=0)
from Conventions import FUT_CT,FUT_CT_Q, ccy, ccy_infl, hist
from SWAP_BUILD import swap_build, libor_from_nodes
from SWAP_PRICER import Swap_Pricer, Swap_curve_fwd
from SWAP_TABLE import swap_table, swap_table2, curve_hmap
from INF_ZC_BUILD import infl_zc_swap_build, Infl_ZC_Pricer, inf_swap_table
from BOND_CURVES import bond_curve_build
from VOL_BUILD import build_vol_surf, build_vol_spline, bond_fut_opt_strat, get_sim_option_px, build_stir_vol_surf, stir_opt_strat
from PLOT import plt_curve, plt_inf_curve, plt_opt_strat, rates_hm, curve_hm, plt_ois_curve, plot_opt_vol_surf, plt_stir_opt_strat, plotool, ecfc_plot
from BOND_TABLES import linker_table
from INFL_CARRY import linker_carry_calc
from MINING import get_data, data_heatmap, run_gmm





import QUIXOTIC
app  = QUIXOTIC.Quix()
app.mainloop()

## Eikon API
import eikon as ek
eikon_app_key= '6ccde6df4ee247cea42850581c08b61c4126f047'
ek.set_app_key(eikon_app_key)
from SWAPTION import Swaption_Pricer, Swaption_Curve, usd_volc, gbp_volc, usd_volc_sofr     #### req eikon

