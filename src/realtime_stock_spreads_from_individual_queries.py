
"""

description

    code that gets the real-time bid/ask spread of a list of tickers on 5 second intervals from yahoo finance
    runs indefinately and outputs data to screen
        
        free API has a max of 30 tickers, and 200 API calls per minute
        https://alpaca.markets/data

    according to Alpaca's free tier data source IEX, which has a 15 min lag.

	one guy uses Yahoo Finance for realtime quotes instead of Alpaca (even though it seems he's trading on Alpaca), and is getting decent results.
        "I use Alpaca for trade executions, but actually ping Yahoo Finance for live price data. I've found that YFinance seems more accurate and my orders execute somewhere around 30% more frequently."
            https://www.reddit.com/r/algotrading/comments/utshdp/rip_alpaca_data_feed_alternatives/

sources:

    https://docs.alpaca.markets/reference/stocklatesttradesingle

    https://alpaca.markets/sdks/python/api_reference/data/stock/historical.html
    https://alpaca.markets/sdks/python/api_reference/data/stock/requests.html
    https://alpaca.markets/sdks/python/api_reference/data/models.html

    https://docs.alpaca.markets/docs/market-data-faq
        "Our free market data offering includes live data only from the IEX exchange:
        wss://stream.data.alpaca.markets/v2/iex

        The Algo Trader Plus subscription on the other hand offers SIP data:
        wss://stream.data.alpaca.markets/v2/sip"

    https://medium.com/automation-generation/exploring-the-differences-between-u-s-stock-market-data-feeds-3da26946cbd6
        
        SIP Exchange Proprietary Market Data Feeds

            While the SIP or another consolidated stream is entirely sufficient for most investors and traders as their source for stock quotes and trades, most exchanges sell their own proprietary data feeds, which provide additional quote and trade information. These proprietary feeds are typically used by professional day traders, who visually interpret the full order book for additional information. The feeds are also used in a non-display format by for high-frequency traders and market makers, who may incorporate all order book and trade information into their trading strategies and may benefit from reacting as quickly as possible to this information. Although this sounds concerning, there’s nothing nefarious here, as these are all public feeds that any individual or company can purchase.
        
        IEX Market Data

            One proprietary exchange feed worth highlighting is IEX’s market data feed. Unlike other exchanges, IEX currently provides its market data for free. There’s no catch (at least for now), as IEX wants to promote activity on its exchange and has stated that “legacy stock exchanges obstruct transparency and create an uneven playing field by overcharging for market data on orders they did not create.” IEX’s market data includes both top of book and last sale information as well as aggregated deep book information (although not a full stream of every event, which IEX does not provide). You can read more about IEX’s market data here, but the important point to remember is that these feeds only include orders and executions on the IEX order book.

            Considering that IEX’s market share based on total consolidated volume is around 2.5 to 3% as of December 2018, the IEX trade and quote feeds may be missing out on significant information contained in the other venues’ trades and quotes. Nevertheless, IEX data is a good starting point and is easy to access and use for paper trading with Alpaca’s API.


    https://iexcloud.io/documentation/using-core-data/real-time-delayed-and-intraday-stock-prices.html
        Real-time and 15 Minute Delayed Prices

            During market trading hours, IEX Cloud provides both real-time stock quotes and 15 minute delayed stock quotes for U.S. stocks and ETFs. You can access this data via the Stock Quote endpoint and Intraday Equity Prices endpoint.

            Real-time quotes (or prices) are based on all trades that occur on the Investors Exchange (IEX). 15 minute delayed stock prices reflect activity from all U.S. exchanges, and is provided by the Securities Information Processor / Consolidate Tape Association (SIP).

            While real-time prices for Nasdaq-listed stocks are available to all users, 15 minute delayed price data for Nasdaq-listed securities requires UTP authorization.

            Note that real-time prices available via the IEX Cloud Data are different from real-time prices available via direct connection from IEX. During market hours, IEX Cloud Data prices available from IEX Exchange are real-time. Prices of most stocks are otherwise typically delayed up to 15 minutes–prices of some stocks (e.g., stocks traded in low volume) may be delayed longer.


"""


