
'''

	Description:
		pipeline to get price history of US equities on Alpaca
        on specified
            start_date
            end_date
            interval

	Sources:
        https://docs.alpaca.markets/reference/stockbars
		https://docs.alpaca.markets/docs/market-data-faq

	'''

# standard libraries
import os
import json
import sys
import time
import requests
import pathlib
REPO_PATH = str(pathlib.Path(__file__).resolve().parent.parent)
DATA_PATH = os.path.join(REPO_PATH, "data", "price_data")
# print('REPO_PATH', REPO_PATH)
# print('DATA_PATH', DATA_PATH)
# sys.exit()

# non-standard libraries
from datetime import datetime, timedelta
import pandas as pd
pd.set_option('display.max_columns', 10)
pd.set_option('display.width', 1000)
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetAssetsRequest
from alpaca.trading.enums import AssetClass


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

trading_client = TradingClient(API_KEY, API_SECRET)


input_filename = "all_shortable_alpaca_stocks.csv"
# filename = "all_alpaca_stocks.csv"
# filename = "all_fractional_and_non_fractionable_alpaca_stocks.csv"
df0 = pd.read_csv(os.path.join(REPO_PATH, "data", "ticker_data", input_filename))
df0.sort_values(by=['ticker'], inplace=True)
# print(df0)

now = datetime.now()
end_date = now.strftime('%Y-%m-%d')
start_date = (now - timedelta(days=365)).strftime('%Y-%m-%d') # one year ago
# end_date = ... if end_date is excluded, the current time is assumed
interval = '1Day' # see here for valid intervals: https://docs.alpaca.markets/reference/stockbars
exchange = 'iex' # 'sip'
def get_price_history(ticker):
    url = f"https://data.alpaca.markets/v2/stocks/bars?symbols={ticker}&timeframe={interval}&start={start_date}&end={end_date}&limit=1000&adjustment=all&feed={exchange}&sort=asc"
    response = requests.get(url, headers=HEADERS)
    # NOTE: if you request more than 1000 data points (in total, not per symbol), you'll have to concatinate paginated responses
    data = json.loads(response.text)
    # print(json.dumps(data, indent=4))
    if "bars" not in data.keys() or ticker not in data["bars"].keys():
        print(f"no price data found for {ticker}")
        return None
    df = pd.DataFrame(data['bars'][ticker])
    # i asked in alpaca's slack what "n" stands for and their AI said
    # "number of trades that occurred during the bar's time period"
    # and it said "vw" was "volume-weighted average price of the stock during the bar's time period."
    # https://alpaca-community.slack.com/archives/CEL9HCSN4/p1704602713177009
    df.rename(columns={
         'c' : "close",
         'h' : "high",
         'l' : "low",
         'n' : "number_of_trades",
         'o' : "open",
         't' : "time",
         'v' : "volume",
         'vw' : "volumn_weighted_average_price"
    }, inplace=True)
    reordered_columns = [
         "time",
         "open",
         "high",
         "low",
         "close",
         "number_of_trades",
         "volume",
         "volumn_weighted_average_price"
    ]
    df = df[reordered_columns]
    return df



if __name__ == '__main__':

    output_dir_name = f"price_data_for_1_year_on_daily_intervals_from_{start_date}_to_{end_date}_of_shortable_alpaca_stocks"
    output_dir_path = os.path.join(DATA_PATH, output_dir_name)
    if not os.path.exists(output_dir_path):
        os.makedirs(output_dir_path)

    for i, row in df0.iterrows():
        if i < 1975: continue # for testing purposes only, also this script sometimes gets stuck
        ticker = row['ticker']
        print(f"ticker {i + 1} of {df0.shape[0]}: {ticker}")
        df = get_price_history(ticker)
        if isinstance(df, pd.DataFrame):
            df.to_csv(os.path.join(output_dir_path, f"{ticker}.csv"), index=False)
        time.sleep(1)

