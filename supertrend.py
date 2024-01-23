instrument = "BANKNIFTY"
timeframe = "5minute"
lots = 1
strike = 500
token = 260105
if timeframe =="minute" :
    days = 5
    mult = 1
elif timeframe == "3minute" :
    days= 5
    mult =3
elif timeframe == "5minute" :
    days = 10
    mult = 5
elif timeframe == "10minute" :
    days =20
    mult = 10
elif timeframe == "15minute" :
    days = 35
    mult = 15
elif timeframe == "30minute" :
    days = 45
    mult = 30
elif timeframe == "60minute":
    days = 60
    mult = 60
import pandas as pd
import datetime
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from pyotp import TOTP
import time
from kiteconnect import KiteConnect
import pandas_ta as ta
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import rms

# def autologin():
#     try:
#         token_path = "api_key.txt"
#         key, secret, username, password, totp_secret = open(token_path, 'r').read().split()
#         chrome_options = webdriver.ChromeOptions()
#         chrome_options.binary_location = '/usr/bin/google-chrome-stable'
#         service = Service(executable_path='/usr/local/bin/chromedriver')
#         options = webdriver.ChromeOptions()
#         options.add_argument('--headless')
#         options.add_argument('--disable-gpu')  # Required for headless mode on Linux

#         # Provide the full path to the chromedriver executable
#         chromedriver_path = "/home/ubuntu/chromedriver-linux64/chromedriver"
#         driver = webdriver.Chrome(service=service, options=options)
#         logging.info("WebDriver instance created in headless mode")

#         # Initialize KiteConnect with your API key
#         kite = KiteConnect(api_key=key)
#         logging.info("KiteConnect initialized")
#         kite = KiteConnect(api_key=key)
#         logging.info("KiteConnect initialized")

#         # Open the Kite login page
#         driver.get(kite.login_url())
#         driver.implicitly_wait(10)
#         logging.info("Kite login page opened")

#         # Fill in the username and password fields
#         username_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="userid"]')))
#         password_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="password"]')))

#         logging.info("Username and password fields located")

#         username_input.send_keys(username)
#         password_input.send_keys(password)

#         # Click the "Login" button
#         login_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="container"]/div/div/div/form/div[4]/button')))
#         login_button.click()
#         logging.info("Clicked the 'Login' button")
#         time.sleep(2)

#         # Generate TOTP
#         totp = TOTP(totp_secret)
#         token = totp.now()

#         # Locate the TOTP input field and submit button
#         totp_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="userid"]')))
#         submit_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div/div/div[1]/div[2]/div/div/form/div[2]/button')))

#         totp_input.send_keys(token)
#         submit_button.click()
#         logging.info("Filled TOTP and clicked 'Submit'")
#         time.sleep(5)

#         # Wait for successful login  # Replace with the URL you expect after login
#         logging.info("Successfully logged in")

#         # Extract the request token from the URL
#         url = driver.current_url
#         initial_token = url.split('request_token=')[1]
#         request_token = initial_token.split('&')[0]
#         print(request_token)

#         # Close the WebDriver
#         driver.quit()
#         logging.info("WebDriver closed")

#         # Initialize KiteConnect again with your API key and the new access token
#         kite = KiteConnect(api_key=key)
#         data = kite.generate_session(request_token,secret)
#         access_token = kite.set_access_token(data["access_token"])
#         print(data)
#         logging.info("Jarvis Enabled")
#         #store_access_token(kite.access_token)
#         return kite

#     except StaleElementReferenceException:
#         logging.error("Stale element reference: The element is no longer valid.")
#     except Exception as e:
#         logging.error(f"Error during login: {str(e)}")