from datetime import datetime, timedelta
from pytz import timezone
import os, sys, time
import pandas as pd

LOG_UTIL_PATH = "/home/luke/rooms/tech/software/projects/python-common-utils/utils/logging/src"
sys.path.append(LOG_UTIL_PATH)
import logging_utils
log = logging_utils.Log()

import json
import requests
from alpaca.data import StockHistoricalDataClient
from alpaca.data.requests import StockLatestQuoteRequest, StockLatestTradeRequest
from alpaca.data.enums import DataFeed
from timeout_decorator import timeout, TimeoutError

INTERVAL = 5 # measured in seconds
DATE_FMT = '%Y-%m-%d %I:%M:%S %p %Z'


# API constants
LIVE_TRADING = False
with open('credentials.json') as f:
	creds = json.load(f)
ENDPOINT   = creds['live_trading' if LIVE_TRADING else 'paper_trading']['ENDPOINT']
API_KEY    = creds['live_trading' if LIVE_TRADING else 'paper_trading']['API_KEY_ID']
API_SECRET = creds['live_trading' if LIVE_TRADING else 'paper_trading']['SECRET_KEY']
HEADERS = {
    "accept": "application/json",
    "APCA-API-KEY-ID": API_KEY,
    "APCA-API-SECRET-KEY": API_SECRET
}

# Global Variables
data_client = StockHistoricalDataClient(API_KEY, API_SECRET)
exchange = 'iex'


log.print("enter list of tickers to get realtime price data of (separated by spaces)", i=0, ns=True)
ticker_symbols = None
while ticker_symbols == None:
    user_input = input()
    try:
        ticker_symbols = user_input.upper()#.split(' ')
        # todo: verify valid tickers on API
    except:
        log.print("invalid ticker list", i=1)
        ticker_symbols = None


def datafeed(now):
    log.print_same_line("querying alpaca ...          ", i=1, ns=True)

    quotes_df = get_latest_quotes()
    trades_df = get_latest_trades()
    df = pd.merge(quotes_df, trades_df, on='ticker')\
        .sort_values(by=['ticker'])\
        .reset_index(drop=True)

    # time.sleep(1) # for testing purposes only
    log.print_same_line(now.strftime('%Y-%m-%d %I:%M:%S %p %Z'), i=1, ns=True)
    df_str = df.to_string(max_rows=df.shape[0])
    log.print(df_str, i=2)
    return df

def get_latest_quotes():
    # note: using request library to use timeout to avoid error described in get_latest_trades()
    quotes_df = get_latest_quotes_via_requests_library()
    try:
        quotes_df = get_latest_quotes_via_alpaca_library()
    except TimeoutError as e:
        log.print('failed to get quote, timed out')
        log.print(e)
    return quotes_df
def get_latest_quotes_via_requests_library():

    # get quotes with requests library
    # https://docs.alpaca.markets/reference/stocklatestquotes
    # NOTE: 'V' is the IEX exchange
    # https://alpaca.markets/sdks/python/api_reference/data/enums.html#alpaca.data.enums.DataFeed
    df = pd.DataFrame(columns=[
        'ticker',
        'highestBid',
        'lowestAsk',
        'bidSize',
        'askSize',
        'exchange',
        'quote_query_time',
    ])
    symbols = '%2C'.join(ticker_symbols.split(' ')) # ex: AAPL%2CTSLA%2CMSFT
    url = f"https://data.alpaca.markets/v2/stocks/quotes/latest?symbols={symbols}&feed={exchange}"
    quotes_time = datetime.now().strftime(DATE_FMT)
    response = requests.get(url, headers=HEADERS)
    quotes = json.loads(response.text)['quotes']
    # print(json.dumps(quotes, indent=4))
    for t, ticker in enumerate(ticker_symbols.split(' ')):
        df = pd.concat([
            df if not df.empty else None,
            pd.DataFrame({
                'ticker'           : ticker,
                'highestBid'       : quotes[ticker]['bp'],
                'lowestAsk'        : quotes[ticker]['ap'],
                'bidSize'          : quotes[ticker]['bs'],
                'askSize'          : quotes[ticker]['as'],
                'exchange'         : exchange,
                'quote_query_time' : quotes_time,
            }, index=[t + 1])
        ])
    return df

