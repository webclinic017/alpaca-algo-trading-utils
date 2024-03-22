
# standard libraries
import os
import json
import sys
import time
import pathlib
REPO_PATH = str(pathlib.Path(__file__).resolve().parent.parent)
DATA_PATH = os.path.join(REPO_PATH, "data", "ticker_data")
# print('REPO_PATH', REPO_PATH)
# print('DATA_PATH', DATA_PATH)
# sys.exit()

# non-standard libraries
import numpy as np
import pandas as pd
pd.set_option('display.max_columns', 10)
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetAssetsRequest
from alpaca.trading.enums import AssetClass, AssetStatus


# API constants
LIVE_TRADING = False
with open('credentials.json') as f:
	creds = json.load(f)
ENDPOINT   = creds['live_trading' if LIVE_TRADING else 'paper_trading']['ENDPOINT']
API_KEY    = creds['live_trading' if LIVE_TRADING else 'paper_trading']['API_KEY_ID']
API_SECRET = creds['live_trading' if LIVE_TRADING else 'paper_trading']['SECRET_KEY']

trading_client = TradingClient(API_KEY, API_SECRET)

# https://alpaca.markets/sdks/python/api_reference/trading/assets.html#get-asset
symbol = "SOFI"
asset = trading_client.get_asset(symbol)

print(f'name:\t\t{asset.name}')
print(f'symbol:\t\t{asset.symbol}')
print(f'asset_class:\t{asset.asset_class}')
print(f'status:\t\t{asset.status}')
print(f'tradable:\t{asset.tradable}')
print(f'marginable:\t{asset.marginable}')
print(f'shortable:\t{asset.shortable}')
print(f'fractionable:\t{asset.fractionable}')
print(f'alpaca uuid:\t{asset.id}')




