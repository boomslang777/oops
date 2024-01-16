from ib_insync import *
import pandas as pd
# import logging
# logging.basicConfig(level=logging.INFO)
# def close_orders():
#     pass

def close_open_positions():

#     positions = ib.portfolio()

#     for position in positions:
#         contract = position.contract
#         action = None
#         sqoff = None
#         # sqoff = Stock(pos.contract.symbol,"SMART",pos.contract.currency)
#         if contract.secType == 'STK':
#             if position.position > 0:
#                 action = 'SELL'
#                 sqoff = Stock(contract.symbol, contract.exchange, contract.currency)
#             elif position.position < 0:
#                 action = 'BUY'
#                 sqoff = Stock(contract.symbol, contract.exchange, contract.currency)
# # sqoff = Option(pos.contract.symbol,pos.contract.lastTradeDateOrContractMonth,pos.contract.strike,pos.contract.right,"SMART",pos.contract.multiplier,pos.contract.currency)

#         elif contract.secType == 'OPT':
#             if position.position > 0:
#                 action = 'SELL'
#                 sqoff = Option(
#                     contract.symbol,
#                     contract.lastTradeDateOrContractMonth,
#                     contract.strike,
#                     contract.right,
#                     contract.exchange,
#                     contract.multiplier,
#                     contract.currency
#                 )
#             elif position.position < 0:
#                 action = 'BUY'
#                 sqoff = Option(
#                     contract.symbol,
#                     contract.lastTradeDateOrContractMonth,
#                     contract.strike,
#                     contract.right,
#                     contract.exchange,
#                     contract.multiplier,
#                     contract.currency
#                 )

#         if action and sqoff:
#             # Qualify the contract
#             ib.qualifyContracts(sqoff)

#             # Place a market order to close the position
#             order = MarketOrder(action, abs(position.position))
#             ib.placeOrder(sqoff, order)
#             print("Positions squared off successfully")



    possy = ib.portfolio()
    print(possy)
    for pos in possy :
        contract = pos.contract
        if contract.secType == 'STK' :
            if pos.position > 0 :
                action = 'SELL'
                sqoff = Stock(pos.contract.symbol,"SMART",pos.contract.currency)
                ib.qualifyContracts(sqoff)
            elif pos.position < 0 :
                action = 'BUY'
                sqoff = Stock(pos.contract.symbol,"SMART",pos.contract.currency)
                ib.qualifyContracts(sqoff)
        elif contract.secType == 'OPT':
            if pos.position > 0 :
                action = 'SELL'
                sqoff = Option(pos.contract.symbol,pos.contract.lastTradeDateOrContractMonth,pos.contract.strike,pos.contract.right,"SMART",pos.contract.multiplier,pos.contract.currency)
                ib.qualifyContracts(sqoff)
            elif pos.position < 0 :
                action = 'BUY'
                sqoff = Option(pos.contract.symbol,pos.contract.lastTradeDateOrContractMonth,pos.contract.strike,pos.contract.right,"SMART",pos.contract.multiplier,pos.contract.currency)
                ib.qualifyContracts(sqoff)
        Order = MarketOrder(action, abs(pos.position))
        ib.placeOrder(sqoff, Order)
ib = IB()
ib.connect('127.0.0.1', 7497, clientId=225)
spx = Index('SPX', 'CBOE')
ib.qualifyContracts(spx)
cds = ib.reqContractDetails(spx)
ib.reqMarketDataType(1)
[ticker] = ib.reqTickers(spx)
spxValue = ticker.marketPrice()
print(spxValue)
chains = ib.reqSecDefOptParams(spx.symbol, '', spx.secType, spx.conId)

util.df(chains)
chain = next(c for c in chains if c.tradingClass == 'SPXW' and c.exchange == 'SMART')


# Assuming you want contracts for the first expiration date
strikes = [strike for strike in chain.strikes
           if strike % 5 == 0
           and spxValue - 100 < strike < spxValue + 100]
expirations = sorted(exp for exp in chain.expirations)[:3]
rights = ['P', 'C']

# Filter contracts based on a specific expiration
desired_expiration = expirations[0]  # Change this to the desired expiration date
contracts = [Option('SPX', desired_expiration, strike, right, 'SMART')
             for right in rights
             for strike in strikes]
Option()
contracts = ib.qualifyContracts(*contracts)
print(len(contracts))
tickers = ib.reqTickers(*contracts)
call_deltas = [0.05, 0.1]
put_deltas = [-0.05, -0.1]

# Filter call and put tickers based on delta conditions
call_tickers = [ticker for ticker in tickers if ticker.contract.right == 'C' and call_deltas[0] < ticker.modelGreeks.delta < call_deltas[1]]
put_tickers = [ticker for ticker in tickers if ticker.contract.right == 'P' and put_deltas[0] > ticker.modelGreeks.delta > put_deltas[1]]

# Check if the lists are not empty before finding the maximum
max_ltp_call = max(call_tickers, key=lambda ticker: ticker.last, default=None)
max_ltp_put = max(put_tickers, key=lambda ticker: ticker.last, default=None)

# Return the strikes of the calls and puts with maximum LTP if they exist
if max_ltp_call:
    max_ltp_call_strike = max_ltp_call.contract.strike
    print(f"Strike of Call with Max LTP: {max_ltp_call_strike}")
else:
    print("No eligible call options found.")

if max_ltp_put:
    max_ltp_put_strike = max_ltp_put.contract.strike
    print(f"Strike of Put with Max LTP: {max_ltp_put_strike}")
else:
    print("No eligible put options found.")

offset = 30

# Store short put and short call contracts in a list
short_put_contract = max_ltp_put.contract
short_call_contract = max_ltp_call.contract
short_contracts = [short_put_contract, short_call_contract]

