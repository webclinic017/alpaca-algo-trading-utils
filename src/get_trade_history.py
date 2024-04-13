
'''

    description
        script to get all trades of a given stock in a given timeframe

    sources
        https://alpaca.markets/sdks/python/api_reference/data/stock/historical.html
            ctrl f "get_stock_trades"
        https://alpaca.markets/sdks/python/api_reference/data/stock/requests.html#alpaca.data.requests.StockTradesRequest
        https://alpaca.markets/sdks/python/api_reference/data/enums.html#alpaca.data.enums.DataFeed

'''

import json
from datetime import datetime, timedelta
from alpaca.data.requests import StockTradesRequest
from alpaca.data.enums import DataFeed
from alpaca.data import StockHistoricalDataClient


# Alpaca API Constants
LIVE_TRADING = False
CREDENTIALS_FILEPATH = \
    "/home/luke/rooms/money/exchanges_and_data_sources/exchanges/alpaca/alpaca-algo-trading-utils/src/credentials.json"
with open(CREDENTIALS_FILEPATH) as f:
	creds = json.load(f)
ENDPOINT   = creds['live_trading' if LIVE_TRADING else 'paper_trading']['ENDPOINT']
API_KEY    = creds['live_trading' if LIVE_TRADING else 'paper_trading']['API_KEY_ID']
API_SECRET = creds['live_trading' if LIVE_TRADING else 'paper_trading']['SECRET_KEY']
HEADERS = {
    "accept": "application/json",
    "APCA-API-KEY-ID": API_KEY,
    "APCA-API-SECRET-KEY": API_SECRET,
}

data_client = StockHistoricalDataClient(API_KEY, API_SECRET)


tickers = ["AAPL"]
end_time = datetime.now()
start_time = end_time - timedelta(hours=1)
request_params = StockTradesRequest(
    symbol_or_symbols=tickers, # must be a list, see NOTE below for why
    start=start_time,
    end=end_time,
    feed=DataFeed.IEX)
all_trades = data_client.get_stock_trades(request_params)
# print(type(all_trades)) # <class 'alpaca.data.models.trades.TradeSet'>
print()
print('%d ticker symbol(s):' % len(tickers))
for symbol in tickers:
    try:
        trades = all_trades.data[symbol]
        num_trades = len(trades)
    except KeyError:
        num_trades = 0
    print(f'    found {num_trades} trade(s) for ticker: {symbol}')
    if num_trades > 0:
        for i, trade in enumerate(trades):
            print(f'        trade {i + 1} of {len(trades)}:')
            print(f'            {trade.symbol}') # str
            print(f'            {trade.timestamp}') # datetime
            print(f'            {trade.exchange}') # Optional[Union[Exchange, str]]
            print(f'            {trade.price}') # float
            print(f'            {trade.size}') # float
            print(f'            {trade.id}') # int
            print(f'            {trade.conditions}') # Optional[List[str]]
            print(f'            {trade.tape}') # Optional[str]
            # source: file at:
            # /home/luke/rooms/money/exchanges_and_data_sources/exchanges/alpaca/alpaca-algo-trading-utils/src/virt_env/lib/python3.11/site-packages/alpaca/data/models/trades.py
print()





''' NOTE:

idk why but symbol_or_symbols needs to be a list of strings instead of just a string.
the docs say it can also be just a string but when setting it to for example "AAPL"
and running it during a time when theres no trades (ex: Saturday) i get this error:

    Traceback (most recent call last):
    File "/home/luke/rooms/money/exchanges_and_data_sources/exchanges/alpaca/alpaca-algo-trading-utils/src/get_all_trades.py", line 48, in <module>
        all_trades = data_client.get_stock_trades(request_params)
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    File "/home/luke/rooms/money/exchanges_and_data_sources/exchanges/alpaca/alpaca-algo-trading-utils/src/virt_env/lib/python3.11/site-packages/alpaca/data/historical/stock.py", line 154, in get_stock_trades
        return TradeSet(raw_trades)
            ^^^^^^^^^^^^^^^^^^^^
    File "/home/luke/rooms/money/exchanges_and_data_sources/exchanges/alpaca/alpaca-algo-trading-utils/src/virt_env/lib/python3.11/site-packages/alpaca/data/models/trades.py", line 71, in __init__
        parsed_trades[symbol] = [Trade(symbol, trade) for trade in trades]
                                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    File "/home/luke/rooms/money/exchanges_and_data_sources/exchanges/alpaca/alpaca-algo-trading-utils/src/virt_env/lib/python3.11/site-packages/alpaca/data/models/trades.py", line 71, in <listcomp>
        parsed_trades[symbol] = [Trade(symbol, trade) for trade in trades]
                                ^^^^^^^^^^^^^^^^^^^^
    File "/home/luke/rooms/money/exchanges_and_data_sources/exchanges/alpaca/alpaca-algo-trading-utils/src/virt_env/lib/python3.11/site-packages/alpaca/data/models/trades.py", line 48, in __init__
        for key, val in raw_data.items()
                        ^^^^^^^^^^^^^^
    AttributeError: 'NoneType' object has no attribute 'items'

but when making it a list of strings it returns:
data={}

closest thing i could find online is:
https://forum.alpaca.markets/t/is-it-expected-behavior-for-the-alpaca-historical-trades-api-to-throw-an-error-if-there-are-no-trades/11980/6

'''
