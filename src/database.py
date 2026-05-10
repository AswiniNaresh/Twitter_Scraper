from typing import Dict, List, Any
import pymongo
from datetime import datetime
import logging

class MongoDBHandler:
    def __init__(self, connection_string: str = "mongodb://localhost:27017/"):
        self.client = pymongo.MongoClient(connection_string)
        self.db = self.client["TwitterScraper"]
        self.collection = self.db["ScrapedData"]
        self.logger = logging.getLogger(__name__)

    def save_tweets(self, keyword: str, tweets: List[Dict[str, Any]]) -> bool:
        """
        Save scraped tweets to MongoDB
        """
        try:
            document = {
                "Scraped_Word": keyword,
                "Scraped_Date": datetime.now().strftime("%Y-%m-%d"),
                "Scraped_Data": tweets
            }
            self.collection.insert_one(document)
            return True
        except Exception as e:
            self.logger.error(f"Error saving to MongoDB: {str(e)}")
            return False