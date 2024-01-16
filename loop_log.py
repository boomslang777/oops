import tweepy
from datetime import datetime, timedelta
import time
import regex
import csv

# Replace these values with your Twitter API keys and access tokens
api_key = "iwp2xEOKk9AdgmBDXzVLVn24L"
api_secret = "VpTOJjlHkuyalpcmS40w3OQYriALybH3crzk7IkZFR70DHyRA8"
bearer_token = "AAAAAAAAAAAAAAAAAAAAAM9VrwEAAAAAdjGQHUIbFw1vAQLulxTdcn2zuRQ%3DRh5HFtnMOlCjyFYKqtAjCEdLv45o5LlWCZwLaryVzc2l5u7Ikx"
access_token = "1743537760428781569-I7jshYQ0UXXlj6lRmwXjCGX1hJlwAY"
access_token_secret = "DrDbKYc6pAezfscNCe5ijdPO1apFfc7kwWHgxtTXrdmHo"

# Initialize Tweepy client and authentication
client = tweepy.Client(bearer_token, api_key, api_secret, access_token, access_token_secret)
auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_token, access_token_secret)
api = tweepy.API(auth)

# Set the initial start time to current UTC time minus an hour
start_time = datetime.utcnow() - timedelta(hours=1)

# Open CSV file in write mode and create a CSV writer
with open('tweet_log.csv', 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['Timestamp', 'Message']
    csv_writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    # Write the header to the CSV file
    csv_writer.writeheader()

    # Run the loop
    while True:
        # Calculate the end time as the current UTC time
        end_time = datetime.utcnow()

        # Convert datetimes to string format required by the API
        start_time_str = start_time.strftime('%Y-%m-%dT%H:%M:%SZ')
        end_time_str = end_time.strftime('%Y-%m-%dT%H:%M:%SZ')

        try:
            # Get tweets in the specified time range
            tweets = client.get_home_timeline(start_time=start_time_str, end_time=end_time_str, max_results=1)
            
            if tweets.data:
                first_tweet = tweets.data[0]
                tweet_text = first_tweet.text
                print(tweet_text)
                fields = regex.extract_fields(tweet_text)

                # Write timestamp and message to the CSV file
                csv_writer.writerow({'Timestamp': end_time_str, 'Message': tweet_text})

            # Update the start time for the next iteration
            start_time = end_time

        except tweepy.errors.TooManyRequests:
            print("Rate limit exceeded. Sleeping for 3 minutes.")
            time.sleep(180)  # Sleep for 3 minutes (180 seconds)
            continue

        # Wait for 3 minutes before the next iteration
        time.sleep(180)  # Sleep for 3 minutes (180 seconds)
