import json, time
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest, GetOrdersRequest
from alpaca.trading.enums import OrderSide, TimeInForce, QueryOrderStatus, OrderType


'''

	Description:
		example script to place market and limit orders on Alpaca
		WARNING: make sure LIVE_TRADING is set to False!
          
        Todo: test if this only works during market hours
            isn't crypto 24/7 though?

	Sources:
        https://alpaca.markets/sdks/python/trading.html

        https://alpaca.markets/sdks/python/api_reference/trading/orders.html
            see this link for more api functions such as
                get_order_by_id
                replace_order_by_id
                cancel_orders
                cancel_order_by_id

        https://docs.alpaca.markets/docs/working-with-orders
            see this link for more api function such as
                Submitting Trailing Stop Orders
                Listen for Updates to Orders

	'''

# API constants
LIVE_TRADING = False
with open('credentials.json') as f:
	creds = json.load(f)
ENDPOINT   = creds['live_trading' if LIVE_TRADING else 'paper_trading']['ENDPOINT']
API_KEY    = creds['live_trading' if LIVE_TRADING else 'paper_trading']['API_KEY_ID']
API_SECRET = creds['live_trading' if LIVE_TRADING else 'paper_trading']['SECRET_KEY']
trading_client = TradingClient(API_KEY, API_SECRET, paper=not LIVE_TRADING)




####### positions #######

def get_all_positions(verbose=False):
    # sources
    # get_all_positions()
    #     https://docs.alpaca.markets/docs/working-with-positions
    #     https://alpaca.markets/sdks/python/api_reference/trading/positions.html
    # position class https://alpaca.markets/sdks/python/api_reference/trading/models.html#alpaca.trading.models.Position
    # other fields of potential interest:
    # market_value: Total dollar amount of the position.
    # qty_available: Total number of shares available minus open orders.
    # usd: Represents the position in USD values.
    portfolio = trading_client.get_all_positions()

    # Print the quantity of shares for each position.
    if verbose: print(f'\n{len(portfolio)} position(s) in portfolio:')
    for i, position in enumerate(portfolio):
        if verbose: print(f"    position {i + 1} of {len(portfolio)}: {position.side.value} {position.qty} shares of {position.symbol} on the exchange {position.exchange.value}. P/L = ${'%.4f' % float(position.unrealized_pl)} = {'%.4f' % (100 * float(position.unrealized_plpc))} %")

def close_all_positions(verbose=False):
    responses = trading_client.close_all_positions(
        cancel_orders=False, # cancel_orders (Optional[bool]) – If true is specified, cancel all open orders before liquidating all positions.
    ) # returns a list of responses from each closed position containing the status code and order id.
    # source: https://alpaca.markets/sdks/python/api_reference/trading/positions.html
    # each response is of type: ClosePositionResponse
    # source: https://alpaca.markets/sdks/python/api_reference/trading/models.html#alpaca.trading.models.ClosePositionResponse
    if verbose:
        print(f'\nclosed all {len(responses)} position(s):')
        for i, response in enumerate(responses):
            print(f'    order {i + 1} of {len(responses)}:')
            amount = ("%s share(s)" % response.body.qty) if response.body.qty != None else ("$%.2f" % float(response.body.notional))
            limit_price = "" if response.body.type != OrderType.LIMIT else (", limit_price = $%.2f" % float(response.body.limit_price))
            print(f'        {response.body.type.value} order to {response.body.side.value} {amount} of {response.body.symbol}{limit_price}')
            print(f'        status = {response.body.status.value}')

def close_position_by_ticker(verbose=False):
    # todo: close position by ticker
    # source: https://alpaca.markets/sdks/python/api_reference/trading/positions.html#close-a-position

    portfolio = trading_client.get_all_positions()
    if verbose: print(f'\n{len(portfolio)} position(s) in portfolio:')
    for i, position in enumerate(portfolio):

        # close position by symbol
        # source: https://alpaca.markets/sdks/python/api_reference/trading/positions.html#close-a-position
        order = trading_client.close_position(position.symbol) # return type = Order
        # source: https://alpaca.markets/sdks/python/api_reference/trading/models.html#alpaca.trading.models.Order

        if verbose: print(f"    closed position {i + 1} of {len(portfolio)}: {position.side.value} {position.qty} shares of {position.symbol} on the exchange {position.exchange.value}. P/L = ${'%.4f' % float(position.unrealized_pl)} = {'%.4f' % (100 * float(position.unrealized_plpc))} %. order id = {order.id}")



####### orders #######

def place_market_order(verbose=False):

    ''' market order argument details

        https://alpaca.markets/sdks/python/trading.html
            "Market orders allow the trade of fractional shares for stocks. Fractional shares must be denoted either with a non-integer qty value or with the use of the notional parameter. The notional parameter allows you to denote the amount you wish to trade in units of the quote currency. For example, instead of trading 1 share of SPY, we can trade $200 of SPY. notional orders are inherently fractional orders."

        https://alpaca.markets/sdks/python/api_reference/trading/requests.html
            notional "For stocks, only works with MarketOrders"

        note:
            paper trading account reset to resolve this error
            https://github.com/alpacahq/alpaca-trade-api-python/issues/490

        '''
	
    # preparing order
    market_order_data = MarketOrderRequest(
        symbol="AAPL",
        # qty=0.023,
        notional=50.00,
        side=OrderSide.BUY,
        time_in_force=TimeInForce.DAY)

    # place order
    market_order = trading_client.submit_order(order_data=market_order_data)

