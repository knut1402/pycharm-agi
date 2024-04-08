import warnings
warnings.filterwarnings('ignore')

import QuantLib as ql
import numpy as np
import pandas as pd
import itertools

from scipy.stats import norm
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

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



# Some utility functions used later to plot 3D vol surfaces, generate paths, and generate vol surface from Heston params
def plot_vol_surface(vol_surface, plot_years=np.arange(0.1, 3, 0.1), plot_strikes=np.arange(70, 130, 1), funct='blackVol'):
    if type(vol_surface) != list:
        surfaces = [vol_surface]
    else:
        surfaces = vol_surface

    fig = plt.figure()
    ax = fig.add_subplot(projection = '3d')
    X, Y = np.meshgrid(plot_strikes, plot_years)

    for surface in surfaces:
        method_to_call = getattr(surface, funct)

        Z = np.array([method_to_call(float(y), float(x))
                      for xr, yr in zip(X, Y)
                          for x, y in zip(xr,yr) ]
                     ).reshape(len(X), len(X[0]))

        surf = ax.plot_surface(X,Y,Z, rstride=1, cstride=1, linewidth=0.1)

    fig.colorbar(surf, shrink=0.5, aspect=5)
    plt.show()

def generate_multi_paths_df(sequence, num_paths):
    spot_paths = []
    vol_paths = []

    for i in range(num_paths):
        sample_path = seq.next()
        values = sample_path.value()

        spot, vol = values

        spot_paths.append([x for x in spot])
        vol_paths.append([x for x in vol])

    df_spot = pd.DataFrame(spot_paths, columns=[spot.time(x) for x in range(len(spot))])
    df_vol = pd.DataFrame(vol_paths, columns=[spot.time(x) for x in range(len(spot))])

    return df_spot, df_vol

def create_vol_surface_mesh_from_heston_params(today, calendar, spot, v0, kappa, theta, rho, sigma,
                                               rates_curve_handle, dividend_curve_handle,
                                               strikes = np.linspace(40, 200, 161), tenors = np.linspace(0.1, 3, 60)):
    quote = ql.QuoteHandle(ql.SimpleQuote(spot))

    heston_process = ql.HestonProcess(rates_curve_handle, dividend_curve_handle, quote, v0, kappa, theta, sigma, rho)
    heston_model = ql.HestonModel(heston_process)
    heston_handle = ql.HestonModelHandle(heston_model)
    heston_vol_surface = ql.HestonBlackVolSurface(heston_handle)

    data = []
    for strike in strikes:
        data.append([heston_vol_surface.blackVol(tenor, strike) for tenor in tenors])

    expiration_dates = [calendar.advance(today, ql.Period(int(365*t), ql.Days)) for t in tenors]
    implied_vols = ql.Matrix(data)
    feller = 2 * kappa * theta - sigma ** 2

    return expiration_dates, strikes, implied_vols, feller



today = ql.Date(datetime.datetime.now().day, datetime.datetime.now().month, datetime.datetime.now().year)
c = ccy('SOFR_DC', today)
calendar = c.cal
sofr_live = ois_dc_build('SOFR_DC')
ester_live = ois_dc_build('ESTER_DC')
flat_ts = ql.YieldTermStructureHandle(sofr_live.curve)
dividend_ts = ql.YieldTermStructureHandle(sofr_live.curve)
spot = 1.085
strikes = np.linspace(0.95, 1.25, 31)
tenors = np.linspace(1, 24, 24)/12

dates, strikes, vols, feller = create_vol_surface_mesh_from_heston_params(today, calendar, spot, 0.0225, 1.0, 0.0625, -0.25, 0.3, flat_ts, dividend_ts, strikes, tenors)
local_vol_surface = ql.BlackVarianceSurface(today, calendar, dates, strikes, vols, ql.ActualActual(ql.ActualActual.ISDA))
plot_vol_surface(local_vol_surface,plot_years=tenors, plot_strikes=strikes)

[vols[int(i)][0] for i in np.arange(31)]
[vols[0][int(i)] for i in np.arange(24)]

len(strikes)

## Calculate the Dupire instantaneous vol
spot_quote = ql.QuoteHandle(ql.SimpleQuote(spot))

local_vol_surface.setInterpolation("bicubic")
local_vol_handle = ql.BlackVolTermStructureHandle(local_vol_surface)
local_vol = ql.LocalVolSurface(local_vol_handle, flat_ts, dividend_ts, spot_quote)
local_vol.enableExtrapolation()