@timeout(5)
def get_latest_quotes_via_alpaca_library():

    # get quotes w/ function get_stock_latest_quote from alpaca-py library
    # from testing, it seems to get the exact same data as the quotes
    # https://alpaca.markets/sdks/python/api_reference/data/stock/historical.html
    df = pd.DataFrame(columns=[
        'ticker',
        'highestBid',
        'lowestAsk',
        'bidSize',
        'askSize',
        'exchange',
        'quote_query_time',
    ])
    request = StockLatestQuoteRequest(
        symbol_or_symbols=ticker_symbols.split(' '),
        feed=DataFeed.IEX,
    )
    quotes_time = datetime.now().strftime(DATE_FMT)
    quotes = data_client.get_stock_latest_quote(request)
    for t, (ticker, quote) in enumerate(quotes.items()):
        df = pd.concat([
            df if not df.empty else None,
            pd.DataFrame({
                'ticker'           : ticker,
                'highestBid'       : quote.bid_price,
                'lowestAsk'        : quote.ask_price,
                'bidSize'          : quote.bid_size,
                'askSize'          : quote.ask_size,
                'exchange'         : exchange,
                'quote_query_time' : quotes_time,
            }, index=[t + 1])
        ])
    return df

def get_latest_trades():
    # note: using request library to use timeout to avoid error:
    ''' error:
            Traceback (most recent call last):
                File "/home/luke/rooms/money/stocks/spread-trade-strategies/strategies/strat7/realtime/virt_env/lib/python3.11/site-packages/urllib3/connectionpool.py", line 793, in urlopen
                    response = self._make_request(
                            ^^^^^^^^^^^^^^^^^^^
                File "/home/luke/rooms/money/stocks/spread-trade-strategies/strategies/strat7/realtime/virt_env/lib/python3.11/site-packages/urllib3/connectionpool.py", line 537, in _make_request
                    response = conn.getresponse()
                            ^^^^^^^^^^^^^^^^^^
                File "/home/luke/rooms/money/stocks/spread-trade-strategies/strategies/strat7/realtime/virt_env/lib/python3.11/site-packages/urllib3/connection.py", line 466, in getresponse
                    httplib_response = super().getresponse()
                                    ^^^^^^^^^^^^^^^^^^^^^
                File "/usr/lib/python3.11/http/client.py", line 1378, in getresponse
                    response.begin()
                File "/usr/lib/python3.11/http/client.py", line 318, in begin
                    version, status, reason = self._read_status()
                                            ^^^^^^^^^^^^^^^^^^^
                File "/usr/lib/python3.11/http/client.py", line 287, in _read_status
                    raise RemoteDisconnected("Remote end closed connection without"
            http.client.RemoteDisconnected: Remote end closed connection without response

            During handling of the above exception, another exception occurred:

            Traceback (most recent call last):
                File "/home/luke/rooms/money/stocks/spread-trade-strategies/strategies/strat7/realtime/virt_env/lib/python3.11/site-packages/requests/adapters.py", line 486, in send
                    resp = conn.urlopen(
                        ^^^^^^^^^^^^^
                File "/home/luke/rooms/money/stocks/spread-trade-strategies/strategies/strat7/realtime/virt_env/lib/python3.11/site-packages/urllib3/connectionpool.py", line 847, in urlopen
                    retries = retries.increment(
                            ^^^^^^^^^^^^^^^^^^
                File "/home/luke/rooms/money/stocks/spread-trade-strategies/strategies/strat7/realtime/virt_env/lib/python3.11/site-packages/urllib3/util/retry.py", line 470, in increment
                    raise reraise(type(error), error, _stacktrace)
                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                File "/home/luke/rooms/money/stocks/spread-trade-strategies/strategies/strat7/realtime/virt_env/lib/python3.11/site-packages/urllib3/util/util.py", line 38, in reraise
                    raise value.with_traceback(tb)
                File "/home/luke/rooms/money/stocks/spread-trade-strategies/strategies/strat7/realtime/virt_env/lib/python3.11/site-packages/urllib3/connectionpool.py", line 793, in urlopen
                    response = self._make_request(
                            ^^^^^^^^^^^^^^^^^^^
                File "/home/luke/rooms/money/stocks/spread-trade-strategies/strategies/strat7/realtime/virt_env/lib/python3.11/site-packages/urllib3/connectionpool.py", line 537, in _make_request
                    response = conn.getresponse()
                            ^^^^^^^^^^^^^^^^^^
                File "/home/luke/rooms/money/stocks/spread-trade-strategies/strategies/strat7/realtime/virt_env/lib/python3.11/site-packages/urllib3/connection.py", line 466, in getresponse
                    httplib_response = super().getresponse()
                                    ^^^^^^^^^^^^^^^^^^^^^
                File "/usr/lib/python3.11/http/client.py", line 1378, in getresponse
                    response.begin()
                File "/usr/lib/python3.11/http/client.py", line 318, in begin
                    version, status, reason = self._read_status()
                                            ^^^^^^^^^^^^^^^^^^^
                File "/usr/lib/python3.11/http/client.py", line 287, in _read_status
                    raise RemoteDisconnected("Remote end closed connection without"
            urllib3.exceptions.ProtocolError: ('Connection aborted.', RemoteDisconnected('Remote end closed connection without response'))

            During handling of the above exception, another exception occurred:

            Traceback (most recent call last):
                File "/home/luke/rooms/money/stocks/spread-trade-strategies/strategies/strat7/realtime/tests/verify_data_is_realtime/driver.py", line 392, in <module>
                    collect_price_data(now, i=1)
                File "/home/luke/rooms/money/stocks/spread-trade-strategies/strategies/strat7/realtime/tests/verify_data_is_realtime/driver.py", line 89, in collect_price_data
                    alpaca_price_datafeed(i=i+1)
                File "/home/luke/rooms/money/stocks/spread-trade-strategies/strategies/strat7/realtime/tests/verify_data_is_realtime/driver.py", line 129, in alpaca_price_datafeed
                    quotes_df = get_latest_quotes()
                                ^^^^^^^^^^^^^^^^^^^
                File "/home/luke/rooms/money/stocks/spread-trade-strategies/strategies/strat7/realtime/tests/verify_data_is_realtime/driver.py", line 146, in get_latest_quotes
                    quotes_df = get_latest_quotes_via_alpaca_library()
                                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                File "/home/luke/rooms/money/stocks/spread-trade-strategies/strategies/strat7/realtime/tests/verify_data_is_realtime/driver.py", line 200, in get_latest_quotes_via_alpaca_library
                    quotes = data_client.get_stock_latest_quote(request)
                            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                File "/home/luke/rooms/money/stocks/spread-trade-strategies/strategies/strat7/realtime/virt_env/lib/python3.11/site-packages/alpaca/data/historical/stock.py", line 196, in get_stock_latest_quote
                    raw_latest_quotes = self._data_get(
                                        ^^^^^^^^^^^^^^^
                File "/home/luke/rooms/money/stocks/spread-trade-strategies/strategies/strat7/realtime/virt_env/lib/python3.11/site-packages/alpaca/data/historical/stock.py", line 338, in _data_get
                    response = self.get(path=path, data=params, api_version=api_version)
                            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                File "/home/luke/rooms/money/stocks/spread-trade-strategies/strategies/strat7/realtime/virt_env/lib/python3.11/site-packages/alpaca/common/rest.py", line 221, in get
                    return self._request("GET", path, data, **kwargs)
                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                File "/home/luke/rooms/money/stocks/spread-trade-strategies/strategies/strat7/realtime/virt_env/lib/python3.11/site-packages/alpaca/common/rest.py", line 129, in _request
                    return self._one_request(method, url, opts, retry)
                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                File "/home/luke/rooms/money/stocks/spread-trade-strategies/strategies/strat7/realtime/virt_env/lib/python3.11/site-packages/alpaca/common/rest.py", line 193, in _one_request
                    response = self._session.request(method, url, **opts)
                            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                File "/home/luke/rooms/money/stocks/spread-trade-strategies/strategies/strat7/realtime/virt_env/lib/python3.11/site-packages/requests/sessions.py", line 589, in request
                    resp = self.send(prep, **send_kwargs)
                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                File "/home/luke/rooms/money/stocks/spread-trade-strategies/strategies/strat7/realtime/virt_env/lib/python3.11/site-packages/requests/sessions.py", line 703, in send
                    r = adapter.send(request, **kwargs)
                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                File "/home/luke/rooms/money/stocks/spread-trade-strategies/strategies/strat7/realtime/virt_env/lib/python3.11/site-packages/requests/adapters.py", line 501, in send
                    raise ConnectionError(err, request=request)
            requests.exceptions.ConnectionError: ('Connection aborted.', RemoteDisconnected('Remote end closed connection without response'))
    '''
    # this error occured on rare occations when querying via the alpaca library in the
    # strat7 verify_data_is_realtime/driver.py test
    # see this slack thread for further details
    # https://alpaca-community.slack.com/archives/CEL9HCSN4/p1708531519248269
    trades_df = get_latest_trades_via_requests_library()
    # trades_df = get_latest_trades_via_alpaca_library()
    return trades_df
