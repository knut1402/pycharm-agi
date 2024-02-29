import numpy as np
import pandas as pd

from bokeh.models import ColumnDataSource, TapTool
from bokeh.events import Tap

from bokeh.plotting import figure
from bokeh.layouts import column

from bokeh.io import curdoc
from bokeh.client import push_session, pull_session

x = np.random.randn(1001)
y = np.random.randn(1001)

cat1 = np.random.rand(1001) * 10.0
cat2 = np.random.rand(1001) * 10.0

data = np.column_stack((x,y,cat1,cat2))

df = pd.DataFrame(data=data, columns=('x','y','cat1','cat2'))
SRC = ColumnDataSource(df)


TOOLTIPS = [
    ("x", "@x"),
    ("y", "@y"),
    ("Category 1", "@cat1"),
    ("Category 2", "@cat2")]

TOOLS="pan,wheel_zoom,zoom_in,zoom_out,box_zoom,reset,tap"
cplot = figure(tools = TOOLS, tooltips=TOOLTIPS)
cplot.circle("x", "y", source=SRC)

bSource = ColumnDataSource(dict(x=['cat1','cat2'], top=[None]*2))
bplot = figure(x_range=('cat1','cat2'))
bplot.vbar(x='x', top='top', source=bSource)

def callback(event):
    SELECTED = SRC.selected.indices
    print("SELECTED {:}".format(SELECTED))
    if len(SELECTED) > 1:
        SELECTED = SELECTED[-1] # last point in case of multiselect
    bSource.patch(dict(top=[(slice(2),[SRC.data['cat1'][SELECTED],SRC.data['cat2'][SELECTED]])]))

taptool = cplot.select(type=TapTool)
cplot.on_event(Tap, callback)

curdoc().add_root(column(cplot, bplot))

