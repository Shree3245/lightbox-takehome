import os
from dotenv import load_dotenv
from pymongo import MongoClient

# Load environment variables
load_dotenv()

# Environment setup
def env_setup():
    os.environ["MKL_NUM_THREADS"] = "8"
    os.environ["NUMEXPR_NUM_THREADS"] = "8"
    os.environ["OMP_NUM_THREADS"] = "8"

# Create a MongoDB Client
def mongo_client():
    client = MongoClient(os.getenv('MONGO_HOST'))
    return client['takehome']