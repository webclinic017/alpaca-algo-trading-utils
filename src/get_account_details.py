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
# print(type(account))
# outputs:
# <class 'alpaca.trading.models.TradeAccount'>
# for details on the fields this class has go here
# https://alpaca.markets/sdks/python/api_reference/trading/account.html
# https://alpaca.markets/sdks/python/api_reference/trading/models.html#alpaca.trading.models.TradeAccount

print('\nAccount:\n')
print('account.id\t\t\t\t', account.id) # The account ID
print('account.account_number\t\t\t', account.account_number) # The account number
print('account.status\t\t\t\t', account.status) # The current status of the account
print('account.crypto_status\t\t\t', account.crypto_status) # The status of the account in regards to trading crypto. Only present if crypto trading is enabled for your brokerage account.
print('account.currency\t\t\t', account.currency) # Currently will always be the value “USD”.
print('account.buying_power\t\t\t', account.buying_power) # Current available cash buying power. If multiplier = 2 then buying_power = max(equity-initial_margin(0) * 2). If multiplier = 1 then buying_power = cash.
print('account.regt_buying_power\t\t', account.regt_buying_power) # User’s buying power under Regulation T (excess equity - (equity - margin value) - * margin multiplier)
print('account.daytrading_buying_power\t\t', account.daytrading_buying_power) # The buying power for day trades for the account
print('account.non_marginable_buying_power\t', account.non_marginable_buying_power) # The non marginable buying power for the account
print('account.cash\t\t\t\t', account.cash) # Cash balance in the account
print('account.accrued_fees\t\t\t', account.accrued_fees) # Fees accrued in this account
print('account.pending_transfer_out\t\t', account.pending_transfer_out) # Cash pending transfer out of this account
print('account.pending_transfer_in\t\t', account.pending_transfer_in) # Cash pending transfer into this account
print('account.portfolio_value\t\t\t', account.portfolio_value) # Total value of cash + holding positions. (This field is deprecated. It is equivalent to the equity field.)
print('account.pattern_day_trader\t\t', account.pattern_day_trader) # Whether the account is flagged as pattern day trader or not.
print('account.trading_blocked\t\t\t', account.trading_blocked) # If true, the account is not allowed to place orders.
print('account.transfers_blocked\t\t', account.transfers_blocked) # If true, the account is not allowed to request money transfers.
print('account.account_blocked\t\t\t', account.account_blocked) # If true, the account activity by user is prohibited.
print('account.created_at\t\t\t', account.created_at) # Timestamp this account was created at
print('account.trade_suspended_by_user\t\t', account.trade_suspended_by_user) # If true, the account is not allowed to place orders.
print('account.multiplier\t\t\t', account.multiplier) # Multiplier value for this account.
print('account.shorting_enabled\t\t', account.shorting_enabled) # Flag to denote whether or not the account is permitted to short
print('account.equity\t\t\t\t', account.equity) # This value is cash + long_market_value + short_market_value. This value isn’t calculated in the SDK it is computed on the server and we return the raw value here.
print('account.last_equity\t\t\t', account.last_equity) # Equity as of previous trading day at 16:00:00 ET
print('account.long_market_value\t\t', account.long_market_value) # Real-time MtM value of all long positions held in the account
print('account.short_market_value\t\t', account.short_market_value) # Real-time MtM value of all short positions held in the account
print('account.initial_margin\t\t\t', account.initial_margin) # Reg T initial margin requirement
print('account.maintenance_margin\t\t', account.maintenance_margin) # Maintenance margin requirement
print('account.last_maintenance_margin\t\t', account.last_maintenance_margin) # Maintenance margin requirement on the previous trading day
print('account.sma\t\t\t\t', account.sma) # Value of Special Memorandum Account (will be used at a later date to provide additional buying_power)
print('account.daytrade_count\t\t\t', account.daytrade_count) # The current number of daytrades that have been made in the last 5 trading days (inclusive of today)
print('account.options_buying_power\t\t', account.options_buying_power) # Your buying power for options trading
print('account.options_approved_level\t\t', account.options_approved_level) # The options trading level that was approved for this account. 0=disabled, 1=Covered Call/Cash-Secured Put, 2=Long Call/Put.
print('account.options_trading_level\t\t', account.options_trading_level) # The effective options trading level of the account. This is the minimum between account options_approved_level and account configurations max_options_trading_level. 0=disabled, 1=Covered Call/Cash-Secured Put, 2=Long
print('\nsource:')
print('https://alpaca.markets/sdks/python/api_reference/trading/models.html#alpaca.trading.models.TradeAccount\n')
