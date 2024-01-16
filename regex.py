import re
import ibkr
from datetime import datetime
balance = 500

# Define high risk phrases at the global scope
high_risk_phrases = ["high risk", "sizing lighter than usual", "light size", "sized lighter", "risky", "not using a hard stop", "lotto"]

def convert_date_format(input_date):
    # Get the current year
    current_year = datetime.now().year

    # Split the input date into month and day
    month, day = map(int, input_date.split('/'))

    # Create a datetime object with the current year, input month, and input day
    result_date = datetime(current_year, month, day)

    # Format the result date as "yyyymmdd"
    formatted_date = result_date.strftime('%Y%m%d')

    return formatted_date

def determine_account_size(message, balance):
    if any(phrase in message for phrase in high_risk_phrases):
        return 0.15 * balance
    else:
        return 0.40 * balance

def extract_fields(message):
    # Define a regular expression pattern to capture the relevant fields
    pattern = r'(\bBTO|STO|BTC|STC\b)\s*\$([A-Z]+)\s*(\d{1,2}/\d{1,2})\s*(\d{3,})\s*(C|P)\s*([\d.]+)'

    # Search for the pattern in the message
    match = re.search(pattern, message)
    if match :
        action = match.group(1)
        instrument = match.group(2)
        expiry = match.group(3)
        exps = convert_date_format(expiry)
        strike = match.group(4)
        stk = float(strike)
        right = match.group(5)
        price = match.group(6)
        pri = float(price)

        # Determine the account size based on the message content
        account_size = determine_account_size(message, balance)

        # Adjust the quantity based on the account size
        qty = account_size // pri

        # Check if the message contains "added"
        if "added" in message:
            # Increase the account size and adjust the quantity accordingly
            account_size = account_size * 1.25 if any(phrase in message for phrase in high_risk_phrases) else account_size * 1.5
            qty = account_size // pri

        ibkr.manage_orders(instrument,exps,stk,right,"SMART",pri, qty)
    else :
        print("wrong message homie")

   

# Your specific message
# your_message = "#ALERT\n\nBTO $SPY 1/10 468C\n\n1.61\n\n____\n\nRoom for one add if we dip a bit lower"


# # # # Extract fields from your message
# extract_fields(your_message)

# if fields:
#     print("Extracted Fields:")
#     for key, value in fields.items():
#         print(f"{key}: {value}")
# else:
#     print("No match found in the message.")



