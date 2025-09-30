import os
import redis
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()


MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")
client = MongoClient(MONGO_URI)
db = client[DB_NAME]


launches_collection = db["launch"]
rockets_collection = db["rockets"]
launchpads_collection = db["launchpads"]


# Redis setup
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))
redis_client = redis.Redis(
    host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True
)
CACHE_TTL = int(os.getenv("CACHE_TTL", 3600))
