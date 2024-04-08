import panel as pn

from pn_swap_monitor import SwapMon
from pn_inflation_swap import InflSwapMon
from pn_swap_plot import SwapPlot
from pn_swap_heatmap import SwapHeatMap
from pn_wirp_plot import WirpPlot
from pn_listed_options import ListedTab
from pn_ecfc import ECFC
from pn_linker_rv import LinkerRV


class Quix3:
    def __init__(self):
        self.tab1 = SwapMon()
        self.tab2 = InflSwapMon()
        self.tab3 = SwapPlot()
        self.tab4 = SwapHeatMap()
        self.tab5 = WirpPlot()
        self.tab6 = ListedTab()
        self.tab7 = ECFC()
        self.tab8 = LinkerRV()

        self.main = pn.Tabs( ('SWPM',self.tab1.view),
                             ('INFL',self.tab2.view),
                             ('SW_PLOT',self.tab3.view),
                             ('SW_HM', self.tab4.view),
                             ('WIRP',self.tab5.view),
                             ('LISTED', self.tab6.view),
                             ('ECFC',self.tab7.view),
                             ('LINKER',self.tab8.view))
    def publish(self):
        return self.main.servable()


quix_layout = Quix3()
quix_layout.publish()

