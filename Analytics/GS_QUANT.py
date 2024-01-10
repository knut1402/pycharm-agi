###### GS QUANT
gs_client_id ='2eb2f48872304c1d94fa1642fa691afe'
gs_secret_key ='91cb9c89110495d1f62d0ab0c4014555c992c2509de8f5ae2b8bf1a2d3c86bd4'


from gs_quant.session import GsSession
GsSession.use(client_id=gs_client_id, client_secret=gs_secret_key, scopes=('read_product_data','run_analytics'))

from datetime import date, timedelta, datetime
from gs_quant.data import Dataset
import pydash

ds = Dataset('IR_SWAPTION_VOLS_V1_STANDARD')


start_date = date(2019, 1, 15)
end_date = date(2019, 1, 18)

data = ds.get_data(start_date, end_date, assetId=["MA07CYVJYXCD7TJ3"])
data.head()









############### Backtesting Swaptions

from gs_quant.backtests.triggers import PeriodicTrigger, PeriodicTriggerRequirements
from gs_quant.backtests.actions import AddTradeAction
from gs_quant.common import PayReceive, Currency
from gs_quant.instrument import IRSwaption

from datetime import date

start_date, end_date = date(2020, 1, 1), date(2020, 12, 1)
# define dates on which actions will be triggered (1b=every business day here)
trig_req = PeriodicTriggerRequirements(start_date=start_date, end_date=end_date, frequency='1b')



# straddle is the position we'll be adding (note it's a short position since buy_sell='Sell')
straddle = IRSwaption(PayReceive.Straddle, '10y', Currency.USD, expiration_date='1m', notional_amount=1e8, buy_sell='Sell')

# this action specifies we will add the straddle when this action is triggered and hold it until expiration_date
action = AddTradeAction(straddle, 'expiration_date')

# we will now combine our trigger requirement and action to produce a PeriodicTrigger
# Note, action can be a list if there are multiple actions
trigger = PeriodicTrigger(trig_req, action)






