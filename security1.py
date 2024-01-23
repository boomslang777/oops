from datetime import  timedelta
import pandas as pd
import time
import json
from kiteconnect import KiteConnect
from stocktrends import Renko
import datetime

def save_to_csv(dataframe, filename):
    dataframe.to_csv(filename, index=False)


def monitor(instrument, direction,quantity,brick_size,days,mult,token,timeframe,kite):
    mark_price = kite.ltp(f"NFO:{instrument}")[f"NFO:{instrument}"]["last_price"]
    print(f"{mark_price} is mark price")
    sl_order_id = kite.place_order(variety=kite.VARIETY_REGULAR,
                                   exchange=kite.EXCHANGE_NFO,
                                   tradingsymbol=instrument,
                                   transaction_type=kite.TRANSACTION_TYPE_SELL,
                                   quantity=quantity,
                                   product=kite.PRODUCT_NRML,
                                   order_type=kite.ORDER_TYPE_SL,
                                   price=mark_price - 4*brick_size,
                                   trigger_price = mark_price -(4*brick_size-5),
                                   tag="SL")
    print(f"Stop loss order placed for BankNifty with order id {sl_order_id}")
    

    while True:
        # current_time = datetime.datetime.now().time()
        # if current_time >= datetime.time(15,25):
        #     print("Current time is greater than 3:25 pm. Exiting SL TRAIL.")
        #     cancel_orders(kite)
        #     square_off_all_positions(kite)
        #     break
        #wait_time = (60 * mult) - (current_time.second % (60 * mult))
        #time.sleep(wait_time)
        #print(f"sleeping for  {wait_time}")
        current_time = datetime.datetime.now().time()
        minutes = current_time.minute
        seconds = current_time.second
        minutes_to_wait = mult - (minutes % mult)
        if minutes_to_wait == mult:
            minutes_to_wait = 0
        seconds_to_wait = 60 - seconds if seconds != 0 else 0
        total_wait_time = minutes_to_wait * 60 + seconds_to_wait
        print(total_wait_time)
        time.sleep(total_wait_time)
        to_date = pd.Timestamp.now().strftime('%Y-%m-%d')
        from_date = (pd.Timestamp.now() - pd.DateOffset(days=days)).strftime('%Y-%m-%d')
        instrument_token = token

        # Fetch historical data for Bank Nifty within the specified date range
        raw_data = kite.historical_data(instrument_token, from_date=from_date, to_date=to_date, interval=timeframe)
        nifty_data = pd.DataFrame(raw_data)
        # Convert 'timestamp' column to datetime
        nifty_data['timestamp'] = pd.to_datetime(nifty_data['date'], unit='ms')

        # Fetch new data and convert it to a DataFrame
        new_data = kite.historical_data(instrument_token, from_date=from_date, to_date=to_date, interval=timeframe)
        new_data_df = pd.DataFrame(new_data)

        # Check if 'timestamp' is present in the columns
        if 'date' in new_data_df.columns:
            # Convert 'timestamp' column to datetime
            new_data_df['timestamp'] = pd.to_datetime(new_data_df['date'], unit='ms')
            nifty_data = nifty_data._append(new_data_df, ignore_index=True)
            print(new_data_df.columns)
            # Call the get_renko function and print the resulting DataFrame
            renko_bricks = df_to_renko(nifty_data, brick_size)
            print("Renko DF")
            print(renko_bricks)

            
            if direction == "BUY" and renko_bricks['uptrend'].iloc[-1]==False:
                cancel_orders(kite)
                square_off_all_positions(kite)
                print("close")
                print("orders close")
                break
                
            elif direction == "SELL" and renko_bricks['uptrend'].iloc[-1]==True:
                cancel_orders(kite)
                square_off_all_positions(kite)
                print("Close positions")
                print("Close orders")
                break
            #current_time = datetime.datetime.now().time()
            #wait_time = (60 * mult) - (current_time.second % (60 * mult))
            #time.sleep(wait_time)
            #print(f"sleeping for  {wait_time}")
            #time.sleep(60*mult)

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
        return renko_bricks



                      
def fire(condition,contract_name,brick_size,quantity,days,mult,token,timeframe,strike,kite):
    square_off_all_positions(kite)
    if condition == 1:
        direction = "BUY"
        option_type = "CE"
    elif condition == -1:
        direction = "SELL"
        option_type = "PE"
    exp = get_exp(contract_name)
    stk = get_stk(contract_name,direction,strike,kite)
    order_info = f"{contract_name}{exp}{stk}{option_type}"
    print(f"{order_info} is order info ")
    place_order(order_info, quantity,kite)
    monitor(order_info, direction,quantity,brick_size,days,mult,token,timeframe,kite)
    calculate_and_log_pnl(kite)


