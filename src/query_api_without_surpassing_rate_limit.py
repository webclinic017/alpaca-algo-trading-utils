import sys, time, json, requests
import pandas as pd
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


'''

    Description

        This script is an implementation of what Dan (Alpaca Developer Relations employee) described here:
        https://forum.alpaca.markets/t/executing-orders/12029/2

            "The simple way to ensure one doesn't exceed the rate limit is to wait 1/200 minutes (or .3 seconds) between calls. A more sophisticated method to maximize throughput is to look at the header information of the last API call." ... "The X-Ratelimit-Reset is the next time (in seconds epoch time) when the rate counter will reset. One way to use this information is to send orders as fast as you wish. If one gets a "429 rate limit exceeded" error, simply look at the header X-Ratelimit-Reset time. Pause until that time and then continue."

        I figured out how to read the headers in python and put it in a try/catch like Dan recommended. Unfortunately the alpaca-py library "does not directly expose these headers in its high-level API." - kapa.ai. I was looking in the [https://alpaca.markets/sdks/python/getting_started.html](docs) and couldn't find anything either, so I used the requests library to query the Alpaca URLs directly. It'd be nice if alpaca-py could do this, otherwise I'll have to not use it, or wait 1/200th a second between API calls.

    '''

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

# Global Variables and CONSTANTS
ratelimit_remaining = 200 # 1000
ratelimit_reset = 0
num_api_calls = 0
rate_limit_reached = False
QUERIES_TO_DO_AFTER_RATE_LIMIT_REACHED = 3
queries_done_after_rate_limit_reached = 0
TIMEZONE = 'US/Eastern' # 'US/Pacific' # 'UTC'
exchange = 'iex'
ticker_symbols = ['AAPL', 'JNJ', 'CVX']

def get_latest_quotes():

    global ratelimit_remaining, ratelimit_reset, num_api_calls
    print("\nquerying alpaca ... ")
    print(f'X-Ratelimit-Remaining = {ratelimit_remaining}')
    print(f'X-Ratelimit-Reset     = {ratelimit_reset}')
    print(f'current_time          = {int(time.time())}')
    print(f'number of API calls made so far: {num_api_calls}')
    # if ratelimit_remaining <= 0: # avoid rate limit error all together
    #     seconds_till_reset = ratelimit_reset - time.time()
    #     print(f'waiting {"%.2f" % seconds_till_reset} second(s) to query API again to not surpass API rate limit')

    # get quotes with requests library
    # https://docs.alpaca.markets/reference/stocklatestquotes
    symbols = '%2C'.join(ticker_symbols) # ex: AAPL%2CTSLA%2CMSFT
    url = f"https://data.alpaca.markets/v2/stocks/quotes/latest?symbols={symbols}&feed={exchange}"
    query_time = datetime.now().strftime('%Y-%m-%d %I:%M:%S %p %Z')
    try:
        response = requests.get(url, headers=HEADERS)
        num_api_calls += 1
        response.raise_for_status()
        ratelimit_reset = int(response.headers['X-Ratelimit-Reset'])
        ratelimit_remaining = int(response.headers['X-Ratelimit-Remaining'])
        print_quotes(response, query_time)

    # if rate limit is reached, wait until X-Ratelimit-Reset
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:
            print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! RATE LIMIT REACHED !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
            print(json.dumps(dict(e.response.headers), indent=4))
            print(json.dumps(json.loads(e.response.text), indent=4))
            global rate_limit_reached
            rate_limit_reached = True
            seconds_till_reset = ratelimit_reset - time.time()
            print(f'must wait {"%.2f" % seconds_till_reset} second(s) to query API again')
            time.sleep(seconds_till_reset)
        else:
            raise e

def print_quotes(response, query_time):
    print(f'quote {query_time}')
    quotes = json.loads(response.text)['quotes']
    # print(json.dumps(quotes, indent=4))
    df = pd.DataFrame(columns=[
        'ticker',
        'highestBid',
        'lowestAsk',
        'bidSize',
        'askSize',
        'exchange',
        'quote_query_time',
    ])
    for t, ticker in enumerate(ticker_symbols):
        df = pd.concat([
            df if not df.empty else None,
            pd.DataFrame({
                'ticker'           : ticker,
                'highestBid'       : quotes[ticker]['bp'],
                'lowestAsk'        : quotes[ticker]['ap'],
                'bidSize'          : quotes[ticker]['bs'],
                'askSize'          : quotes[ticker]['as'],
                'exchange'         : exchange,
                'quote_query_time' : query_time,
            }, index=[t + 1])
        ])
        # NOTE: in the quote response 'V' represents the IEX exchange
        # https://docs.alpaca.markets/reference/stocklatestquotes
    df_str = df.to_string(max_rows=df.shape[0])
    print(df_str)

print('bid/ask spread datafeed:')
while True:
    get_latest_quotes()
    if rate_limit_reached:
        if queries_done_after_rate_limit_reached >= QUERIES_TO_DO_AFTER_RATE_LIMIT_REACHED:
            print('\nrate limit test complete\n')
            sys.exit() # this line is for testing purposes only
        else:
            queries_done_after_rate_limit_reached += 1

