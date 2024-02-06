#### Data Mining and Machine Learning
import os
import pandas as pd
import numpy as np
import math
import datetime
import pdblp
import eikon as ek
import runpy
import QuantLib as ql
# import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns
from tabulate import tabulate
from sklearn.preprocessing import minmax_scale
from sklearn.mixture import GaussianMixture
from scipy.stats import zscore
import pickle
import re
import concurrent.futures
import time

pd.set_option("display.max_columns", 10000)
pd.set_option("display.width", 10000)
## BBG API
con = pdblp.BCon(debug=False, port=8194, timeout=50000)
con.start()

from Utilities import *
from Conventions import FUT_CT, FUT_CT_Q, ccy, ccy_infl

data = pd.ExcelFile("./DataLake/eco_master.xlsx")
data_df = pd.read_excel(data,"EcoData")


def get_data(
    df, country, start, end=-1, cat1="all", cat2="all", change=6, roc=3, zs_period=0
):
#        df=data_df
#        country='AU'
#        cat2 = 'all'
#        start = '20000101'
#        zs_period = 20

    df = df[df["Country"] == country]
    if cat1 != "all":
        df = df[df["Cat1"] == cat1]
    if cat2 != "all":
        df = df[df["Cat2"] == cat2]

    tickers = df["Ticker"].tolist()
    labels = df["Label"].tolist()

    q1 = datetime.datetime(int(start[:4]), int(start[4:6]), int(start[-2:]))
    today = ql.Date(
        datetime.datetime.now().day,
        datetime.datetime.now().month,
        datetime.datetime.now().year,
    )
    q2 = ql_to_datetime(today)
    if end == -1:
        end_date = bbg_date_str(today, ql_date=1)

    df1 = pd.DataFrame(columns=labels, index=pd.date_range(start=q1, end=q2, freq="M"))
    for i in np.arange(len(tickers)):
        #        print(tickers[i])
        df2 = con.bdh(tickers[i], "PX_LAST", start, end_date, longdata=True)
        df2.index = df2["date"]
        df1[labels[i]] = df2["value"]

    #### dealing with weekly data
    for i in df[df["Freq"] != "M"]["Ticker"].tolist():
        df3 = con.bdh(i, "PX_LAST", start, end_date, longdata=True)
        df3.index = df3["date"]
        df3 = df3.resample("M").last()
        df1[df[df["Ticker"] == i]["Label"].tolist()[0]] = df3["value"]
    df1.name = "Raw"

    #### dealing with NaNs
    is_na_tab = pd.DataFrame(columns=["#", "First", "Last"], index=labels)
    for i in labels:
        is_na_tab["#"][i] = df1[i].isna().sum()
        is_na_tab["First"][i] = df1[i].first_valid_index()
        is_na_tab["Last"][i] = df1[i].last_valid_index()

    #### dealing with YoY transform
    df4 = df1.copy()
    df4.name = "Pct"
    t2 = df[df["IsIndex"] == 1]["Label"].tolist()
    for i in np.arange(len(t2)):
        df4[t2[i]] = np.round(100 * df1[t2[i]].pct_change(periods=12), 2)

    #### finding changes and roc
    df5 = pd.DataFrame(columns=labels)
    df5.name = "Chg"
    df6 = pd.DataFrame(columns=labels)
    df6.name = "ROC"
    df7 = pd.DataFrame(columns=labels)
    df7.name = "Pct_ROC"
    for i in labels:
        df5[i] = df1[i].diff(periods=change)
        df6[i] = df5[i].diff(periods=roc)
        df7[i] = df4[i].diff(periods=roc)

    #### finding_zscores
    z_score_excl = df[df["ZS_excl"] == 1]["Label"].tolist()

    z_df1 = pd.DataFrame(columns=labels, index=df1.index[-12 * zs_period :])
    z_df1.name = "ZScore_Raw"
    z_df4 = pd.DataFrame(columns=labels, index=df4.index[-12 * zs_period :])
    z_df4.name = "ZScore_Pct_Chg_YoY"
    z_df5 = pd.DataFrame(columns=labels, index=df5.index[-12 * zs_period :])
    z_df5.name = "ZScore_Raw_Chg_YoY"
    z_df6 = pd.DataFrame(columns=labels, index=df6.index[-12 * zs_period :])
    z_df6.name = "ZScore_Raw_ROC"
    z_df7 = pd.DataFrame(columns=labels, index=df7.index[-12 * zs_period :])
    z_df7.name = "ZScore_Pct_ROC"
    for i in labels:
        z_df1[i] = zscore(
            df1[i][-12 * zs_period :], nan_policy="omit"
        )  ####### check this z-score calc to confirm row wise operation + understand how we can make it row wise first/last non-nan  zscore(x, axis=1, nan_policy='omit')
        z_df4[i] = zscore(df4[i][-12 * zs_period :], nan_policy="omit")
        z_df5[i] = zscore(df5[i][-12 * zs_period :], nan_policy="omit")
        z_df6[i] = zscore(df6[i][-12 * zs_period :], nan_policy="omit")
        z_df7[i] = zscore(df7[i][-12 * zs_period :], nan_policy="omit")

    for j in [z_df1, z_df4, z_df5, z_df6, z_df7]:
        j["Avg"] = j.mean(axis=1)

    print(
        "Available:",
        "raw,",
        "df_pct,",
        "df_chg,",
        "df_roc,",
        "df_pct_roc,",
        "zs_raw,",
        "zs_pct,",
        "zs_chg,",
        "zs_roc,",
        "zs_pct_roc",
    )

    class get_data_output:
        def __init__(self):
            self.raw = df1
            self.nantab = is_na_tab
            self.df_pct = df4
            self.df_chg = df5
            self.df_roc = df6
            self.df_pct_roc = df7
            self.zs_raw = z_df1
            self.zs_pct = z_df4
            self.zs_chg = z_df5
            self.zs_roc = z_df6
            self.zs_pct_roc = z_df7
            self.zs_excl = z_score_excl

    return get_data_output()