# Plot the Dupire surface ...
plot_vol_surface(local_vol, plot_years=tenors, plot_strikes=strikes, funct='localVol')

# Calibrate Heston Process
v0 = 0.015; kappa = 2.0; theta = 0.065; rho = -0.3; sigma = 0.45
feller = 2 * kappa * theta - sigma ** 2

heston_process = ql.HestonProcess(flat_ts, dividend_ts, spot_quote, v0, kappa, theta, sigma, rho)
heston_model = ql.HestonModel(heston_process)

# How does the vol surface look at the moment?
heston_handle = ql.HestonModelHandle(heston_model)
heston_vol_surface = ql.HestonBlackVolSurface(heston_handle)

# Plot the vol surface ...
plot_vol_surface([local_vol_surface, heston_vol_surface], plot_years=tenors, plot_strikes=strikes)

#Run the local vol fitting and calculate the leverage function

# Calibrate via Monte-Carlo
end_date = c.cal.advance(today,ql.Period('1Y'))
generator_factory = ql.MTBrownianGeneratorFactory(43)
calibration_paths_vars = [2**15, 2**17, 2**19, 2**20]
time_steps_per_year, n_bins = 365, 201

for calibration_paths in calibration_paths_vars:
    print("Paths: {}".format(calibration_paths))
    stoch_local_mc_model = ql.HestonSLVMCModel(local_vol, heston_model, generator_factory, end_date, time_steps_per_year, n_bins, calibration_paths)

    a = time.time()
    leverage_functon = stoch_local_mc_model.leverageFunction()
    b = time.time()

    print("calibration took {0:2.1f} seconds".format(b-a))
    plot_vol_surface(leverage_functon, funct='localVol', plot_years=np.arange(0.1, 0.98, 0.1),plot_strikes=strikes)
    plt.pause(0.05)

#### Generating paths for Stoch Vol
num_paths = 25000
timestep = 32
length = 1
times = ql.TimeGrid(length, timestep)

stoch_local_process = ql.HestonSLVProcess(heston_process, leverage_functon)
dimension = stoch_local_process.factors()

rng = ql.GaussianRandomSequenceGenerator(ql.UniformRandomSequenceGenerator(dimension * timestep, ql.UniformRandomGenerator()))
seq = ql.GaussianMultiPathGenerator(stoch_local_process, list(times), rng, False)

df_spot, df_vol = generate_multi_paths_df(seq, num_paths)

fig = plt.figure(figsize=(20,10))
plt.subplot(2, 2, 1)
plt.plot(df_spot.iloc[0:10].transpose())
plt.subplot(2, 2, 2)
plt.hist(df_spot[1.0])
plt.subplot(2, 2, 3)
plt.plot(df_vol.iloc[0:10].transpose())
plt.subplot(2, 2, 4)
plt.hist(df_vol[1.0])
plt.show()

(df_spot[1.0] - 1.1).clip(lower=0).mean()



slv_engine = ql.FdHestonVanillaEngine(heston_model, 400, 400, 100, 0, ql.FdmSchemeDesc.Hundsdorfer(), leverage_functon)
option = ql.EuropeanOption(ql.PlainVanillaPayoff(ql.Option.Call, 1.1), ql.EuropeanExercise(ql.Date(20,9,2024)))
option.setPricingEngine(slv_engine)
option.NPV()

option.setPricingEngine(engine)
option.NPV()


##### Build a Heston Surface

flat_ts =  ql.YieldTermStructureHandle(sofr_live.curve)
dividend_ts =  ql.YieldTermStructureHandle(ester_live.curve)
spot = 1.085
dividend_rate = 0.00
dividend_ts = ql.YieldTermStructureHandle(ql.FlatForward(today, dividend_rate, ql.ActualActual(ql.ActualActual.ISDA)))


# dummy parameters
v0 = 0.01; kappa = 0.2; theta = 0.02; rho = -0.75; sigma = 0.5;

process = ql.HestonProcess(flat_ts, dividend_ts, ql.QuoteHandle(ql.SimpleQuote(spot)), v0, kappa, theta, sigma, rho)
model = ql.HestonModel(process)
engine = ql.AnalyticHestonEngine(model)
heston_helpers = []

