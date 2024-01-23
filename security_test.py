from datetime import datetime, timedelta
import pandas as pd
import time
import json
from kiteconnect import KiteConnect
import pandas_ta as ta
from stocktrends import Renko

quantity = 15
key = "9gdjvyog0alqsyll"

# Open the JSON file and load the data
with open('access_token.json', 'r') as file:
    data = json.load(file)

# Access the 'access_token' from the loaded data
access_token = data.get('access_token')
kite = KiteConnect(api_key=key)
kite.set_access_token(access_token)

def save_to_csv(dataframe, filename):
    dataframe.to_csv(filename, index=False)

def qty_selector():
    return kite.margins(segment="equity")['net']
def monitor(instrument, direction):
    banknifty_ltp = kite.ltp("NSE:NIFTY BANK")["NSE:NIFTY BANK"]["last_price"]
    print(banknifty_ltp)
    mark_price = kite.ltp(f"NFO:{instrument}")[f"NFO:{instrument}"]["last_price"]
    print(f"{mark_price} is mark price")
    sl_order_id = kite.place_order(variety=kite.VARIETY_REGULAR,
                                   exchange=kite.EXCHANGE_NFO,
                                   tradingsymbol=instrument,
                                   transaction_type=kite.TRANSACTION_TYPE_SELL,
                                   quantity=quantity,
                                   product=kite.PRODUCT_MIS,
                                   order_type=kite.ORDER_TYPE_SL,
                                   price=mark_price - 40,
                                   trigger_price = mark_price -35,
                                   tag="SL")
    print(f"Stop loss order placed for BankNifty with order id {sl_order_id}")
    
    highest_high = get_ltp(instrument)

# Main loop

    remaining_quantity = quantity
    while True:
        ltp = get_ltp(instrument)
    
        if ltp > highest_high:
            highest_high = ltp
            print(f"{highest_high} is the highest high")

        elif highest_high - ltp > 20:
            # Calculate the quantity to square off (half of the remaining quantity)
            quantity_to_square_off = remaining_quantity // 2
            quantity_to_square_off = max(1, quantity_to_square_off)  # Ensure at least 1 lot is squared off

            # Modify the stop-loss order for the remaining quantity
            kite.modify_order(
                variety=kite.VARIETY_REGULAR,
                order_id=sl_order_id,
                quantity=remaining_quantity - quantity_to_square_off,
                trigger_price=ltp - 35,
                price=ltp - 40
            )
            print(f"Stop loss order modified for remaining quantity: {remaining_quantity - quantity_to_square_off}")

            # Square off half the quantity
            kite.place_order(
                variety=kite.VARIETY_REGULAR,
                exchange=kite.EXCHANGE_NFO,
                tradingsymbol=instrument,
                transaction_type=kite.TRANSACTION_TYPE_SELL if direction == "BUY" else kite.TRANSACTION_TYPE_BUY,
                quantity=quantity_to_square_off,
                product=kite.PRODUCT_MIS,
                order_type=kite.ORDER_TYPE_MARKET,
            )
            print(f"Squared off {quantity_to_square_off} quantity due to price fall.")

            # Update remaining quantity
            remaining_quantity -= quantity_to_square_off
            

        
        to_date = pd.Timestamp.now().strftime('%Y-%m-%d')
        from_date = (pd.Timestamp.now() - pd.DateOffset(days=5)).strftime('%Y-%m-%d')
        instrument_token = 260105

        # Fetch historical data for Bank Nifty within the specified date range
        raw_data = kite.historical_data(instrument_token, from_date=from_date, to_date=to_date, interval="minute")
        nifty_data = pd.DataFrame(raw_data)

        # Print and save nifty_data to CSV
       

        # Convert 'timestamp' column to datetime
        nifty_data['timestamp'] = pd.to_datetime(nifty_data['date'], unit='ms')

        # Fetch new data and convert it to a DataFrame
        new_data = kite.historical_data(instrument_token, from_date=from_date, to_date=to_date, interval="minute")
        new_data_df = pd.DataFrame(new_data)

        # Check if 'timestamp' is present in the columns
        if 'date' in new_data_df.columns:
            # Convert 'timestamp' column to datetime
            new_data_df['timestamp'] = pd.to_datetime(new_data_df['date'], unit='ms')

            # Append new data to the existing dataframe
            nifty_data = nifty_data._append(new_data_df, ignore_index=True)
            print(new_data_df.columns)
            # Call the get_renko function and print the resulting DataFrame
            renko_bricks = df_to_renko(nifty_data, 20)
            print("Renko DF")
            print(renko_bricks)
            renko_bricks['ao'] = ta.ao(renko_bricks['high'], renko_bricks['low'])

    # Calculate Donchian Channels
            donchian_df = ta.donchian(renko_bricks['high'], renko_bricks['low'], 10, 10)

        # Merge the calculated Donchian Channels with the original DataFrame
            df = pd.concat([renko_bricks, donchian_df], axis=1)
            print("Renko Data:")
            print(df)
            if direction == "BUY" and renko_bricks['close'].iloc[-1] < renko_bricks['open'].iloc[-1]:
                cancel_orders()
                square_off_all_positions()
                print("close")
                print("orders close")
                break
                
            elif direction == "SELL" and renko_bricks['close'].iloc[-1] > renko_bricks['open'].iloc[-1]:
                cancel_orders()
                square_off_all_positions()
                print("Close positions")
                print("Close orders")
                break

            time.sleep(60)

