from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
import time
import pandas as pd


#Define constants for location, radius and date.
geocode = 'geocode:54.972109,-1.611168,10.0km'
latitude = '54.972109'
longitude = '-1.611168'
radius = '10.0km'
#TODO: Add date/time constraints.

#No Filter
# twitter_link = f'https://twitter.com/search?q=geocode%3A{latitude}%2C{longitude}%2C{radius}&src=typed_query&f=live'

#Filters links
# twitter_link = f'https://twitter.com/search?f=live&q=geocode%3A{latitude}%2C{longitude}%2C{radius}%20-filter%3Alinks&src=typed_query&f=live'

#Filters links and replies
twitter_link = f'https://twitter.com/search?q=geocode%3A{latitude}%2C{longitude}%2C{radius}%20-filter%3Alinks%20-filter%3Areplies&src=typed_query&f=live'

#Use ChromeDriverManager().install() to update driver for browser.
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.get(twitter_link)

#Wait for the readyState = complete so data has loaded in. 
state = ''
while state != 'complete':
  print('Page loading not complete')
  time.sleep(3)
  state = driver.execute_script('return document.readyState')

#Wait 10s for the DOM element containing data-testid="tweet" to be returned. 
try:
  WebDriverWait(driver, 10).until(expected_conditions.presence_of_all_elements_located((By.CSS_SELECTOR, '[data-testid="tweet"]')))
except WebDriverException:
  print('-- Error! No tweets found. Try running as headless=False to diagnose issue. --')

#Get tweets
tweets = driver.find_elements(By.CSS_SELECTOR, '[data-testid="tweet"]')
print('Num tweets: ',len(tweets))


tweet_df = pd.DataFrame(columns=['tweetText', 'datetime'])

for tweet in tweets:
  try:
    datetime_element = tweet.find_element(By.TAG_NAME, 'time')
    datetime_value = datetime_element.get_attribute('datetime')
    text_element = tweet.find_element(By.CSS_SELECTOR, '[data-testid="tweetText"]')
    text_value = text_element.text
    new_row = {'tweetText': text_value, 'datetime': datetime_value}
    tweet_df = tweet_df.append(new_row, ignore_index=True)
  except Exception as err:
    print(f'Error: {err}')
    continue
  

print(tweet_df)
