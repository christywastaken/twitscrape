from utils.twitter_scraper import TwitterScraper

today_scraper = TwitterScraper(filter_links=True, filter_replies=True)

tweets_df = today_scraper.run_scraper()


tweets_df.to_csv('test2.csv')

