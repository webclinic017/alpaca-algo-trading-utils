
'''

    description:
        use multiprocessing library to stream crypto price data.

    todo:
        use threading library instead of multiprocessing to share state between threads
            (see realtime_stock_spreads_from_async_streams.py file)

'''

import json, os, time
import pandas as pd
from datetime import datetime
from pytz import timezone
import multiprocessing as mp
from alpaca.data.live.crypto import CryptoDataStream
from alpaca.data.enums import CryptoFeed



# Alpaca API Constants
LIVE_TRADING = False
CREDENTIALS_FILEPATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "credentials.json")
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
EXCHANGE = 'iex'


INTERVAL = 3 # seconds, guy on Alpaca Slack said you can query every 3 seconds instead of every 5
TICKERS = ["BTC/USD"]#, "ETH/USD", "LTC/USD", "BCH/USD"]
TIMEZONE = 'UTC' # 'EST' # 'EDT'
''' TIMEZONE NOTE:
Eastern Standard Time (EST), when observing standard time (autumn/winter), are five hours behind Coordinated Universal Time (UTC−05:00). Eastern Daylight Time (EDT), when observing daylight saving time (spring/summer), are four hours behind Coordinated Universal Time (UTC−04:00). On the second Sunday in March, at 2:00 a.m. EST, clocks are advanced to 3:00 a.m. EDT leaving a one-hour gap. On the first Sunday in November, at 2:00 a.m. EDT, clocks are moved back to 1:00 a.m. EST, which results in one hour being duplicated.

source: https://en.wikipedia.org/wiki/Eastern_Time_Zone#:~:text=Eastern%20Standard%20Time%20(EST)%2C,UTC%E2%88%9204%3A00).
'''
DATE_FMT = '%Y-%m-%d %H:%M:%S %Z'

wss_client = CryptoDataStream(API_KEY, API_SECRET, feed=CryptoFeed.US)


quote_filepath = 'crypto_quotes.csv'
open(quote_filepath, 'w').close() # clear file
async def quote_data_handler(quote):

    # when quote data changes in any way for any of the listed tickers given to subscribe_quotes
    # this function will return ithat ticker's updated quote as an alpaca quote object
    # alpaca.data.models.quotes.Quote
    # https://alpaca.markets/sdks/python/api_reference/data/models.html#quote

    # when quote data changes in any way for any of the listed tickers given to subscribe_quotes
    # this function will return ithat ticker's updated quote as an alpaca quote object
    # alpaca.data.models.trades.Trade
    # https://alpaca.markets/sdks/python/api_reference/data/models.html#trade
    quote_received_time = datetime.now(timezone(TIMEZONE)).strftime(DATE_FMT)
    df = pd.DataFrame({
        'symbol'              : [quote.symbol], # ticker identifier for the security. TYPE: str
        'timestamp'           : [quote.timestamp], # time of submission of the quote. TYPE: datetime
        'ask_exchange'        : [quote.ask_exchange], # exchange of the quote ask. Defaults to None. TYPE: Optional[str, Exchange]
        'ask_price'           : [quote.ask_price], # asking price of the quote. TYPE: float
        'ask_size'            : [quote.ask_size], # size of the quote ask. TYPE: float
        'bid_exchange'        : [quote.bid_exchange], # exchange of the quote bid. Defaults to None. TYPE: Optional[str, Exchange]
        'bid_price'           : [quote.bid_price], # bid price of the quote. TYPE: float
        'bid_size'            : [quote.bid_size], # size of the quote bid. TYPE: float
        'conditions'          : [quote.conditions], # quote conditions. Defaults to None. TYPE: Optional[Union[List[str], str]]
        'tape'                : [quote.tape], # quote tape. Defaults to None. TYPE: Optional[str]
        'quote_recieved_time' : [quote_received_time],
    }, index=[0])

    # save row to CSV without reading the entire CSV
    if (not os.path.exists(quote_filepath)) or (os.path.getsize(quote_filepath) == 0):
        df.to_csv(quote_filepath, index=False)
    else:
        tmp_filepath = 'tmp.csv'
        df.to_csv(tmp_filepath, index=False, header=False)
        with open(tmp_filepath, 'r') as tmp_file:
            with open(quote_filepath, 'a') as quotes_file:
                new_row = tmp_file.read()
                quotes_file.write(new_row)
        os.remove(tmp_filepath)
    print(f'saved quote for {quote_received_time} to CSV')
def collect_data_in_separate_process():

    wss_client.subscribe_quotes(quote_data_handler, *TICKERS)
    # source to subscribe_quotes and subscribe_trades
    # https://alpaca.markets/sdks/python/api_reference/data/stock/live.html#stockdatastream

    # if data is not collected in a separate thread then
    # the script will be blocked after calling "wss_client.run()"
    # and "print('stream started')" will not run
    print('starting stream')
    wss_client.run()
    print('finished wss_client.run()')
    # NOTE: errors in this thread will print to console and will stop this thread
    # but will not the parent thread. Handle errors in this thread with a try/execpt block
    # source: convo with kapa.ai: https://alpaca-community.slack.com/archives/CEL9HCSN4/p1708615661484309

if __name__ == '__main__':
    print('creating process')
    process = mp.Process(target=collect_data_in_separate_process, daemon=True)
    print('process created')
    process.start()
    print('ran "process.start()"')
    # NOTE: process.start() must be in main function, can't be in script itself (with no indent, like "process = ...")
    # RuntimeError:
    #     An attempt has been made to start a new process before the
    #     current process has finished its bootstrapping phase.

    while True:
        time.sleep(50)

    # wss_client.unsubscribe_quotes()
    # wss_client.unsubscribe_trades()
    # wss_client.close()

    print('terminating process')
    process.terminate()
    print('process terminated')
    # source: https://stackoverflow.com/questions/32053618/how-to-to-terminate-process-using-pythons-multiprocessing

