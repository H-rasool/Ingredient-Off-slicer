import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME   = os.getenv("MONGO_DB", "off")
COLL_NAME = os.getenv("MONGO_COLLECTION", "products")

client = MongoClient(MONGO_URI, uuidRepresentation="standard")
coll = client[DB_NAME][COLL_NAME]

doc = {
    "_id": "demo-0001",
    "code": "demo-0001",
    "ingredients_text_en": "3 tbsp unsalted butter, softened at room temperature, sugar (12%), cocoa powder (5%), milk powder"
}
coll.replace_one({"_id": doc["_id"]}, doc, upsert=True)
print("Seeded demo-0001 → ", doc)
