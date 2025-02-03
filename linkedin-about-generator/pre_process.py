import os
import pandas as pd
from pymongo import MongoClient
from dotenv import load_dotenv
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, ArrayType, DoubleType, StringType
import logging
import time

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Load environment variables
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise ValueError("MONGO_URI environment variable is not set.")

# Initialize Spark
spark = SparkSession.builder.appName("PreProcessLinkedIn").getOrCreate()

# MongoDB connection settings
try:
    logging.info("Connecting to MongoDB...")
    client = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=60000,
        connectTimeoutMS=60000,
        socketTimeoutMS=60000,
        maxPoolSize=100,
        waitQueueTimeoutMS=20000
    )
    db = client["linkdin_generator_database"]
    collection_basic_data = db["basic_data"]
    collection_embeddings = db["embedding_users"]
    logging.info("Connected to MongoDB.")
except Exception as e:
    logging.error(f"Failed to connect to MongoDB: {e}")
    raise

# Define schema for embedding Spark DataFrame
schema = StructType([
    StructField("id", StringType(), True),
    StructField("certifications_averaged_embeddings", ArrayType(DoubleType()), True),
    StructField("city_embeddings", ArrayType(DoubleType()), True),
    StructField("company_position_embeddings", ArrayType(DoubleType()), True),
    StructField("education_averaged_embeddings", ArrayType(DoubleType()), True),
    StructField("experience_averaged_embeddings", ArrayType(DoubleType()), True),
    StructField("about", StringType(), True)
])
user_ids = collection_embeddings.distinct("id")
logging.info(f"Total users in embedding_users collection: {len(user_ids)}")
logging.info(f"Sample user IDs: {user_ids[:10]}")
