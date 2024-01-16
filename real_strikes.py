from ib_insync import *
import pandas as pd
import math

def net_premium(sc, lc, sp, lp):
    return sc + sp - lc - lp



ib = IB()
ib.connect('127.0.0.1', 7497, clientId=1)
spx = Index('SPX', 'CBOE')

ib.qualifyContracts(spx)
cds = ib.reqContractDetails(spx)
ib.reqMarketDataType(4)
[ticker] = ib.reqTickers(spx)
spxValue = (ticker.marketPrice() // 5) * 5
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
print(contracts)


# Create tickers for all contracts
tickers = ib.reqTickers(*contracts)
print(tickers[-1])

# Filter call_strikes based on market prices between 1 and 2
# filtered_calls = [call for call, ticker in zip(contracts, tickers) if call.right == 'C' and 1 <= ticker.marketPrice() <= 2]
# call_strikes = [call.strike for call in filtered_calls]
# filtered_calls_long = [call for call, ticker in zip(contracts, tickers) if call.right == 'C' and 0 <= ticker.marketPrice() <= 1]
# print("Call strikes 1 to 2 ",call_strikes)
# long_strikes = [call.strike for call in filtered_calls_long]
# print("call strikes 0 to 1 ",long_strikes)
# # Filter call_strikes based on market prices between 1 and 2
# filtered_puts = [put for put, ticker in zip(contracts, tickers) if put.right == 'P' and 1 <= ticker.marketPrice() <= 2]
# put_strikes = [put.strike for put in filtered_puts]

# filtered_puts_long = [put for put, ticker in zip(contracts, tickers) if put.right == 'P' and 0 <= ticker.marketPrice() <= 1]
# long_put_strikes = [put.strike for put in filtered_puts_long]

# print("Put Strikes (1 to 2):", put_strikes)
# print("Put Strikes (0 to 1):", long_put_strikes)
# filtered_calls = [call for call, ticker in zip(contracts, tickers) if call.right == 'C' and 0.05 <= ticker.modelGreeks < 0.01]
# call_strikes = [call.strike for call in filtered_calls]
# print(call_strikes)
# filtered_calls = [call for call, ticker in zip(contracts, tickers) if call.right == 'C']

# for call, ticker in zip(filtered_calls, ticker):
#     print(f"Strike: {call.strike}, Model Greeks: {ticker.modelGreeks}")
# filtered_calls_long = [call for call, ticker in zip(contracts, tickers) if call.right == 'C' and 0 <= ticker.marketPrice() < 1.5]
# long_strikes = [call.strike for call in filtered_calls_long]

# filtered_puts = [put for put, ticker in zip(contracts, tickers) if put.right == 'P' and 0 <= ticker.marketPrice() < 1.9]
# put_strikes = [put.strike for put in filtered_puts]

# filtered_puts_long = [put for put, ticker in zip(contracts, tickers) if put.right == 'P' and 0 <= ticker.marketPrice() < 1.2]
# long_put_strikes = [put.strike for put in filtered_puts_long]

# # Initialize variables to store the result
# max_premium_difference = -float('inf')
# result_strikes = None

# # Tolerance for comparing strike differences
# tolerance = 1e-5

# # Iterate through the two call lists
# for strike_0_to_1 in long_strikes:
#     for strike_1_to_2 in call_strikes:
#         # Compute the difference in strike
#         strike_difference =   strike_0_to_1 - strike_1_to_2

#         # Check if the difference is between 25 and 35 with tolerance
#         if 25 - tolerance <= strike_difference <= 35 + tolerance:
#             # Find the corresponding option contracts
#             call_contract_0_to_1 = next(c for c in filtered_calls_long if math.isclose(c.strike, strike_0_to_1, abs_tol=tolerance))
#             call_contract_1_to_2 = next(c for c in filtered_calls if math.isclose(c.strike, strike_1_to_2, abs_tol=tolerance))

#             # Convert contracts to tickers and request market prices
#             ticker_0_to_1 = ib.reqTickers(call_contract_0_to_1)[0]
#             ticker_1_to_2 = ib.reqTickers(call_contract_1_to_2)[0]

#             # Compute the premium difference
#             premium_difference = ticker_1_to_2.marketPrice() - ticker_0_to_1.marketPrice()

#             # Update the result if the premium difference is greater
#             if premium_difference > max_premium_difference:
#                 max_premium_difference = premium_difference
#                 result_strikes = (strike_0_to_1, strike_1_to_2)

# # Print the result
# print("Result Strikes with Max Premium Difference:", result_strikes)

# max_premium_difference_puts = -float('inf')
# result_strikes_puts = None

# # Tolerance for comparing strike differences
# tolerance = 1e-5
# # Iterate through the two put lists
# for strike_0_to_1_put in long_put_strikes:
#     for strike_1_to_2_put in put_strikes:
#         # Compute the difference in strike
#         strike_difference_put =  strike_1_to_2_put - strike_0_to_1_put 
#         # print(f"{strike_0_to_1_put} {strike_1_to_2_put} {strike_difference_put}")  # Corrected variable name

#         # Check if the difference is between 25 and 35 with tolerance
#         if 25 - tolerance <= strike_difference_put <= 35 + tolerance:
#             # Find the corresponding option contracts
#             put_contract_0_to_1 = next(c for c in filtered_puts_long if math.isclose(c.strike, strike_0_to_1_put, abs_tol=tolerance))
#             put_contract_1_to_2 = next(c for c in filtered_puts if math.isclose(c.strike, strike_1_to_2_put, abs_tol=tolerance))

#             # Convert contracts to tickers and request market prices
#             ticker_0_to_1_put = ib.reqTickers(put_contract_0_to_1)[0]
#             ticker_1_to_2_put = ib.reqTickers(put_contract_1_to_2)[0]

#             # Compute the premium difference
#             premium_difference_put = ticker_1_to_2_put.marketPrice() - ticker_0_to_1_put.marketPrice()

#             # Update the result if the premium difference is greater
#             if premium_difference_put > max_premium_difference_puts:
#                 max_premium_difference_puts = premium_difference_put
#                 result_strikes_puts = (strike_0_to_1_put, strike_1_to_2_put)
# net_premium = (
#     ticker_1_to_2.marketPrice() - ticker_0_to_1.marketPrice() +
#     ticker_1_to_2_put.marketPrice() - ticker_0_to_1_put.marketPrice()
# )
# print(f"short call {ticker_1_to_2.marketPrice()} long call {ticker_0_to_1.marketPrice()} short put {ticker_1_to_2_put.marketPrice()} long put {ticker_0_to_1_put.marketPrice()}")
# print("Net Premium:", net_premium)
# # Print the result for puts
# print("Result Strikes with Max Premium Difference (Puts):", result_strikes_puts)

# def place_market_order(contract, action, quantity):
#     order = MarketOrder(action, quantity)
#     trade = ib.placeOrder(contract, order)
#     print(f"Placed {action} order for {quantity} contracts: {contract}")
#     return trade

# # Place market orders for long calls
# # Assuming result_strikes is a tuple (strike_0_to_1, strike_1_to_2) for calls
# strike_0_to_1, strike_1_to_2 = result_strikes

# # Place market order to buy the long call (strike_0_to_1)
# place_market_order(filtered_calls_long[long_strikes.index(strike_0_to_1)], 'BUY', 1)

# # Place market order to sell the short call (strike_1_to_2)
# place_market_order(filtered_calls[call_strikes.index(strike_1_to_2)], 'SELL', 1)

# # Assuming result_strikes_puts is a tuple (strike_0_to_1_put, strike_1_to_2_put) for puts
# strike_0_to_1_put, strike_1_to_2_put = result_strikes_puts

# # Place market order to buy the long put (strike_0_to_1_put)
# place_market_order(filtered_puts_long[long_put_strikes.index(strike_0_to_1_put)], 'BUY', 1)

# # Place market order to sell the short put (strike_1_to_2_put)
# place_market_order(filtered_puts[put_strikes.index(strike_1_to_2_put)], 'SELL', 1)

# print(f"{result_strikes}{result_strikes_puts}")