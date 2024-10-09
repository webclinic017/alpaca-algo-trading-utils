
'''

    description
        script to get all level 1 quotes of a given stock in a given timeframe
        (copied from get_trade_history.py)

    sources
        https://alpaca.markets/sdks/python/api_reference/data/stock/historical.html#get-stock-quotes
        https://alpaca.markets/sdks/python/api_reference/data/stock/requests.html#alpaca.data.requests.StockQuotesRequest
        https://alpaca.markets/sdks/python/api_reference/data/enums.html#alpaca.data.enums.DataFeed
        https://alpaca.markets/sdks/python/api_reference/data/models.html#quoteset
        https://alpaca.markets/sdks/python/api_reference/data/models.html#quote

'''

import json
from datetime import datetime, timedelta
from alpaca.data.requests import StockQuotesRequest
from alpaca.data.enums import DataFeed
from alpaca.data import StockHistoricalDataClient


# Alpaca API Constants
LIVE_TRADING = False
CREDENTIALS_FILEPATH = \
    "/mnt/c/Users/luciu/rooms/money/trading/alpaca/alpaca-algo-trading-utils/src/credentials.json"
# "/home/luke/rooms/money/exchanges_and_data_sources/exchanges/alpaca/alpaca-algo-trading-utils/src/credentials.json"
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


feed = DataFeed.IEX
tickers = ["AAPL"]
end_time = datetime.now() - timedelta(days=4)
start_time = end_time - timedelta(days=1)
request_params = StockQuotesRequest(
    symbol_or_symbols=tickers, # must be a list, see NOTE at bottom of get_trade_history.py for why
    start=start_time,
    end=end_time,
    limit=20, # limit was added to speed up testing, this API call takes a long time, not sure why, probably a lot of data
    feed=feed)
all_quotes = data_client.get_stock_quotes(request_params)
# print(type(all_quotes)) # <class 'alpaca.data.models.quotes.QuoteSet'>
print()
print('%d ticker symbol(s):' % len(tickers))
for symbol in tickers:
    try:
        quotes = all_quotes.data[symbol]
        num_quotes = len(quotes)
    except KeyError:
        num_quotes = 0
    print(f'    found {num_quotes} quote(s) for ticker: {symbol}')
    if num_quotes > 0:
        for i, quote in enumerate(quotes):
            print(f'        quote {i + 1} of {len(quotes)}:')
            print(f'            {quote.symbol}') # str
            print(f'            {quote.timestamp}') # datetime
            print(f'            {quote.bid_price}') # float
            print(f'            {quote.bid_size}') # float
            print(f'            {quote.bid_exchange}') # Optional[Union[Exchange, str]]
            print(f'            {quote.ask_price}') # float
            print(f'            {quote.ask_size}') # float
            print(f'            {quote.ask_exchange}') # Optional[Union[Exchange, str]]
            print(f'            {quote.conditions}')
            print(f'            {quote.tape}')
            # source: file at:
            # /home/luke/rooms/money/exchanges_and_data_sources/exchanges/alpaca/alpaca-algo-trading-utils/src/virt_env/lib/python3.11/site-packages/alpaca/data/models/trades.py
print()
