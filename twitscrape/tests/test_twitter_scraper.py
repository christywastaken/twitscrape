from twitscrape.twitter_scraper import TwitterGeolocationScraper

test_scraper = TwitterGeolocationScraper(start_date='2022-06-20', end_date='2022-06-28', filter_links=True, filter_replies=True, is_headless=True)

test_df = test_scraper.run()
test_df.to_csv('test.csv')

#TODO: Learn how to properly utilise pytest, rather than saving a csv of output.