def df_to_renko(data, n):
        data.reset_index(inplace=True)
        data.columns = [i.lower() for i in data.columns]
        
        if 'datetime' in data.columns:
            data['date'] = data['datetime']
        elif 'date' in data.columns:
            data['date'] = data['date']

        print(data.isnull().values.any())

        df_renko = Renko(data)
        df_renko.brick_size = n
        renko_bricks = df_renko.get_ohlc_data()
        return renko_bricks[:-1]

# def get_renko(timestamps, close, step):
#     prices = close
#     first_brick = {
#         'timestamp': timestamps[0],
#         'open': (prices.iloc[0] // step) * step,
#         'close': ((prices.iloc[0] // step) + 1) * step
#     }
#     bricks = [first_brick]
    
#     for timestamp, price in zip(timestamps, prices):
#         if price > (bricks[-1]['close'] + step):
#             step_mult = (price - bricks[-1]['close']) // step
#             next_bricks = [{
#                 'timestamp': timestamp,
#                 'open': bricks[-1]['close'] + (mult * step),
#                 'close': bricks[-1]['close'] + ((mult + 1) * step)
#             } for mult in range(1, int(step_mult) + 1)]
#             bricks += next_bricks

#         elif price < (bricks[-1]['open'] - step):
#             step_mult = (bricks[-1]['open'] - price) // step
#             next_bricks = [{
#                 'timestamp': timestamp,
#                 'open': bricks[-1]['close'] - ((mult + 1) * step),
#                 'close': bricks[-1]['close'] - (mult * step)
#             } for mult in range(1, int(step_mult) + 1)]
#             bricks += next_bricks

#     df = pd.DataFrame(bricks)
#     df['high'] = df['close'].shift(-1)
#     df['low'] = df['open'].shift(-1)
#     df = df[:-1]  # Remove the last row with NaN values
#     # df.to_csv('renko_data.csv', index=False)

#     return df

                      
def fire(condition):
    square_off_all_positions()
    if condition == 1:
        direction = "BUY"
        option_type = "CE"
    elif condition == -1:
        direction = "SELL"
        option_type = "PE"
    exp = get_exp().upper()
    stk = get_stk(direction)
    contract_name = "BANKNIFTY"
    order_info = f"{contract_name}{exp}{stk}{option_type}"
    place_order(order_info, quantity)
    monitor(order_info, direction)


def get_exp():
    current_date = datetime.now()
    day_of_week = current_date.weekday()
    days_until_wednesday = (2 - day_of_week + 7) % 7
    nearest_wednesday_date = current_date + timedelta(days=days_until_wednesday)

    if nearest_wednesday_date.month != (nearest_wednesday_date + timedelta(days=7)).month:
        # Last week of the month, return in the format "YYMON"
        return nearest_wednesday_date.strftime('%y%b')
    else:
        # Regular case, return in the format "YYMDD"
        return nearest_wednesday_date.strftime('%y%m%d')[1:]


def get_stk(condition):
    banknifty_ltp = kite.ltp("NSE:NIFTY BANK")["NSE:NIFTY BANK"]["last_price"]
    print(banknifty_ltp)
    strike_price = round(banknifty_ltp / 100) * 100
    print(f"{strike_price} is strike price")

    if condition == "BUY":
        return strike_price + 500
    elif condition == "SELL":
        return strike_price - 500
    else:
        return strike_price