def get_latest_trades_via_requests_library():

    # get latest trades with requests library
    # https://docs.alpaca.markets/reference/stocklatesttrades
    df = pd.DataFrame(columns=[
        'ticker',
        'lastTradePrice',
        'lastTradeTime',
        'lastTradeID',
    ])
    symbols = '%2C'.join(ticker_symbols.split(' ')) # ex: AAPL%2CTSLA%2CMSFT
    url = f"https://data.alpaca.markets/v2/stocks/trades/latest?symbols={symbols}&feed={exchange}"
    response = requests.get(url, headers=HEADERS)
    latest_trades = json.loads(response.text)['trades']
    # print(json.dumps(latest_trades, indent=4))
    for t, (ticker, latest_trade) in enumerate(latest_trades.items()):
        df = pd.concat([
            df if not df.empty else None,
            pd.DataFrame({
                'ticker'         : ticker,
                'lastTradePrice' : latest_trade['p'],
                'lastTradeTime'  : latest_trade['t'],
                'lastTradeID'    : latest_trade['i'],
            }, index=[t + 1])
        ])
    return df
def get_latest_trades_via_alpaca_library():

    # get latest trades with alpaca library
    # https://docs.alpaca.markets/reference/stocklatesttrades
    df = pd.DataFrame(columns=[
        'ticker',
        'lastTradePrice',
        'lastTradeTime',
        'lastTradeID',
    ])
    request = StockLatestTradeRequest(
        symbol_or_symbols=ticker_symbols.split(' '),
        feed=DataFeed.IEX,
    )
    latest_trades = data_client.get_stock_latest_trade(request)
    for t, (ticker, latest_trade) in enumerate(latest_trades.items()):
        df = pd.concat([
            df if not df.empty else None,
            pd.DataFrame({
                'ticker'         : ticker,
                'lastTradePrice' : latest_trade.price,
                'lastTradeTime'  : latest_trade.timestamp,
                'lastTradeID'    : latest_trade.id,
            }, index=[t + 1])
        ])
    return df



log.print('bid/ask spread datafeed:', i=0, ns=True)
last_timestep = datetime.now(timezone('EST'))
first = True
data_str = ""
old_update_message = None
while True:
    now = datetime.now(timezone('EST'))
    time_since_last_update = now - last_timestep
    time_until_next_update = INTERVAL - time_since_last_update.total_seconds()
    if first or time_until_next_update <= 0:
        first = False
        datafeed(now)
        last_timestep = now
    new_update_message = 'next update in %d seconds        ' % (time_until_next_update + 1)
    if old_update_message == None or new_update_message != old_update_message:
        log.print_same_line(new_update_message, i=1, ns=True)
        old_update_message = new_update_message

