
import os
import time
import pandas as pd
import numpy as np
import datetime
import pdblp
import runpy
import QuantLib as ql
import matplotlib as mpl
import matplotlib.pyplot as plt
from tabulate import tabulate
from Utilities import *
from Conventions import FUT_CT, ccy, ccy_infl
from OIS_DC_BUILD import get_wirp_hist, get_wirp
from INF_ZC_BUILD import update_inflation_fixing_history
from BATCH_HIST import batch_ois, batch_libor, batch_ois_update

con = pdblp.BCon(debug=False, port=8194, timeout=50000)
con.start()

############################# OIS MEETING HISTORICAL
################## Run at init for Conventions

def update_hist(force_update=0):
    os.chdir('C:\\Users\A00007579\PycharmProjects\pythonProject')
    ois_hist_file_last_time = os.path.getmtime('.\DataLake\SOFR_DC_OIS_MEETING_HIST.pkl')
    mins_from_last_update1 = datetime.timedelta(seconds=time.time()-ois_hist_file_last_time).seconds/60

    os.chdir('C:\\Users\A00007579\PycharmProjects\pythonProject')
    fixing_hist_file_last_time = os.path.getmtime('.\DataLake\HICPxT_fixing_hist.pkl')
    mins_from_last_update2 = datetime.timedelta(seconds=time.time()-fixing_hist_file_last_time).seconds/60

    if (mins_from_last_update1 > 600) or (force_update == 1):
        for j in ['SOFR_DC', 'ESTER_DC', 'SONIA_DC', 'AONIA_DC', 'CORRA_DC']:
            df = get_wirp_hist(j, write =1, update=1)
            print(j+'  ois meeting hist updated')
    else:
        print('latest ois (meeting date) update: ',datetime.datetime.fromtimestamp(ois_hist_file_last_time, tz=datetime.timezone.utc).strftime('%d-%b-%Y @ %H:%M'))

    if (mins_from_last_update2 > 600) or (force_update == 1):
        update_inflation_fixing_history(['UKRPI','HICPxT','USCPI'])
        os.chdir('C:\\Users\A00007579\PycharmProjects\pythonProject')
        print('inf fixing hist updated')
    else:
        print('latest infl fixing update: ',datetime.datetime.fromtimestamp(fixing_hist_file_last_time, tz=datetime.timezone.utc).strftime('%d-%b-%Y @ %H:%M'))

    return

def update_swap_hist():
    for i, j, k in ((pd.read_csv("./DataLake/query-usd-ois.csv"), 'SOFR_DC', 'SOFR_H'),
                    (pd.read_csv("./DataLake/query-eur-ester.csv"), 'ESTER_DC', 'ESTER_H'),
                    (pd.read_csv("./DataLake/query-gbp-sonia.csv"), 'SONIA_DC', 'SONIA_H'),
                    (pd.read_csv("./DataLake/query-chf-saron.csv"), 'SARON_DC', 'SARON_H'),
                    (pd.read_csv("./DataLake/query-aud-aonia.csv"), 'AONIA_DC', 'AONIA_H'),
                    (pd.read_csv("./DataLake/query-cad-corra.csv"), 'CORRA_DC', 'CORRA_H')):
        batch_ois_update(i, j, k)
    return


update_swap_hist()

