
import json
from alpaca.trading.client import TradingClient
from alpaca.common.exceptions import APIError

'''

	Description:
		script to get info on a position
        NOTE: this script is untested

	Sources:
        https://alpaca.markets/sdks/python/api_reference/trading/positions.html#get-open-position
        https://alpaca.markets/sdks/python/api_reference/trading/models.html#alpaca.trading.models.Position

	'''

# API constants
LIVE_TRADING = False
with open('credentials.json') as f:
	creds = json.load(f)
ENDPOINT   = creds['live_trading' if LIVE_TRADING else 'paper_trading']['ENDPOINT']
API_KEY    = creds['live_trading' if LIVE_TRADING else 'paper_trading']['API_KEY_ID']
API_SECRET = creds['live_trading' if LIVE_TRADING else 'paper_trading']['SECRET_KEY']
trading_client = TradingClient(API_KEY, API_SECRET, paper=not LIVE_TRADING)

symbol = 'NVDA'
try:
    position = trading_client.get_open_position(symbol)
    print(type(position))
    print(position)
    # outputs:
    # <class 'alpaca.trading.models.Position'>
    # for details on the fields this class has go here
    # https://alpaca.markets/sdks/python/api_reference/trading/positions.html#get-open-position
    # https://alpaca.markets/sdks/python/api_reference/trading/models.html#alpaca.trading.models.Position
    print('asset_id', position.asset_id) # asset_id - ID of the asset. TYPE: UUID
    print('symbol', position.symbol) # symbol - Symbol of the asset. TYPE: str
    print('exchange', position.exchange) # exchange - Exchange name of the asset. TYPE: AssetExchange
    print('asset_class', position.asset_class) # asset_class - Name of the asset’s asset class. TYPE: AssetClass
    print('asset_marginable', position.asset_marginable) # asset_marginable - Indicates if this asset is marginable. TYPE: Optional[bool]
    print('avg_entry_price', position.avg_entry_price) # avg_entry_price - The average entry price of the position. TYPE: str
    print('qty', position.qty) # qty - The number of shares of the position. TYPE: str
    print('side', position.side) # side - “long” or “short” representing the side of the position. TYPE: PositionSide
    print('market_value', position.market_value) # market_value - Total dollar amount of the position. TYPE: Optional[str]
    print('cost_basis', position.cost_basis) # cost_basis - Total cost basis in dollars. TYPE: str
    print('unrealized_pl', position.unrealized_pl) # unrealized_pl - Unrealized profit/loss in dollars. TYPE: Optional[str]
    print('unrealized_plpc', position.unrealized_plpc) # unrealized_plpc - Unrealized profit/loss percent. TYPE: Optional[str]
    print('unrealized_intraday_pl', position.unrealized_intraday_pl) # unrealized_intraday_pl - Unrealized profit/loss in dollars for the day. TYPE: Optional[str]
    print('unrealized_intraday_plpc', position.unrealized_intraday_plpc) # unrealized_intraday_plpc - Unrealized profit/loss percent for the day. TYPE: Optional[str]
    print('current_price', position.current_price) # current_price - Current asset price per share. TYPE: Optional[str]
    print('lastday_price', position.lastday_price) # lastday_price - Last day’s asset price per share based on the closing value of the last trading day. TYPE: Optional[str]
    print('change_today', position.change_today) # change_today - Percent change from last day’s price. TYPE: Optional[str]
    print('swap_rate', position.swap_rate) # swap_rate - Swap rate is the exchange rate (without mark-up) used to convert the price into local currency or crypto asset. TYPE: Optional[str]
    print('avg_entry_swap_rate', position.avg_entry_swap_rate) # avg_entry_swap_rate - The average exchange rate the price was converted into the local currency at. TYPE: Optional[str]
    print('usd', position.usd) # usd - Represents the position in USD values. TYPE: USDPositionValues
    print('qty_available', position.qty_available) # qty_available - Total number of shares available minus open orders. TYPE: Optional[str]

except APIError as e:
    print('position does not exist')
    print(e)


