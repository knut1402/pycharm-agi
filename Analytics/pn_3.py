import panel as pn

from pn_2 import Swap_Plot, InflSwapMon
from pn_swap_monitor import SwapMon
from pn_ecfc import ECFC


class Quix3:
    def __init__(self):
        self.tab1 = SwapMon()
        self.tab2 = InflSwapMon()
        self.tab3 = Swap_Plot()
        self.tab4 = ECFC()

        self.main = pn.Tabs( ('SWPM',self.tab1.view),
                             ('INFL',self.tab2.view),
                             ('SW_PLOT',self.tab3.view),
                             ('ECFC',self.tab4.view))
    def publish(self):
        return self.main.servable()


quix_layout = Quix3()
quix_layout.publish()


#q1 = SwapMon()
#q2 = InflSwapMon().view()
#q3 = pn.Row(q2).servable()


