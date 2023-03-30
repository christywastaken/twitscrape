from ...geolocation_twitter_scraper.src.geolocation_twitter_scraper.twitter_scraper import TwitterGeolocationScraper

test_scraper = TwitterGeolocationScraper(filter_replies=True, filter_links=True)
tweet_df = test_scraper.run()

print(tweet_df)