def place_limit_order(verbose=False):

    # preparing order
    limit_order_data = LimitOrderRequest(
        # symbol="BTC/USD",
        # limit_price=55000, # way lower than current price, so that it isn't filled (for testing purposes)
        symbol="TSLA",
        limit_price=485.00,
        side=OrderSide.SELL,
        qty=1.00,
        # notional=1.00, # alpaca.common.exceptions.APIError: {"code":42210000,"message":"fractional orders cannot be sold short"}        qty=1.00,
        # time_in_force=TimeInForce.FOK,
        # time_in_force=TimeInForce.GTC
        time_in_force=TimeInForce.DAY) # alpaca.common.exceptions.APIError: {"code":42210000,"message":"fractional orders must be DAY orders"}

    # place order
    limit_order = trading_client.submit_order(order_data=limit_order_data)

def get_all_orders(verbose=False):
     
    # params to filter orders by
    request_params = GetOrdersRequest(
        status=QueryOrderStatus.OPEN,
        # side=OrderSide.SELL
    )

    # orders that satisfy params
    orders = trading_client.get_orders(filter=request_params)
    if verbose: print(f'\n{len(orders)} order(s) placed:\n')
    for i, order in enumerate(orders):
        if verbose:
            print(f'    order {i + 1} of {len(orders)}:')
            amount = ("%s share(s)" % order.qty) if order.qty != None else ("$%.2f" % float(order.notional))
            limit_price = "" if order.type != OrderType.LIMIT else (", limit_price = $%.2f" % float(order.limit_price))
            print(f'        {order.type.value} order to {order.side.value} {amount} of {order.symbol}{limit_price}')
            print(f'        status = {order.status.value}')
            # print('\torder id', order.id)
            # print('\tclient_order_id', order.client_order_id) # Client unique order ID
            # print('\tasset_id', order.asset_id)
            # print('\tsymbol', order.symbol)
            # print('\tcreated_at', order.created_at)
            # print('\tupdated_at', order.updated_at)
            # print('\tsubmitted_at', order.submitted_at)
            # print('\tfilled_at', order.filled_at)
            # print('\texpired_at', order.expired_at)
            # print('\tcanceled_at', order.canceled_at)
            # print('\tfailed_at', order.failed_at)
            # print('\treplaced_at', order.replaced_at)
            # print('\treplaced_by', order.replaced_by)
            # print('\treplaces', order.replaces)
            # print('\tnotional', order.notional)
            # print('\tqty', order.qty)
            # print('\tfilled_qty', order.filled_qty)
            # print('\tfilled_avg_price', order.filled_avg_price)
            # print('\torder_class', order.order_class)
            # print('\ttype', order.type) # Valid values: market, limit, stop, stop_limit, trailing_stop.
            # print('\tside', order.side) # Valid values: buy and sell.
            # print('\ttime_in_force', order.time_in_force) # Length of time the order is in force.
            # print('\tlimit_price', order.limit_price)
            # print('\tstop_price', order.stop_price)
            # print('\tstatus', order.status)
            # print('\tlegs', order.legs) # When querying non-simple order_class orders in a nested style, an array of order entities associated with this order. Otherwise, null. TYPE: Optional[List[alpaca.trading.models.Order]]
            # print('\ttrail_percent', order.trail_percent) # The percent value away from the high water mark for trailing stop orders. TYPE: Optional[str]
            # print('\trail_price', order.trail_price) # The dollar value away from the high water mark for trailing stop orders. TYPE: Optional[str]
            print()
            # source: https://alpaca.markets/sdks/python/api_reference/trading/models.html#alpaca.trading.models.Order
    return orders

def cancel_all_orders(verbose=False):
    # source: https://alpaca.markets/sdks/python/api_reference/trading/orders.html#
    trading_client.cancel_orders()
    time.sleep(1.0) # takes a second to update Alpaca's database for my account

def cancel_orders_by_id(verbose=False):
    orders = get_all_orders(verbose=False)
    if verbose and len(orders) > 0: print('\ncancelling %d orders by id:' % len(orders))
    for order in orders:
        order_id = order.id
        trading_client.cancel_order_by_id(order_id)
        if verbose: print('\tcancelled order: %s' % order_id)



####### test #######

if __name__ == '__main__':

    # place_market_order(verbose=True)
    # place_limit_order(verbose=True)
    # cancel_all_orders(verbose=True)
    # cancel_orders_by_id(verbose=True)
    close_all_positions(verbose=True)
    get_all_positions(verbose=True)
    get_all_orders(verbose=True)


    