import unittest

import twitter_scraper



test_scraper = twitter_scraper.TwitterGeolocationScraper(filter_replies=True, filter_links=True, is_headless=True)
tweet_df = test_scraper.run()

print(tweet_df)
unittest.main()
