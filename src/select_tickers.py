
# standard libraries
import os
import json
import sys
import time
import random
from datetime import datetime, date, timedelta, timezone
from dateutil.tz import tzlocal

# non-standard libraries
import numpy as np
import pandas as pd
# pd.set_option('display.max_columns', 10)
import matplotlib.pyplot as plt
import alpaca_trade_api as tradeapi
from alpaca_trade_api.rest import TimeFrame, TimeFrameUnit, URL

# repo path constants
import pathlib
REPO_PATH = str(pathlib.Path(__file__).resolve().parent.parent.parent.parent)
DATA_PATH = os.path.join(REPO_PATH, 'data', 'alpaca')
# print('REPO_PATH\t%s' % REPO_PATH)
# print('DATA_PATH\t%s' % DATA_PATH)
# sys.exit()

# API constants
LIVE_TRADING = False
with open(os.path.join(DATA_PATH, 'credentials.json')) as f:
	creds = json.load(f)
ENDPOINT   = creds['live_trading' if LIVE_TRADING else 'paper_trading']['ENDPOINT']
API_KEY    = creds['live_trading' if LIVE_TRADING else 'paper_trading']['API_KEY_ID']
API_SECRET = creds['live_trading' if LIVE_TRADING else 'paper_trading']['SECRET_KEY']

alpaca = tradeapi.REST(API_KEY, API_SECRET, URL(ENDPOINT), 'v2')
# tickers = ["AAPL", "MSFT"]
# df = alpaca.get_bars(tickers, TimeFrame.Hour, "2021-06-08", "2021-06-08", adjustment='raw').df
# print(df)

# returns list of tickers
def get_all_available_alpaca_stocks():
	stock_category = 'all'
	active_assets = alpaca.list_assets(
		status='active', asset_class='us_equity')
	return [asset.symbol for asset in active_assets if \
		asset.tradable and \
		asset.marginable and \
		asset.shortable and \
		asset.easy_to_borrow and \
		asset.fractionable], stock_category
def get_all_sec_stocks_on_alpaca():
    filepath = os.path.join(DATA_PATH, 'ticker_data', 'all_sec_stocks_on_alpaca.csv')
    stock_category = 'all'
    try:
        all_sec_stocks_on_alpaca = pd.read_csv(filepath, index_col=0)['ticker'].tolist()
    except:
        available_tickers, _ = get_all_available_alpaca_stocks()
        sec_stocks_filepath = os.path.join(DATA_PATH, 'ticker_data', 'all_SEC_tickers.csv')
        df = pd.read_csv(sec_stocks_filepath, index_col=0)
        sec_stocks = df['ticker'].tolist()
        stocks = set(available_tickers).intersection(set(sec_stocks))
        all_sec_stocks_on_alpaca = df[df['ticker'].isin(stocks)]
        all_sec_stocks_on_alpaca.to_csv(filepath)
    return all_sec_stocks_on_alpaca, stock_category

def sort_stocks_by_average_volume(stocks, plot=False, exclude_sp500_stocks=False):
    filepath = os.path.join(DATA_PATH, 'ticker_data',
        'stocks_on_alpaca_sorted_by_average_volume.csv')
    try:
        sorted_stocks_df = pd.read_csv(filepath, index_col=0)
        sorted_stocks = sorted_stocks_df['ticker'].tolist()
    except:
        average_volumes = {}
        end_date = datetime.now(tz=timezone.utc)#tz=tzlocal())
        # end_date = datetime(2022, 5, 30, tzinfo=timezone.utc) # they only have data for the past few months :(
        # end_date_str = datetime.strftime(current_time, '%Y-%m-%d %H:%M:%S %Z')
        start_date = end_date - timedelta(days=31)
        interval = 'minute'
        for i, ticker in enumerate(stocks):
            raw_price_history = get_price_history(
                ticker,
                start_date,
                end_date,
                interval)
            input()
            volumes = [candle['volume'] for candle in raw_price_history['candles']]
            # print('volumes', volumes)
            # input()
            if len(volumes) < 100:
                print('ticker %d of %d: %s\tskipping b/c len(volumes) of %d < 100' % (
                    i+1, len(stocks), ticker, len(volumes)))
            else:
                prices = [candle['close'] for candle in raw_price_history['candles']]
                # print('prices', prices)
                # input()
                average_price = round(float(sum(prices)) / len(prices), 2)
                if average_price < 1.00:
                    print('ticker %d of %d: %s\tskipping b/c average_price of $%.2f < $1.00' % (
                        i+1, len(stocks), ticker, average_price))
                else:
                    average_volumes[ticker] = round(float(sum(volumes)) / len(volumes), 2)
                    print('ticker %d of %d: %s\taverage %s volume = $%.2f' % (
                        i+1, len(stocks), ticker, interval, average_volumes[ticker]))
            time.sleep(1)
        sorted_average_volumes = sorted(average_volumes.items(), key=lambda x : x[1], reverse=True)
        sorted_stocks = [ticker for ticker, volume in sorted_average_volumes]
        if plot: # plot used to verify sufficient volume in non sp500 stocks
            bars = [volume for ticker, volume in sorted_average_volumes]
            sp500_stocks = pd.read_csv('sp500_tickers.csv')['ticker'].tolist()
            colors = ['red' if ticker in sp500_stocks else 'blue' for ticker in sorted_stocks]
            fig, ax = plt.subplots(1, 1)
            mng = plt.get_current_fig_manager()
            mng.window.showMaximized()
            window_title = 'sorted average %s volume' % interval
            mng.set_window_title(window_title)
            ax.bar(sorted_stocks, bars, color=colors)#, width=0.4)
            def format_coord(x, y):
                if 0 <= x < len(sorted_stocks):
                    ticker = sorted_stocks[int(x)]
                    volume = bars[int(x)]
                    return '%s average %s volume = $%.2f' % (ticker, interval, volume)
                else:
                    return ''
            ax.format_coord = format_coord
            plt.show()
        if exclude_sp500_stocks:
            sp500_stocks = pd.read_csv('sp500_tickers.csv')['ticker'].tolist()
            sorted_stocks = [ticker for ticker in sorted_stocks if ticker not in sp500_stocks]
            print('\nnon-sp500 tickers sorted descending volume:')
            for i, ticker in enumerate(sorted_stocks):
                print('    ticker %d of %d\t%s average %s volume = $%.2f' % (
                    i+1, len(sorted_stocks), ticker, interval, average_volumes[ticker]))
        sorted_stocks_df = pd.DataFrame(columns=df.columns.tolist()+['volume'])
        all_stocks_filepath = os.path.join(DATA_PATH, 'ticker_data', 'all_SEC_tickers.csv')
        df = pd.read_csv(all_stocks_filepath, index_col=0)
        for ticker in sorted_stocks:
            df2 = df[df['ticker'] == ticker].copy()
            df2['volume'] = average_volumes[ticker]
            sorted_stocks_df = pd.concat([sorted_stocks_df, df2])
        sorted_stocks_df.reset_index(inplace=True, drop=True)
        sorted_stocks_df.to_csv(filepath)
    # print(sorted_stocks)
    # print(sorted_stocks_df)
    return sorted_stocks
