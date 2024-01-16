from ib_insync import *
ib = IB()
ib.connect('127.0.0.1', 7497, clientId=1)
import logging
logging.basicConfig(level=logging.INFO)
balance = 500
def manage_orders(symbol,expiry,strike,right,exchange,price, qty):
    tolerance = price*1.03
    print(f"{tolerance} is tolerance")

    contract = Option(symbol, expiry, strike, right, exchange)
    print(contract)
    ib.qualifyContracts(contract)

    # Set market data type
    ib.reqMarketDataType(1)

    # Wait for the market data to arrive (you can adjust the time as needed)
    [ticker] = ib.reqTickers(contract)
    # Fetch the LTP for each contract
    ltps = [ticker.marketPrice()]
    print(ltps)
    ltp = float(ltps[0])
    print(f"{qty} is the quantity")
    print(f"{ltp} is the ltp")
    if ltp <= tolerance :
        order = LimitOrder("BUY",qty,tolerance)
        trade = ib.placeOrder(contract, order)
        print("order placed successfully")
    else :
        print("Price out of bounds")