def place_order(instrument, qty):
    print(instrument)
    kite.place_order(variety=kite.VARIETY_REGULAR, exchange="NFO",
                     tradingsymbol=instrument,
                     transaction_type="BUY",
                     quantity=qty,
                     order_type="MARKET",
                     product="MIS",
                     validity="DAY",
                     price=0,
                     trigger_price=0)
    print("Position entered successfully")


def square_off_all_positions():
    # Fetch current positions
    positions = kite.positions()

    # Iterate through each position type ('net', 'day')
    for position_type in ['net']:
        # Iterate through positions of the current type
        for position in positions.get(position_type, []):
            # Extract relevant information
            tradingsymbol = position['tradingsymbol']
            quantity = position['quantity']
            if quantity > 0:
                # Place a market sell order to square off the position
                order_id = kite.place_order(variety=kite.VARIETY_REGULAR,
                                            exchange=kite.EXCHANGE_NFO,
                                            tradingsymbol=tradingsymbol,
                                            transaction_type=kite.TRANSACTION_TYPE_SELL,
                                            quantity=quantity,
                                            product=kite.PRODUCT_MIS,
                                            order_type=kite.ORDER_TYPE_MARKET,
                                            tag="SquareOff")

                # Print information about the square off order
                print(f"Square off order placed for {tradingsymbol} with order id {order_id}")
            else:
                print("No order to square off ")


def calculate_and_log_pnl():
    orders = kite.orders()
    completed_orders = [order for order in orders if order['status'] == 'COMPLETE']

    total_pnl = 0

    # Print the orders dictionary
    print("Orders Dictionary:", orders)

    for squareoff_order in completed_orders:
        if 'tags' in squareoff_order and 'SquareOff' in squareoff_order['tags']:
            entry_order = next((order for order in completed_orders if
                                order['instrument_token'] == squareoff_order['instrument_token']
                                and order['product'] == squareoff_order['product']
                                and order['transaction_type'] != squareoff_order['transaction_type']
                                and order['status'] == 'COMPLETE'), None)

            if entry_order:
                entry_price = entry_order['average_price']
                entry_quantity = entry_order['filled_quantity']

                squareoff_price = squareoff_order['average_price']
                squareoff_quantity = squareoff_order['filled_quantity']

                # Print additional information for debugging
                print(f"Entry Quantity: {entry_quantity}, SquareOff Quantity: {squareoff_quantity}")

                # Ensure the quantities match
                if entry_quantity == squareoff_quantity:
                    pnl = (squareoff_price - entry_price) * entry_quantity

                    # Print additional information for debugging
                    print(f"Entry Price: {entry_price}, Entry Quantity: {entry_quantity}")
                    print(f"SquareOff Price: {squareoff_price}, SquareOff Quantity: {squareoff_quantity}")

                    total_pnl += pnl

                    # Log the individual PNL for each completed order
                    print(f"Entry Order ID: {entry_order['order_id']}, SquareOff Order ID: {squareoff_order['order_id']}, PNL: {pnl}")
                else:
                    print("Quantity mismatch between Entry and SquareOff orders.")
            else:
                print(f"No matching entry order found for SquareOff Order ID: {squareoff_order['order_id']}")
        else:
            print(f"SquareOff tag not found for Order ID: {squareoff_order['order_id']}")

    # Log the total PNL for all completed orders
    print(f'Total PNL: {total_pnl}')
    return total_pnl


def cancel_orders():
    orders = kite.orders()
    print(orders)
    for order in orders:
        if order["status"] == "OPEN" and order["pending_quantity"] > 0:
            order_id = order["order_id"]
            print(order_id)
            kite.cancel_order(kite.VARIETY_REGULAR, order_id)
            print(f"Order {order_id} cancelled")




def get_ltp(instrument):
   return kite.ltp(f"NFO:{instrument}")[f"NFO:{instrument}"]["last_price"]


# nfo = kite.instruments("NFO")
# nfo_data = pd.DataFrame(nfo)
# nfo_data.to_csv('nfo_data.csv', index=False)

print(get_exp().upper())
# cancel_orders()
# square_off_all_positions()
# print(calculate_and_log_pnl())
# fire(-1)
# monitor("BANKNIFTY23DEC47000PE",1)
# print(qty_selector())
#token for nifty is 256265