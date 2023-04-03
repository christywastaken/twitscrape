import unittest

import twitter_scraper

test_scraper = twitter_scraper.TwitterGeolocationScraper(is_headless=True, filter_replies=True)
test_df = test_scraper.run()
print(test_df.memory_usage(deep=True).sum())
test_df.to_csv('test.csv', index=False)

