import json
from alpaca.trading.client import TradingClient

'''

	Description:
		script to get Alpaca trading account details

	Sources:
		https://alpaca.markets/sdks/python/api_reference/trading/account.html
		https://alpaca.markets/sdks/python/api_reference/trading/models.html#alpaca.trading.models.TradeAccount

	'''

# API constants
LIVE_TRADING = False
with open('credentials.json') as f:
	creds = json.load(f)
ENDPOINT   = creds['live_trading' if LIVE_TRADING else 'paper_trading']['ENDPOINT']
API_KEY    = creds['live_trading' if LIVE_TRADING else 'paper_trading']['API_KEY_ID']
API_SECRET = creds['live_trading' if LIVE_TRADING else 'paper_trading']['SECRET_KEY']
trading_client = TradingClient(API_KEY, API_SECRET, paper=not LIVE_TRADING)

account = trading_client.get_account()
print(account)
# print(type(account))
# outputs:
# <class 'alpaca.trading.models.TradeAccount'>
# for details on the fields this class has go here
# https://alpaca.markets/sdks/python/api_reference/trading/account.html
# https://alpaca.markets/sdks/python/api_reference/trading/models.html#alpaca.trading.models.TradeAccount

