import panel as pn

from pn_2 import InflSwapMon
from pn_swap_plot import SwapPlot
from pn_swap_monitor import SwapMon
from pn_wirp_plot import WirpPlot
from pn_listed_options import ListedTab
from pn_ecfc import ECFC


class Quix3:
    def __init__(self):
        self.tab1 = SwapMon()
        self.tab2 = InflSwapMon()
        self.tab3 = SwapPlot()
        self.tab4 = WirpPlot()
        self.tab5 = ListedTab()
        self.tab6 = ECFC()

        self.main = pn.Tabs( ('SWPM',self.tab1.view),
                             ('INFL',self.tab2.view),
                             ('SW_PLOT',self.tab3.view),
                             ('WIRP',self.tab4.view),
                             ('LISTED', self.tab5.view),
                             ('ECFC',self.tab6.view))
    def publish(self):
        return self.main.servable()


quix_layout = Quix3()
quix_layout.publish()

