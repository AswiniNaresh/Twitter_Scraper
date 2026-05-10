import os
from dotenv import load_dotenv

load_dotenv()

# MongoDB configuration
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")

# Application settings
MAX_TWEETS = 1000
DEFAULT_TWEET_LIMIT = 100