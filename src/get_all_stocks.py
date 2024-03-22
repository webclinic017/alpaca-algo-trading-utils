
'''

	Description:
		script to get all US equities on Alpaca and save them to a file

	Sources:
		https://alpaca.markets/docs/api-references/trading-api/assets/#asset-entity
		https://alpaca.markets/docs/api-references/trading-api/assets/#get-assets
		https://github.com/alpacahq/alpaca-py

		docs for asset, position, order, ect. (a bunch of useful stuff)
		https://alpaca.markets/sdks/python/api_reference/trading/models.html


	'''

# standard libraries
import os
import json
import sys
import time
import requests
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

# search for stock assets
""" https://docs.alpaca.markets/docs/trading-api-1

	"Retrieves a list of assets that matches the search parameters. If there is not any search parameters provided, a list of all available assets will be returned. Search parameters for assets are defined by the GetAssetsRequest model, which allows filtering by AssetStatus, AssetClass, and AssetExchange."

	enums for AssetClass:
		AssetClass.CRYPTO
		AssetClass.US_EQUITY

	enums for AssetStatus:
		AssetStatus.ACTIVE
		AssetStatus.INACTIVE

	enums for AssetExchange:
		AssetExchange.CRYPTO
		AssetExchange.BATS
		AssetExchange.NASDAQ
		AssetExchange.NYSE
		AssetExchange.OTC
		AssetExchange.AMEX
		AssetExchange.ARCA

	"""
search_params = GetAssetsRequest(asset_class=AssetClass.US_EQUITY)

# https://alpaca.markets/sdks/python/api_reference/trading/assets.html
assets = trading_client.get_all_assets(search_params)

# print(type(assets)) # list
print(f"found {len(assets)} assets(s)") # found 31024 asset(s)
assets_to_save = []
for i, asset in enumerate(assets):
	# print(type(asset)) # alpaca.trading.models.Asset
	# https://alpaca.markets/sdks/python/api_reference/trading/models.html

	print(f'\nasset {i + 1} of {len(assets)}')
	# print(f'name:\t\t{asset.name}')
	# print(f'symbol:\t\t{asset.symbol}')
	# print(f'asset_class:\t{asset.asset_class}')
	# print(f'status:\t\t{asset.status}')
	# print(f'tradable:\t{asset.tradable}')
	# print(f'marginable:\t{asset.marginable}')
	# print(f'shortable:\t{asset.shortable}')
	# print(f'fractionable:\t{asset.fractionable}')
	# print(f'alpaca uuid:\t{asset.id}')

	if \
		asset.asset_class == AssetClass.US_EQUITY and \
		asset.status == AssetStatus.ACTIVE and \
		asset.tradable and \
		asset.marginable and \
		asset.shortable:# and \
		# asset.fractionable:

		assets_to_save.append(asset.symbol)

filename = "all_shortable_alpaca_stocks.csv"
# filename = "all_fractional_and_non_fractionable_alpaca_stocks.csv"
# filename = "all_alpaca_stocks.csv"
filepath = os.path.join(DATA_PATH, filename)
with open(filepath, 'w') as f:
	f.write('\n'.join(["ticker"] + assets_to_save))
	print(f'\nsaved {len(assets_to_save)} asset(s)')





######################### DEPRICATED #########################
# sources:
# https://forum.alpaca.markets/t/how-do-i-get-all-stocks-name-from-the-market-into-a-python-list/2070
# https://alpaca.markets/deprecated/docs/api-documentation/how-to/assets/
# https://github.com/alpacahq/alpaca-trade-api-python

# import alpaca_trade_api as tradeapi
# from alpaca_trade_api.rest import TimeFrame, URL
# alpaca = tradeapi.REST(API_KEY, API_SECRET, URL(ENDPOINT), 'v2')
# active_assets = alpaca.list_assets(status='active', asset_class='us_equity')
# for asset in active_assets:
# 	''' "asset" variable is a <class 'alpaca_trade_api.entity.Asset'>
# 		source:

# 		Example:
# 			{
# 			  "id": "904837e3-3b76-47ec-b432-046db621571b",
# 			  "class": "us_equity",
# 			  "exchange": "NASDAQ",
# 			  "symbol": "AAPL",
# 			  "status": "active",
# 			  "tradable": true,
# 			  "marginable": true,
# 			  "shortable": true,
# 			  "easy_to_borrow": true,
# 			  "fractionable": true
# 			} '''
# 	print(asset.symbol)
# 	print(asset.name)
# 	input()