data = [
    [1.0092, 6.971],
    [1.0305, 6.647],
    [1.0631, 6.081],
    [1.0947, 5.686],
    [1.1223, 5.574],
    [1.1506, 5.650],
    [1.1687, 5.739]]

tenor = ql.Period('6M')
for strike, vol in data:
    helper = ql.HestonModelHelper(tenor, ql.TARGET(), spot, strike, ql.QuoteHandle(ql.SimpleQuote(vol / 100)), flat_ts, dividend_ts )
    helper.setPricingEngine(engine)
    heston_helpers.append(helper)

lm = ql.LevenbergMarquardt(1e-10, 1e-10, 1e-10)
model.calibrate(heston_helpers, lm,  ql.EndCriteria(500, 50, 1.0e-10,1.0e-10, 1.0e-10))
theta, kappa, sigma, rho, v0 = model.params()

print(f"theta = {theta:.4f}, kappa = {kappa:.4f}, sigma = {sigma:.4f}, rho = {rho:.4f}, v0 = {v0:.4f}")

avg = 0.0
summary = []
for i, opt in enumerate(heston_helpers):
    err = (opt.modelValue()/opt.marketValue() - 1.0)
    summary.append((
        data[i][0], opt.marketValue(),
        opt.modelValue(),
        100.0*(opt.modelValue()/opt.marketValue() - 1.0)))
    avg += abs(err)
avg = avg*100.0/len(heston_helpers)

print("Average Abs Error (%%) : %5.3f" % (avg))
df = pd.DataFrame(
    summary,
    columns=["Strikes", "Market value", "Model value", "Relative error (%)"],
    index=['']*len(summary))




############## delta works
from scipy.stats import norm

f = 1.0920
phi = 1
delta = 0.25
vol = 0.057
t = 0.5

f*np.exp((norm.ppf(phi*delta)*vol*((t)**0.5)*(-phi))+(0.5*(vol**2)*t))



today = ql.Date(datetime.datetime.now().day, datetime.datetime.now().month, datetime.datetime.now().year)
c = ccy('SOFR_DC', today)
pair = 'EURUSD'
fwd_ticker = 'EUR'
tenors = ['1W','2W','3W','1M', '2M', '3M', '4M', '6M', '9M', '1Y']
tenor_dates = [c.cal.advance(today,ql.Period(i)) for i in tenors]
fwd_tickers = [fwd_ticker+i+' BGN Curncy' for i in tenors[:-1]]+[fwd_ticker+'12M BGN Curncy']
fwd_points = np.array(con.bdh(fwd_tickers, ['PX_LAST'], bbg_date_str(today), bbg_date_str(today), longdata=True).set_index('ticker').loc[fwd_tickers]['value'])
fwds = con.bdh([pair+' Curncy'], ['PX_LAST'], bbg_date_str(today), bbg_date_str(today), longdata=True)['value'][0]+(fwd_points/10000)
atm_tickers = [pair+'V'+i+' Curncy' for i in tenors]
atm_vols = np.array(con.bdh(atm_tickers, ['PX_LAST'], bbg_date_str(today), bbg_date_str(today), longdata=True).set_index('ticker').loc[atm_tickers]['value'])
delta = [10,25]
delta_fmt = list(np.array(delta)*-1)+list(np.array(delta[::-1])*1)
strike_params = [[( delta_fmt[j]/100, np.sign(delta_fmt[j]), fwds[k], atm_vols[k]/100, (tenor_dates[k]-today)/365 ) for j in np.arange(len(delta_fmt))] for k in np.arange(len(tenor_dates))]

strikes = dict([(key, []) for key in tenors])
for k in np.arange(len(tenors)):
    for j in np.arange(len(delta_fmt)):
        d1, p1, f1, v1, t1 = strike_params[k][j]
        strikes[tenors[k]].append(f1 * np.exp((norm.ppf(p1 * d1) * v1 * ((t1) ** 0.5) * (-p1)) + (0.5 * (v1 ** 2) * t1)))

rr_tickers = [[pair+str(j)+'R'+i+' Curncy' for j in delta] for i in tenors]
fl_tickers = [[pair+str(j)+'B'+i+' Curncy' for j in delta] for i in tenors]