def get_price_history( # TO DO: debug this
    ticker,
    start_date,
    end_date,
    interval,
    verbose=False,
    extended_hours=False):

    '''
        Timeframe for the aggregation. Values are customizeable
        frequently used examples: 1Min, 15Min, 1Hour, 1Day, 1Week, and 1Month
        Limits: 1Min-59Min, 1Hour-23Hour.
        '''
    if interval == 'minute':
        interval = TimeFrame(1, TimeFrameUnit.Minute)
        max_window = timedelta(minutes=59)
    elif interval == 'hour':
        interval = TimeFrame(1, TimeFrameUnit.Hour)
        max_window = timedelta(hours=23)
    elif interval == 'day':
        interval = TimeFrame(1, TimeFrameUnit.Day)
        max_window = None
    elif interval == 'week':
        interval = TimeFrame(1, TimeFrameUnit.Week)
        max_window = None
    elif interval == 'month':
        interval = TimeFrame(1, TimeFrameUnit.Month)
        max_window = None

    if max_window != None:
        current_time = start_date
        df = pd.DataFrame()
        while current_time < end_date:
            next_time = current_time + max_window
            df = pd.concat([df,
                alpaca.get_bars(
                    ticker,
                    interval,
                    "2021-06-08", # current_time,
                    "2021-06-08", # next_time,
                    adjustment='raw').df])
            print(df)
            sys.exit()
            current_time = next_time
    else:
        df = alpaca.get_bars(
            ticker,
            interval,
            start_date,
            end_date)

    # return data and print if requested
    if verbose:
        print(df)
    return df


'''
        i = 0
        block = 500 # max queriable number of tickers
        stocks = []
        while i < len(sec_stocks):
            quotes = TDSession.get_quotes(instruments=sec_stocks[i:i+block])
            equities = [ticker for ticker, quote in quotes.items() if quote['assetType'] == 'EQUITY'] # filter out ETFs and other non-equities
            stocks += equities
            i += block
            print('%d\t%d\t%d' % (len(stocks), i, len(sec_stocks)))
            time.sleep(1)
        tickers_unavailable = list(set(sec_stocks) - set(stocks))
        all_sec_stocks_on_td_ameritrade = df[df['ticker'].isin(stocks)]
        all_sec_stocks_on_td_ameritrade.to_csv(filepath)
    return stocks, stock_category
'''



def select_n_random_tickers(n=500):
    filepath = os.path.join(DATA_PATH, 'ticker_data', '%d_random_tickers.csv' % n)
    try:
        df = pd.read_csv(filepath)
    except:
        all_stocks_filepath = os.path.join(DATA_PATH, 'ticker_data', 'all_SEC_tickers.csv')
        df = pd.read_csv(all_stocks_filepath, index_col=0)
        random_indeces = random.sample(df.index.tolist(), n)
        df = df[df.index.isin(random_indeces)]
        df.drop(columns=['cik', 'name', 'exchange'], inplace=True)
        df.reset_index(inplace=True, drop=True)
        df.to_csv(filepath, index=False)
    return df['ticker'].tolist(), 'random'



if __name__ == '__main__':

    # # sp500 stocks
    # filepath = os.path.join(DATA_PATH, 'ticker_data', 'sp500_tickers.csv')
    # stocks, stock_category = pd.read_csv(filepath)['ticker'].tolist(), 'sp500'
    # print(stocks)
    # print(len(stocks))
    # print(stock_category)
    # sys.exit()

    # # random stocks
    # stocks, stock_category = select_n_random_tickers(n=500)
    # print(stocks)
    # print(len(stocks))
    # print(stock_category)
    # sys.exit()

    # non-sp500 stocks
    # on TD Ameritrade
    # sorted by average minutely volume
    stocks, _ = get_all_sec_stocks_on_alpaca()
    # stocks, _ = get_all_available_alpaca_stocks()
    stocks = sort_stocks_by_average_volume(stocks, plot=False, exclude_sp500_stocks=True)
    # stocks = pd.read_csv('stocks_on_td_ameritrade_sorted_by_average_volume.csv', index_col=0)['ticker'].tolist()
    # n = 500
    # stocks = stocks[:n]
    # print(stocks)
    # print(len(stocks))