# Qualify the short contracts using ib.qualifyContracts
ib.qualifyContracts(*short_contracts)

# Now, qualify the long put and long call contracts
long_put_contract = Contract()
long_put_contract.symbol = short_put_contract.symbol
long_put_contract.secType = short_put_contract.secType
long_put_contract.lastTradeDateOrContractMonth = short_put_contract.lastTradeDateOrContractMonth
long_put_contract.strike = short_put_contract.strike - offset
long_put_contract.right = 'P'  # Put option
long_put_contract.exchange = short_put_contract.exchange

long_call_contract = Contract()
long_call_contract.symbol = short_call_contract.symbol
long_call_contract.secType = short_call_contract.secType
long_call_contract.lastTradeDateOrContractMonth = short_call_contract.lastTradeDateOrContractMonth
long_call_contract.strike = short_call_contract.strike + offset
long_call_contract.right = 'C'  # Call option
long_call_contract.exchange = short_call_contract.exchange

# Use ib.qualifyContracts to get additional contract details for the long contracts
ib.qualifyContracts(long_put_contract, long_call_contract)

# Now you have qualified contracts for both short and long options
print("Qualified Short Put Contract:", short_put_contract)
print("Qualified Long Put Contract:", long_put_contract)
print("Qualified Short Call Contract:", short_call_contract)

print("Qualified Long Call Contract:", long_call_contract)    
short_put_md = ib.reqTickers(short_put_contract)[0]
short_call_md = ib.reqTickers(short_call_contract)[0]
long_put_md = ib.reqTickers(long_put_contract)[0]
long_call_md = ib.reqTickers(long_call_contract)[0]

# Calculate the net premium
net_premium = (short_put_md.marketPrice() + short_call_md.marketPrice()) - (long_put_md.marketPrice() + long_call_md.marketPrice())
print(net_premium)
#Very important code that works on real account but not on demo
# combo_legs = [
#     ComboLeg(conId=short_put_contract.conId, ratio=-1, action='SELL', exchange=short_put_contract.exchange),
#     ComboLeg(conId=long_put_contract.conId, ratio=1, action='BUY', exchange=long_put_contract.exchange),
#     ComboLeg(conId=short_call_contract.conId, ratio=-1, action='SELL', exchange=short_call_contract.exchange),
#     ComboLeg(conId=long_call_contract.conId, ratio=1, action='BUY', exchange=long_call_contract.exchange),
# ]
# combo = Bag(symbol = 'SPX',exchange = 'SMART', currency = 'USD',comboLegs = combo_legs)
# trade = ib.placeOrder(combo,MarketOrder("SELL",1))
long_put_order = MarketOrder('BUY', 1)
long_put_entry = ib.placeOrder(long_put_contract, long_put_order)
print("Market order for Long Put placed.")
ib.sleep(2)
lp = long_put_entry.orderStatus.avgFillPrice

long_call_order = MarketOrder('BUY', 1)
long_call_entry = ib.placeOrder(long_call_contract, long_call_order)
print("Market order for Long Call placed.")
ib.sleep(2)
lc = long_call_entry.orderStatus.avgFillPrice
short_put_order = MarketOrder('SELL', 1)
short_put_entry = ib.placeOrder(short_put_contract, short_put_order)
print("Market order for Short Put placed.")
ib.sleep(2)
sp = short_put_entry.orderStatus.avgFillPrice
print(f"{short_put_entry.filled()} is fill price")
# Place market order for long put



# Place market order for short call
short_call_order = MarketOrder('SELL', 1)
short_call_entry = ib.placeOrder(short_call_contract, short_call_order)
print("Market order for Short Call placed.")
ib.sleep(2)
sc = short_call_entry.orderStatus.avgFillPrice
executed_premium = sp + sc - lp - lc #arbitrary
print(f"{executed_premium} is the executed premium")
# Place market order for long call
while True:
    print("entered here")
    net_premium = (short_put_md.marketPrice() + short_call_md.marketPrice()) - (long_put_md.marketPrice() + long_call_md.marketPrice())
    print(f"{net_premium} is net premium")
    if net_premium > executed_premium + 0.05 :
        diff1 = 5*executed_premium / 100
        diff2 = 15*executed_premium / 100
        print(diff1)
        print(diff2)
        sl_short_call = StopLimitOrder("BUY", short_call_entry.filled(), short_call_md.marketPrice()*diff1+short_call_md.marketPrice(), short_call_md.marketPrice()*diff2+short_call_md.marketPrice())
        sl_short_put = StopLimitOrder("BUY", short_put_entry.filled(), short_put_md.marketPrice()*diff1+short_put_md.marketPrice(),short_put_md.marketPrice()*diff2+short_put_md.marketPrice())
        sl_long_call = StopLimitOrder("SELL", long_call_entry.filled(), long_call_md.marketPrice()*diff1-long_call_md.marketPrice(),long_call_md.marketPrice()*diff2-long_call_md.marketPrice())
        sl_long_put = StopLimitOrder("SELL", long_put_entry.filled(), long_put_md.marketPrice()*diff1-long_put_md.marketPrice(),long_put_md.marketPrice()*diff2-long_put_md.marketPrice())
        
        # Place the stop-loss orders
        ib.placeOrder(short_call_contract, sl_short_call)
        ib.placeOrder(short_put_contract, sl_short_put)
        ib.placeOrder(long_call_contract, sl_long_call)
        ib.placeOrder(long_put_contract, sl_long_put)
        break       
        
while True :
    net_premium =   (short_put_md.marketPrice() + short_call_md.marketPrice()) - (long_put_md.marketPrice() + long_call_md.marketPrice())       
    if net_premium > executed_premium + 35 :
        #close_open_positions()
        #close_orders()
        break
    ib.sleep(5)