def get_exp(contract_name):
    from datetime import datetime, timedelta
    if contract_name == "BANKNIFTY":
        
        current_date = datetime.now()
        day_of_week = current_date.weekday()

        # If it's Tuesday or Wednesday, add 1 or 0 days respectively to get to the next Wednesday
        days_until_nearest_day = (2 - day_of_week + 7) % 7  # 2 corresponds to Wednesday

        nearest_day_date = current_date + timedelta(days=days_until_nearest_day)
        next_week_date = current_date + timedelta(days=7)

        # Check if the selected expiry is the last week of the month
        if nearest_day_date.month != next_week_date.month or (nearest_day_date.day + 7) > next_week_date.day:
            # If it is, return in the format "YYMON"
            return nearest_day_date.strftime('%y%b').upper()
        else:
            # Regular case
            month = nearest_day_date.strftime('%m').lstrip('0')  # Remove leading zero for month
            return nearest_day_date.strftime('%y{0}%d').format(month) + nearest_day_date.strftime('%y%m%d')[6:]
    elif contract_name == "NIFTY":
        current_date = datetime.now()
        day_of_week = current_date.weekday()

        # If it's Tuesday or Wednesday, add 1 or 0 days respectively to get to the next Wednesday
        days_until_nearest_day = (3 - day_of_week + 7) % 7  # 3 corresponds to Thursday

        nearest_day_date = current_date + timedelta(days=days_until_nearest_day)
        next_week_date = current_date + timedelta(days=7)

        # Check if the selected expiry is the last week of the month
        if nearest_day_date.month != next_week_date.month or (nearest_day_date.day + 7) > next_week_date.day:
            # If it is, return in the format "YYMON"
            return nearest_day_date.strftime('%y%b').upper()
        else:
            # Regular case
            month = nearest_day_date.strftime('%m').lstrip('0')  # Remove leading zero for month
            return nearest_day_date.strftime('%y{0}%d').format(month) + nearest_day_date.strftime('%y%m%d')[6:]
def get_stk(contract_name,direction,offset,kite):
    if contract_name == "BANKNIFTY" :
        if direction == "BUY":
            banknifty_ltp = kite.ltp("NSE:NIFTY BANK")["NSE:NIFTY BANK"]["last_price"]
            print(banknifty_ltp)
            strike_price = round(banknifty_ltp / 100) * 100 - offset
            print(f"{strike_price} is strike price")
            return strike_price
        if direction == "SELL":
            banknifty_ltp = kite.ltp("NSE:NIFTY BANK")["NSE:NIFTY BANK"]["last_price"]
            print(banknifty_ltp)
            strike_price = round(banknifty_ltp / 100) * 100 + offset
            print(f"{strike_price} is strike price")
            return strike_price
        
    elif contract_name == "NIFTY" :
        if direction == "BUY" :
            nifty_ltp = kite.ltp("NSE:NIFTY 50")["NSE:NIFTY 50"]["last_price"]
            print(nifty_ltp)
            strike_price = round(nifty_ltp / 50) * 50 - offset
            print(f"{strike_price} is strike price")
            return strike_price
        if direction == "SELL" :
            nifty_ltp = kite.ltp("NSE:NIFTY 50")["NSE:NIFTY 50"]["last_price"]
            print(nifty_ltp)
            strike_price = round(nifty_ltp / 50) * 50 + offset
            print(f"{strike_price} is strike price")
            return strike_price



def place_order(instrument, qty,kite):
    print(instrument)
    kite.place_order(variety=kite.VARIETY_REGULAR, exchange="NFO",
                     tradingsymbol=instrument,
                     transaction_type="BUY",
                     quantity=qty,
                     order_type="MARKET",
                     product="NRML",
                     validity="DAY",
                     price=0,
                     trigger_price=0)
    print("Position entered successfully")


def square_off_all_positions(kite):
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
                                            product=kite.PRODUCT_NRML,
                                            order_type=kite.ORDER_TYPE_MARKET,
                                            tag="SquareOff")

                # Print information about the square off order
                print(f"Square off order placed for {tradingsymbol} with order id {order_id}")
            else:
                print("No order to square off ")


def calculate_and_log_pnl(kite):
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


def cancel_orders(kite):
    orders = kite.orders()
    print(orders)
    for order in orders:
        if  order["pending_quantity"] > 0 and order["status"] == "TRIGGER PENDING" :
            order_id = order["order_id"]
            print(f"{order_id}is the order id to be cancelled")
            kite.cancel_order(kite.VARIETY_REGULAR, order_id)
            print(f"Order {order_id} cancelled")





#print(get_exp())
#cancel_orders()
#square_off_all_positions()
# print(calculate_and_log_pnl())
#fire(-1)
#monitor("BANKNIFTY23DEC48400PE",1)
# print(qty_selector())
