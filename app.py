from utils.twitter_scraper import TwitterScraper

today_scraper = TwitterScraper(filter_links=True, filter_replies=True)

today_scraper.run_scraper()