driver = webdriver.Chrome()
def autologin():
    try:
        token_path = "api_key.txt"
        key, secret, username, password, totp_secret = open(token_path, 'r').read().split()

        # Create a Chrome WebDriver instance
        driver = webdriver.Chrome()
        logging.info("WebDriver instance created")

        # Initialize KiteConnect with your API key
        kite = KiteConnect(api_key=key)
        logging.info("KiteConnect initialized")

        # Check if access token is stored for today

        # Initialize KiteConnect with your API key
        kite = KiteConnect(api_key=key)
        logging.info("KiteConnect initialized")

        # Open the Kite login page
        driver.get(kite.login_url())
        driver.implicitly_wait(10)
        logging.info("Kite login page opened")

        # Fill in the username and password fields
        username_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="userid"]')))
        password_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="password"]')))

        logging.info("Username and password fields located")

        username_input.send_keys(username)
        password_input.send_keys(password)

        # Click the "Login" button
        login_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="container"]/div/div/div/form/div[4]/button')))
        login_button.click()
        logging.info("Clicked the 'Login' button")
        time.sleep(2)

        # Generate TOTP
        totp = TOTP(totp_secret)
        token = totp.now()

        # Locate the TOTP input field and submit button
        totp_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="userid"]')))
        submit_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div/div/div[1]/div[2]/div/div/form/div[2]/button')))

        totp_input.send_keys(token)
        submit_button.click()
        logging.info("Filled TOTP and clicked 'Submit'")
        time.sleep(5)

        # Wait for successful login  # Replace with the URL you expect after login
        logging.info("Successfully logged in")

        # Extract the request token from the URL
        url = driver.current_url
        print(url)
        initial_token = url.split('request_token=')[1]
        request_token = initial_token.split('&')[0]
        print(request_token)

        # Close the WebDriver
        driver.quit()
        logging.info("WebDriver closed")

        # Initialize KiteConnect again with your API key and the new access token
        kite = KiteConnect(api_key=key)
        data = kite.generate_session(request_token,secret)
        kite.set_access_token(data["access_token"])
        print(data)
        logging.info("Jarvis Enabled")
        return kite

       
    except StaleElementReferenceException:
        logging.error("Stale element reference: The element is no longer valid.")
    except Exception as e:
        logging.error(f"Error during login: {str(e)}")

def run_at_915():
    from datetime import datetime, timedelta
    while True:
        now = datetime.now().astimezone()
        print(now)
        target_time = now.replace(hour=8, minute=15, second=0, microsecond=0)
        
        if now >= target_time:
            kite = autologin()
            fetch_nifty_data(kite)
            break

        time.sleep(1)        

def is_candle_close_above_supertrend(close_price, supertrend_value):
    return close_price > supertrend_value

def is_candle_close_below_supertrend(close_price, supertrend_value):
    return close_price < supertrend_value

def fetch_nifty_data(kite):
    while True:
        current_time = datetime.datetime.now().time()
        if current_time >= datetime.time(15,30):
             print("Current time is greater than 3:30 pm. Exiting the loop.")
             break
        #wait_time = (60 * mult) - (current_time.second % (60 * mult))+2
        #print(f"Current wait time is {wait_time}")
        #time.sleep(wait_time)
        current_time = datetime.datetime.now().time()
        minutes = current_time.minute
        seconds = current_time.second
        minutes_to_wait = mult - (minutes % mult)
        if minutes_to_wait == mult:
            minutes_to_wait = 0
        seconds_to_wait = 60 - seconds if seconds != 0 else 0
        total_wait_time = minutes_to_wait * 60 + seconds_to_wait
        print(total_wait_time)
        # time.sleep(total_wait_time)
        #print("total wait time is {total_wait_time}")
        to_date = pd.Timestamp.now().strftime('%Y-%m-%d')
        from_date = (pd.Timestamp.now() - pd.DateOffset(days=days)).strftime('%Y-%m-%d')
        instrument_token = token

        new_data = kite.historical_data(instrument_token, from_date=from_date, to_date=to_date, interval=timeframe)
        new_data_df = pd.DataFrame(new_data)
        print(new_data_df)
        st1 = ta.supertrend(new_data_df['high'], new_data_df['low'], new_data_df['close'], length=5, multiplier=1.5)
        st2 = ta.supertrend(new_data_df['high'], new_data_df['low'], new_data_df['close'], length=5, multiplier=1.3)
        latest_st1 = st1.iloc[-1]
        latest_st2 = st2.iloc[-1]
        supertrend_values_st1 = latest_st1['SUPERT_5_1.5']
        supertrend_values_st2 = latest_st2['SUPERT_5_1.3']
        if (
        is_candle_close_above_supertrend(new_data_df['close'].iloc[-1], supertrend_values_st1) and
        is_candle_close_above_supertrend(new_data_df['close'].iloc[-1], supertrend_values_st2)
    ):  
            rms.fire(kite,"BUY",strike,lots,instrument,mult,token,days,timeframe)

        elif (
        is_candle_close_below_supertrend(new_data_df['close'].iloc[-1], supertrend_values_st1) and
        is_candle_close_below_supertrend(new_data_df['close'].iloc[-1], supertrend_values_st2)

        ):
            rms.fire(kite,"SELL",strike,lots,instrument,mult,token,days,timeframe)  


run_at_915()            