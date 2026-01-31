import os
from typing import Optional, Tuple
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME   = os.getenv("MONGO_DB", "off")
COLL_NAME = os.getenv("MONGO_COLLECTION", "products")
PORT      = int(os.getenv("PORT", "8001"))

def get_mongo_collection():
    """Return (client, collection) if MONGO_URI set; else (None, None)."""
    if not MONGO_URI:
        return None, None
    from pymongo import MongoClient
    client = MongoClient(MONGO_URI, uuidRepresentation="standard")
    coll = client[DB_NAME][COLL_NAME]
    return client, coll
