
import os
import pandas as pd
import numpy as np
import datetime
import pdblp
import runpy
import QuantLib as ql
import matplotlib as mpl
import matplotlib.pyplot as plt
from tabulate import tabulate
from Conventions import FUT_CT, ccy, ccy_infl
from OIS_DC_BUILD import get_wirp_hist, get_wirp

con = pdblp.BCon(debug=False, port=8194, timeout=50000)
con.start()

############################# OIS MEETING HISTORICAL
################## Run at init for Conventions

for j in ['SOFR_DC','ESTER_DC','SONIA_DC']:
#    print('add1:  ', os.getcwd())
    df = get_wirp_hist(j)
#    print('add2:  ', os.getcwd())
    os.chdir('C:\\Users\A00007579\PycharmProjects\pythonProject\DataLake')
#    print('add3:  ', os.getcwd())
    df.to_pickle(j+'_OIS_MEETING_HIST.pkl')
#    print('add4:  ', os.getcwd())
    os.chdir('C:\\Users\A00007579\PycharmProjects\pythonProject')
#    print('add5:  ', os.getcwd())




