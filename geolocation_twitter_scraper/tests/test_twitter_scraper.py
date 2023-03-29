import unittest
from twitter_scraper import TwitterScraper

test_scraper = TwitterScraper(filter_links=True, filter_replies=True)
tweet_df = test_scraper.run_scraper()
print(tweet_df)

unittest.main()