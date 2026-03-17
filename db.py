import os
from dotenv import load_dotenv
import pymongo
import logging

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = "CampusDrive"
COLLECTION_NAME = "StudentApplicants"

def get_db_collection():
    """
    Initializes a connection to MongoDB and returns the StudentApplicants collection.
    Returns:
        pymongo.collection.Collection: The collection object if successful.
        None: If connection fails.
    """
    try:
        # Handle special characters in password implicitly by trying to parse if needed, 
        # but the best way is to let pymongo handle it or manually quote it. 
        # Since we just have MONGO_URI from env, we'll try to use it directly. 
        # If it fails with the specific ValueError about escaping, we'll try to auto-escape it.
        import urllib.parse
        import re
        
        uri_to_use = MONGO_URI
        
        # Check if it needs escaping by looking for unescaped active characters in password
        # A standard atlas URI looks like: mongodb+srv://user:pass@cluster...
        match = re.search(r'mongodb\+srv://([^:]+):([^@]+)@', uri_to_use)
        if match:
            username = match.group(1)
            password = match.group(2)
            # If the password contains unescaped special characters, quote it
            if any(c in password for c in ['@', ':', '/', '?', '#', '[', ']', '{', '}']):
               quoted_pass = urllib.parse.quote_plus(password)
               quoted_user = urllib.parse.quote_plus(username)
               uri_to_use = uri_to_use.replace(f"{username}:{password}@", f"{quoted_user}:{quoted_pass}@")

        # Establish connection with a short timeout to fail fast if no DB
        # Add tlsAllowInvalidCertificates=True to bypass macOS SSL certificate issues locally
        client = pymongo.MongoClient(uri_to_use, serverSelectionTimeoutMS=5000, tlsAllowInvalidCertificates=True)
        # Attempt to retrieve server info to verify connection
        client.server_info()
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]
        return collection
    except pymongo.errors.ServerSelectionTimeoutError as err:
        logger.error(f"Failed to connect to MongoDB at {MONGO_URI}: {err}")
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred while connecting to MongoDB: {e}")
        return None
