from seleniumwire import webdriver
from seleniumwire.utils import decode
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd
import json
from typing import Tuple
from datetime import datetime, timedelta

class TwitterScraper():

  def __init__(self, start_date: str = None, end_date: str = None, latitude: float = None, longitude: float = None, radius: float = None, filter_replies: bool = False, filter_links: bool = False):
    """
    Initialize the TwitterScraper class with optional parameters. The default values are:
    - start_date: None (today - midnight)
    - end_date: None (tomorrow - midnight tonight)
    - latitude: None (default value will be used)
    - longitude: None (default value will be used)
    - radius: None (default value will be used)
    - filter_replies: False
    - filter_links: False

    You can change these properties when initializing the class or later by assigning new values to the attributes.
    """
    self.start_date = start_date
    self.end_date = end_date
    self.latitude = latitude
    self.longitude = longitude
    self.radius = radius
    self.filter_replies = filter_replies
    self.filter_links = filter_links


  def create_twitter_url(self) -> str:
    # As default it uses Central Newcastle-Upon-Tyne with 10km radius, filters links and replies, sorted by latest. Start_date & end_date: current date.
    
    today = datetime.now()
    if self.start_date == None:
      #Set the start_date to today
      start_date = today.strftime('%Y-%m-%d')
    else: start_date = self.start_date

    if end_date == None:
      #Set the end_date to tomorrow
      tomorrow = today + timedelta(days=1)
      end_date = tomorrow.strftime('%Y-%m-%d')
    else:
      end_date = self.end_date
  
    if latitude == None:
      latitude = '54.972109'
    else:
      latitude = self.latitude

    if longitude == None:
      longitude = '-1.611168'
    else: 
      longitude = self.longitude

    if radius == None:
      radius = 10.0
    else:
      radius = self.radius
    
    if filter_replies == False and filter_links == False:
      return f'https://twitter.com/search?f=live&q=geocode%3A{str(latitude)}%2C{str(longitude)}%2C{str(radius)}km%20until%3A{end_date}%20since%3A{start_date}&src=typed_query'   
    if filter_replies == True and filter_links == False:
      return f'https://twitter.com/search?f=live&q=geocode%3A{str(latitude)}%2C{str(longitude)}%2C{str(radius)}km%20until%3A{end_date}%20since%3A{start_date}%20-filter%3Areplies&src=typed_query'                
    if filter_replies == False and filter_links == True:
      return f'https://twitter.com/search?f=live&q=geocode%3A{str(latitude)}%2C{str(longitude)}%2C{str(radius)}km%20until%3A{end_date}%20since%3A{start_date}%20-filter%3Alinks&src=typed_query'
    if filter_replies == True and filter_links == True:  
      return f'https://twitter.com/search?f=live&q=geocode%3A{str(latitude)}%2C{str(longitude)}%2C{str(radius)}km%20until%3A{end_date}%20since%3A{start_date}%20-filter%3Alinks%20-filter%3Areplies&src=typed_query'

      
  
  # Use ChromeDriverManager().install() to update driver for browser.
  driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
  # Narrows the scope of to requests containing 'adaptive' (the requests containing tweets)
  driver.scopes= ['.*adaptive.*']
  driver.get(twitter_link)

  # Wait for the readyState = complete so page has loaded in. 
  state = ''
  while state != 'complete':
    print('Page loading not complete')
    time.sleep(1)
    state = driver.execute_script('return document.readyState')


  def get_tweets() -> Tuple[pd.DataFrame, int, int]:
    tweet_df = pd.DataFrame(columns=['tweet_text', 'datetime'])
    try:
      # Waits for the response containing 'Adaptive' which contains the tweet data.
      request = driver.wait_for_request('adaptive')
      # Decodes the byte data from the response
      body = decode(request.response.body, request.response.headers.get('Content-Encoding', 'identity')) 
      data = json.loads(body)
      tweets = data['globalObjects']['tweets']
      # Get rate limit info
      rate_lim_remaining = request.response.headers.get('x-rate-limit-remaining')
      rate_lim_reset_time = request.response.headers.get('x-rate-limit-reset')
      for tweet_id, tweet_data in tweets.items():
        # Loops through the tweets and stores the tweet text and datetime to DF.
        tweet_text = tweet_data['full_text']
        created_at = tweet_data['created_at']
        new_row_df = pd.DataFrame({'tweet_text': [tweet_text], 'datetime': [created_at]})
        tweet_df = pd.concat([tweet_df, new_row_df], ignore_index=True)
    except Exception as err:
      print(f'-- Error: {err} --')
    tweet_df.sort_values(by='datetime', ascending=False, inplace=True)
    # Deletes driver.requests so get_tweets() waits for the new request response 
    del driver.requests
    return (tweet_df, int(rate_lim_remaining), int(rate_lim_reset_time))


  def scroll_page() -> int:
    time.sleep(1) # I use a 1s wait for safe measure with my old macbook. 
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
    new_height = driver.execute_script("return document.body.scrollHeight")
    return new_height



  def run_scraper():
    tweet_df, rate_lim_remaining, rate_lim_reset_time = get_tweets()
    #TODO: save tweet_df to sql or csv
    tweet_df.to_csv('test.csv', mode='a', header=False)
    print(f'remaining rate limit: {rate_lim_remaining} | tweet_df length: {len(tweet_df)}')
    if rate_lim_remaining <= 2:
      # If we are getting close to the rate limit, sleep the app until the rate-limit has reset. 
      time_dif = rate_lim_reset_time - time.time()
      # Add 10s for good measure
      wait_time = time_dif + 10 
      print(f'-- Waiting {wait_time /60} mins for rate limit to reset --')
      time.sleep(wait_time)
    


    page_height = scroll_page()

replies_filtered = create_twitter_url(start_date='2023-03-29', end_date='2023-03-30', filter_replies=True)
print('twitter link for replies filtered: ', replies_filtered)

all_filtered = create_twitter_url(filter_links=True, filter_replies=True)
print('twitter link for all filtered without adding time cosntraints: ', all_filtered)
