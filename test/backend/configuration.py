
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

# Your MongoDB Atlas connection string
MONGODB_URI = "mongodb+srv://manya:manya23@clusternew.wop6qyw.mongodb.net/?retryWrites=true&w=majority&appName=clusternew"

# Create a new client and connect to the server
client = MongoClient(MONGODB_URI, server_api=ServerApi('1'))
db = client["cargo"]
cargo_collection = db["cargodata"]
zone_collection = db["zones"]
log_collection=db["logs"]