def data_heatmap(df1, inst=[], n=10, minmax=True, fsize=[20, 30]):
    #    df1 = [us.zs_pct]
    #    n=5
    #    minmax = True
    #    inst = ['GT10 Govt']
    g_out = []

    if len(inst) == 0:
        df2 = df1
    else:
        df2 = []
        for i in np.arange(len(df1)):
            df2.append(df1[i].copy())
            for j in np.arange(len(inst)):
                t1 = con.bdh(
                    inst[j],
                    "PX_LAST",
                    bbg_date_str(
                        df1[i].index[0] - datetime.timedelta(days=32), ql_date=0
                    ),
                    bbg_date_str(
                        df1[i].index[-1] + datetime.timedelta(days=32), ql_date=0
                    ),
                    longdata=True,
                )
                t1.index = t1["date"]
                t1 = t1.resample("M").last()
                t1 = t1.loc[df1[i].index]
                df2[i][inst[j]] = t1["value"].diff(1)

    n_df = len(df2)
    if minmax:
        df = [minmax_scale(j) for j in df2]
    else:
        df = df2

    fig, axs = plt.subplots(n_df, 1, figsize=(fsize[0], fsize[1]))
    for i in np.arange(len(df)):
        ax1 = plt.subplot(2, 1, i + 1)
        sns.heatmap(
            df[i][(n * -12) :].T,
            cmap="vlag_r",
            linewidths=1.0,
            xticklabels=df2[i][(n * -12) :].index.strftime(("%b-%y")),
            yticklabels=df2[i].columns,
            fmt=".5g",
            cbar=False,
            ax=ax1,
        )
        ax1.xaxis.set_tick_params(labelsize=8)
        ax1.yaxis.set_tick_params(labelsize=12)
        plt.title(df1[i].name, fontsize=8, color="indigo", loc="left")

        ax2 = ax1.twinx()
        ax2.set_ylim(0, len(df2[i].columns))
        ax2.set_yticks(np.arange(0.5, len(df2[i].columns) + 0.5, 1))
        ax2.set_yticklabels(np.round(df2[i].iloc[-1][::-1], 1))
        ax2.yaxis.set_tick_params(labelsize=12)
    plt.show()
    #    g_out = g_out + [fig]
    return


def run_gmm(df, n, inst, zs_excl, feat_plot=0, is_zs=False):
    ##### Assumption is this is run for long z-score time frame. hence zs_exclude is valid.
    #    df = uk1.zs_pct
    #    zs_excl = uk1.zs_excl
    #    n = 6
    #    inst = ['GT10 Govt']
    #    feat_plot = ['ISM Mfg', 'Retail Sales']

    is_zs = True
    if is_zs:
        df = df.iloc[:, :-1]
    if feat_plot == 0:
        f1 = df.columns[0]
        f2 = df.columns[10]
    else:
        f1 = feat_plot[0]
        f2 = feat_plot[1]

    #    for i in lab2:
    #        print(i, df[i].isna().sum())

    lab2 = [n for n in df.columns if (n not in zs_excl)]
    X = df[lab2].dropna()

    #### Hom many components?
    n_components = np.arange(1, 10)
    models = [
        GaussianMixture(n, covariance_type="full", random_state=0).fit(X)
        for n in n_components
    ]
    plt.plot(n_components, [m.bic(X) for m in models], label="BIC")
    plt.plot(n_components, [m.aic(X) for m in models], label="AIC")
    plt.legend(loc="best")
    plt.xlabel("n_components")
    plt.title("Determine # of mixtures")
    plt.show()

    gmm = GaussianMixture(n_components=n, covariance_type="full").fit(X)
    labels = gmm.predict(X)
    unique, counts = np.unique(labels, return_counts=True)
    print(np.asarray((unique, counts)).T)
    plt.scatter(X[f1], X[f2], c=labels, s=40, cmap="viridis")
    ##### picking 2 features at random
    plt.title(f1 + " / " + f2)
    plt.show()

    colors = ["red", "blue", "green", "yellow", "black", "cyan", "grey", "pink"]
    colors2 = [colors[labels[i]] for i in np.arange(len(labels))]

    #### label plot of feature
    plt.figure(figsize=[10, 7])
    plt.scatter(X.index, X[f1], c=colors2, s=10)
    plt.title("Regimes of " + f1)
    plt.show()

    #### Plot instrument and regime
    fig, axs = plt.subplots(len(inst), 1, figsize=(8, len(inst * 6)))
    for i in np.arange(len(inst)):
        t1 = con.bdh(
            inst[i],
            "PX_LAST",
            bbg_date_str(df.index[0] - datetime.timedelta(days=32), ql_date=0),
            bbg_date_str(df.index[-1] + datetime.timedelta(days=32), ql_date=0),
            longdata=True,
        )
        t1.index = t1["date"]
        t1 = t1.resample("M").last()
        t1 = t1.loc[X.index]
        t1["chg"] = t1["value"].diff(1)

        ax1 = plt.subplot(2, 1, i + 1)
        ax1.scatter(t1.index, t1["value"], c=colors2, s=10)
        plt.title("Regimes of " + inst[i], fontsize=8, color="indigo", loc="left")
    plt.show()

    return