rr = np.array(con.bdh(flat_lst(rr_tickers), ['PX_LAST'], bbg_date_str(today), bbg_date_str(today), longdata=True).set_index('ticker').loc[flat_lst(rr_tickers)]['value'])
fl = np.array(con.bdh(flat_lst(fl_tickers), ['PX_LAST'], bbg_date_str(today), bbg_date_str(today), longdata=True).set_index('ticker').loc[flat_lst(fl_tickers)]['value'])

smile_vol = fl+np.repeat(atm_vols,2)
skew_vol = []
for i in np.arange(0,len(smile_vol),2):
    skew_vol.append([ smile_vol[i]-0.5*rr[i], smile_vol[i+1]-0.5*rr[i+1]  , smile_vol[i+1]+0.5*rr[i+1],   smile_vol[i]+0.5*rr[i] ] )


expiry_dates = tenor_dates
data = [skew_vol[j][:2]+[ atm_vols[j]]+skew_vol[j][2:] for j in np.arange(len(tenors))]
implied_vols = ql.Matrix( (2*len(delta))+1, len(tenors))
for i in range(implied_vols.rows()):
    for j in range(implied_vols.columns()):
        implied_vols[i][j] = data[j][i]/100

k = [strikes[tenors[j]][:2]+[ fwds[j]]+strikes[tenors[j]][2:] for j in np.arange(len(tenors))]
k2 = ql.Matrix( (2*len(delta))+1, len(tenors))
for i in range(k2.rows()):
    for j in range(k2.columns()):
        k2[i][j] = k[j][i]


strikes = [527.50, 560.46, 593.43, 626.40, 659.37, 692.34, 725.31, 758.28]

black_var_surface = ql.BlackVarianceSurface(today, c.cal, expiry_dates, k2, implied_vols, ql.ActualActual(ql.ActualActual.ISDA))

############ heston
flat_ts =  ql.YieldTermStructureHandle(sofr_live.curve)
dividend_ts =  ql.YieldTermStructureHandle(ester_live.curve)
data2 = [[ [data[m][n],k[m][n]] for n in np.arange(5)] for m in np.arange(len(tenors))]

data3=[]
for i in np.arange(len(data2)):
    for j in np.arange(5):
        data3.append(data2[i][j])

v0 = 0.01; kappa = 0.2; theta = 0.02; rho = -0.75; sigma = 0.5;
process = ql.HestonProcess(flat_ts, dividend_ts, ql.QuoteHandle(ql.SimpleQuote(spot)), v0, kappa, theta, sigma, rho)
model = ql.HestonModel(process)
engine = ql.AnalyticHestonEngine(model)
heston_helpers = []

spot = con.bdh([pair+' Curncy'], ['PX_LAST'], bbg_date_str(today), bbg_date_str(today), longdata=True)['value'][0]
for t in np.arange(len(tenors)):
    for vol, strike in data2[t]:
        helper = ql.HestonModelHelper(ql.Period(tenors[t]), c.cal, spot, strike, ql.QuoteHandle(ql.SimpleQuote(vol/100)), flat_ts, dividend_ts )
        helper.setPricingEngine(engine)
        heston_helpers.append(helper)

lm = ql.LevenbergMarquardt(1e-12, 1e-12, 1e-12)
model.calibrate(heston_helpers, lm,  ql.EndCriteria(500, 50, 1.0e-12,1.0e-12, 1.0e-12))
theta, kappa, sigma, rho, v0 = model.params()

print(f"theta = {theta:.4f}, kappa = {kappa:.4f}, sigma = {sigma:.4f}, rho = {rho:.4f}, v0 = {v0:.4f}")

avg = 0.0
summary = []
for i, opt in enumerate(heston_helpers):
    err = (opt.modelValue()/opt.marketValue() - 1.0)
    summary.append((
        data3[i][1], opt.marketValue(),
        opt.modelValue(),
        100.0*(opt.modelValue()/opt.marketValue() - 1.0)))
    avg += abs(err)
avg = avg*100.0/len(heston_helpers)

print("Average Abs Error (%%) : %5.3f" % (avg))
df = pd.DataFrame(
    summary,
    columns=["Strikes", "Market value", "Model value", "Relative error (%)"],
    index=['']*len(summary))


option = ql.EuropeanOption(ql.PlainVanillaPayoff(ql.Option.Call, 1.15), ql.EuropeanExercise(ql.Date(20,9,2024)))
option.setPricingEngine(engine)
option.NPV()*100
