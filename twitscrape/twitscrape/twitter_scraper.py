from seleniumwire import webdriver
from seleniumwire.utils import decode
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd
import json
from typing import Tuple
from datetime import datetime, timedelta

#TODO: Should the returned dataframe be a class property?
#TODO: 'filter_links' - does it also filter media? are media classed as links? Find out. Could be misleading. 

class TwitterGeolocationScraper():

    def __init__(self, start_date:str=None, end_date:str=None, latitude:float=54.972109, longitude:float=-1.611168, radius:float=10.0, filter_replies:bool=False, filter_links:bool=False, is_headless:bool=False):
        """
        Initialize the TwitterScraper class with optional parameters. The default values are:
        - start_date: None (default set to today - midnight)
        - end_date: None (default set to tomorrow - midnight tonight)
        - latitude: 54.972109 (default value will be used - Newcastle-Upon-Tyne)
        - longitude: -1.611168 (default value will be used - Newcastle-Upon-Tyne)
        - radius: 10.0 ((km) default value will be used)
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
        self.is_headless = is_headless
        # Set options for browser/driver
        options = Options()
        if is_headless:
            options.add_argument("--headless=new")
          
        # Use ChromeDriverManager().install() to update driver for browser.
        print('-- TwitterGeolocationScraper running. This may take a minute to update the webdriver. --')
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        # Narrows the scope of to requests containing 'adaptive' (the requests containing tweets)
        self.driver.scopes= ['.*adaptive.*']
        # Tweet_df_model
        self.tweet_df = pd.DataFrame(columns=['tweet_id', 'user_id', 'created_at', 'tweet_text', 'hashtags', 'media_url', 'retweet_count', 'favourite_count', 'reply_count', 'views'])
      



    def create_twitter_url(self) -> str:
        # As default it uses Central Newcastle-Upon-Tyne with 10km radius, filters links and replies, sorted by latest. Start_date & end_date: current date.
        today = datetime.utcnow()
        if self.start_date == None:
            #Set the start_date to today
            start_date = today.strftime('%Y-%m-%d')
        else: 
            start_date = self.start_date
        if self.end_date == None:
            #Set the end_date to tomorrow
            tomorrow = today + timedelta(days=1)
            end_date = tomorrow.strftime('%Y-%m-%d')
        else:
            end_date = self.end_date
        latitude = self.latitude
        longitude = self.longitude
        radius = self.radius
        filter_replies = self.filter_replies
        filter_links = self.filter_links
        if filter_replies == False and filter_links == False:
            return f'https://twitter.com/search?f=live&q=geocode%3A{str(latitude)}%2C{str(longitude)}%2C{str(radius)}km%20until%3A{end_date}%20since%3A{start_date}&src=typed_query'   
        if filter_replies == True and filter_links == False:
            return f'https://twitter.com/search?f=live&q=geocode%3A{str(latitude)}%2C{str(longitude)}%2C{str(radius)}km%20until%3A{end_date}%20since%3A{start_date}%20-filter%3Areplies&src=typed_query'                
        if filter_replies == False and filter_links == True:
            return f'https://twitter.com/search?f=live&q=geocode%3A{str(latitude)}%2C{str(longitude)}%2C{str(radius)}km%20until%3A{end_date}%20since%3A{start_date}%20-filter%3Alinks&src=typed_query'
        if filter_replies == True and filter_links == True:  
            return f'https://twitter.com/search?f=live&q=geocode%3A{str(latitude)}%2C{str(longitude)}%2C{str(radius)}km%20until%3A{end_date}%20since%3A{start_date}%20-filter%3Alinks%20-filter%3Areplies&src=typed_query'

    
    def get_tweets(self) -> Tuple[int, int]:
        """
        Waits for the request containing the tweet data.
        Returns a tuple of (tweet dataframe, remaning rate limit, rate limit reset time)
        """
        
        try:
            # Waits for the response containing 'Adaptive' which contains the tweet data.
            request = self.driver.wait_for_request('adaptive')
            # Decodes the byte data from the response
            body = decode(request.response.body, request.response.headers.get('Content-Encoding', 'identity')) 
            data = json.loads(body)
            try:
                tweets = data['globalObjects']['tweets']
            except Exception as err:
                print(f'Error: {err}')
                with open('error_logging.csv', 'a') as f:
                    f.write(f'BODY: {data} \n')
                    f.write(f'HEADERS: {request.response.headers.as_string()} ------------------------------------------ \n')
                #TODO: logg errors properly. 
            # Get rate limit info
            try:
                rate_lim_remaining = int(request.response.headers.get('x-rate-limit-remaining'))
            except:
                rate_lim_remaining = None
            try:
                rate_lim_reset_time = int(request.response.headers.get('x-rate-limit-reset'))
            except:
                rate_lim_reset_time = None
            for tweet_id, tweet_data in tweets.items():
                try:
                    user_id = tweet_data['user_id']
                except:
                    user_id = None
                try:
                  created_at = tweet_data['created_at']
                except:
                    created_at = None
                try:
                    tweet_text = tweet_data['full_text']
                except:
                    tweet_text = None
                try:
                    hashtags_entity = tweet_data['entities']['hashtags']
                    if not hashtags_entity:
                        hashtags = None
                    else:
                        hashtags = '|'.join([x['text'] for x in hashtags_entity])
                except:
                    hashtags = None
                try:
                    media_entities = tweet_data['extended_entities']['media']
                    if not media_entities:
                      media_urls = None
                    else: 
                        media_urls = '|'.join([x['media_url'] for x in media_entities])
                except:
                    media_urls = None
                try:
                    retweet_count = tweet_data['retweet_count']
                except:
                    retweet_count = None
                try:
                    reply_count = tweet_data['reply_count']
                except:
                    reply_count = None
                try:
                    favorite_count = tweet_data['favorite_count']
                except:
                    favorite_count = None
                try:
                    views = tweet_data['ext_views']['count']
                except:
                    views = None

                new_row_df = pd.DataFrame({'tweet_id': [tweet_id],
                                        'user_id': [user_id],
                                        'created_at': [created_at],
                                        'tweet_text': [tweet_text],
                                        'hashtags': [hashtags],
                                        'media_url': [media_urls],
                                        'retweet_count': [retweet_count],
                                        'reply_count': [reply_count],
                                        'favourite_count': [favorite_count],
                                        'views': [views]})
                
                self.tweet_df = pd.concat([self.tweet_df, new_row_df], ignore_index=True)
                
        except Exception as err:
            print(f'-- Error: {err} --')
        print(f'Tweets Scraped: {len(self.tweet_df)}')
        return (rate_lim_remaining, rate_lim_reset_time)



    def run(self) -> pd.DataFrame:
        """ Runs the scraper, returning a dataframe with all of the tweet data."""
        self.driver.get(self.create_twitter_url())
        # Wait for the readyState = complete so page has loaded in. 
        state = ''
        while state != 'complete':
            print('Page loading not complete')
            time.sleep(1) 
            state = self.driver.execute_script('return document.readyState')

        rate_lim_remaining, rate_lim_reset_time = self.get_tweets()
        
        last_height = 0

        while True:
            # Loop until the document.body.scrollHeight no longer increases - end of page reached. 
            try:
                if rate_lim_remaining < 3:
                    # If we are getting close to the rate limit, sleep the app until the rate-limit has reset. 
                    time_dif = rate_lim_reset_time - time.time()
                    wait_time = time_dif + 10 #TODO: check if this is really requried after new changes made to else statement that stopped driver scrolling
                    print(f'-- Waiting {round(wait_time / 60, 2)} mins for rate limit to reset --')
                    try:
                        time.sleep(wait_time)
                    except Exception as err:
                        print(f'Error: {err}')
                        
                # Deletes driver.requests so get_tweets() waits for the new request response 
                del self.driver.requests
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                time.sleep(0.3) #TODO: Work out a better implementation for this timeout. The scrolling should happen when the page is ready, so it doesn't error.
                
                try:
                    rate_lim_remaining, rate_lim_reset_time = self.get_tweets()
                except Exception as err:
                    print(f'Error getting data - get_tweets(). Error: {err}') 

                if new_height == last_height:
                    print('-- Scraper Finished Running. Success. --')
                    return self.tweet_df
                else:
                    last_height = new_height
            except Exception as err:
                print(f'Error: {err}')
                print('-- Scraper Finished Running Prematurely. Incomplete Data Returned (self.tweet_df) --')
                return self.tweet_df
            



