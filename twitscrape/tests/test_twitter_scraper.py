from twitscrape.twitter_scraper import TwitterGeolocationScraper

test_scraper = TwitterGeolocationScraper(start_date='2022-01-01', end_date='2022-01-29', filter_links=True, filter_replies=True, is_headless=False, num_threads=3)

date_blocks = test_scraper.create_date_blocks()
print(date_blocks)

#TODO: Learn how to properly utilise pytest, rather than saving a csv of output.
