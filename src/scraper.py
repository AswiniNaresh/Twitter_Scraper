import requests
from bs4 import BeautifulSoup
import logging
from typing import List, Dict, Any
from datetime import datetime
import time
import random

class TwitterScraper:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.nitter_instances = [
            "https://nitter.net",
            "https://nitter.1d4.us",
            "https://nitter.kavin.rocks",
            "https://nitter.unixfox.eu"
        ]
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def _get_working_instance(self) -> str:
        """Find a working Nitter instance"""
        random.shuffle(self.nitter_instances)
        for instance in self.nitter_instances:
            try:
                response = requests.get(f"{instance}/", timeout=5, headers=self.headers)
                if response.status_code == 200:
                    return instance
            except:
                continue
        raise Exception("No working Nitter instance found")

    def _parse_tweet(self, tweet_item) -> Dict[str, Any]:
        """Parse a single tweet HTML element"""
        try:
            # Get tweet text
            tweet_content = tweet_item.find('div', class_='tweet-content')
            content = tweet_content.get_text(strip=True) if tweet_content else ""

            # Get tweet stats
            stats = tweet_item.find_all('span', class_='tweet-stat')
            reply_count = stats[0].get_text(strip=True) if len(stats) > 0 else "0"
            retweet_count = stats[1].get_text(strip=True) if len(stats) > 1 else "0"
            like_count = stats[2].get_text(strip=True) if len(stats) > 2 else "0"

            # Get tweet metadata
            tweet_link = tweet_item.find('a', class_='tweet-link')
            tweet_id = tweet_link['href'].split('/')[-1] if tweet_link else ""
            
            username = tweet_item.find('a', class_='username')
            user = username.get_text(strip=True) if username else ""

            tweet_date = tweet_item.find('span', class_='tweet-date')
            date_str = tweet_date.find('a')['title'] if tweet_date and tweet_date.find('a') else ""
            
            return {
                "date": datetime.strptime(date_str, "%b %d, %Y · %I:%M %p UTC") if date_str else None,
                "id": tweet_id,
                "url": f"https://twitter.com/{user}/status/{tweet_id}" if user and tweet_id else "",
                "content": content,
                "user": user,
                "reply_count": reply_count,
                "retweet_count": retweet_count,
                "like_count": like_count,
                "language": "en",  # Nitter doesn't provide language info
                "source": "Twitter Web App"  # Nitter doesn't provide source info
            }
        except Exception as e:
            self.logger.error(f"Error parsing tweet: {str(e)}")
            return None

    def scrape_tweets(self, keyword: str, start_date: str, end_date: str, tweet_limit: int) -> List[Dict[str, Any]]:
        """
        Scrape tweets based on given parameters using Nitter
        """
        scraped_tweets = []
        instance = self._get_working_instance()
        search_url = f"{instance}/search"

        try:
            params = {
                'q': f"{keyword} since:{start_date} until:{end_date}",
                'f': 'tweets'
            }

            tweets_count = 0
            page = 1

            while tweets_count < tweet_limit:
                # Add page parameter for pagination
                if page > 1:
                    params['page'] = str(page)

                response = requests.get(
                    search_url,
                    params=params,
                    headers=self.headers,
                    timeout=10
                )

                if response.status_code != 200:
                    self.logger.error(f"Error: Received status code {response.status_code}")
                    break

                soup = BeautifulSoup(response.text, 'html.parser')
                tweet_items = soup.find_all('div', class_='timeline-item')

                if not tweet_items:
                    break

                for tweet_item in tweet_items:
                    if tweets_count >= tweet_limit:
                        break

                    tweet_data = self._parse_tweet(tweet_item)
                    if tweet_data:
                        scraped_tweets.append(tweet_data)
                        tweets_count += 1

                # Add delay between requests
                time.sleep(random.uniform(1, 3))
                page += 1

            return scraped_tweets

        except Exception as e:
            self.logger.error(f"Error scraping tweets: {str(e)}")
            raise

    def get_tweet_count(self) -> int:
        """Return the number of scraped tweets"""
        return len(self.scraped_tweets) if hasattr(self, 'scraped_tweets') else 0