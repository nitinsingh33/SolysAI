"""
Database Configuration for EV Sentiment Platform
Handles MongoDB and Redis connections
"""
import motor.motor_asyncio
import redis.asyncio as redis
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

class DatabaseManager:
    def __init__(self):
        self.mongodb_client: Optional[motor.motor_asyncio.AsyncIOMotorClient] = None
        self.redis_client: Optional[redis.Redis] = None
        self.database = None
    
    async def connect_mongodb(self):
        """Connect to MongoDB"""
        mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
        self.mongodb_client = motor.motor_asyncio.AsyncIOMotorClient(mongodb_url)
        self.database = self.mongodb_client.ev_sentiment
        print("✅ Connected to MongoDB")
    
    async def connect_redis(self):
        """Connect to Redis"""
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.redis_client = redis.from_url(redis_url)
        print("✅ Connected to Redis")
    
    async def disconnect(self):
        """Disconnect from databases"""
        if self.mongodb_client:
            self.mongodb_client.close()
        if self.redis_client:
            await self.redis_client.close()
        print("🔌 Disconnected from databases")
    
    def get_collection(self, collection_name: str):
        """Get MongoDB collection"""
        return self.database[collection_name]

# Global database instance
database = DatabaseManager()

# Collections
async def get_comments_collection():
    return database.get_collection("comments")

async def get_sentiments_collection():
    return database.get_collection("sentiments")

async def get_brands_collection():
    return database.get_collection("brands")

async def get_analytics_collection():
    return database.get_collection("analytics")
