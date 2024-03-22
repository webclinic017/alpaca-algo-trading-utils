

"""

see file get_price_history.py for notes and sources on why this is depricated

"""

# standard libraries
import os
import json
import sys
import time

# non-standard libraries
import numpy as np
import pandas as pd
# pd.set_option('display.max_columns', 10)
import alpaca_trade_api as tradeapi
from alpaca_trade_api.rest import TimeFrame, URL

# API constants
LIVE_TRADING = False
with open('credentials.json') as f:
	creds = json.load(f)
ENDPOINT   = creds['live_trading' if LIVE_TRADING else 'paper_trading']['ENDPOINT']
API_KEY    = creds['live_trading' if LIVE_TRADING else 'paper_trading']['API_KEY_ID']
API_SECRET = creds['live_trading' if LIVE_TRADING else 'paper_trading']['SECRET_KEY']

alpaca = tradeapi.REST(API_KEY, API_SECRET, URL(ENDPOINT), 'v2')


# to do: get available values for the interval

tickers = ["AAPL", "MSFT"]
df = alpaca.get_bars(tickers, TimeFrame.Hour, "2021-06-08", "2021-06-08", adjustment='raw').df
print(df)
