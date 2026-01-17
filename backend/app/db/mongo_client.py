"""
MongoDB client for cold storage
"""
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings


class MongoClient:
    """Async MongoDB client wrapper"""
    
    def __init__(self):
        self.client = None
        self.db = None
    
    async def connect(self):
        """Connect to MongoDB"""
        self.client = AsyncIOMotorClient(settings.MONGODB_URL)
        self.db = self.client[settings.MONGODB_DB]
    
    async def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
    
    # Collection accessors
    @property
    def sessions(self):
        """Sessions collection"""
        return self.db.sessions
    
    @property
    def preferences(self):
        """User preferences collection"""
        return self.db.preferences
    
    @property
    def layouts(self):
        """Generated layouts collection"""
        return self.db.layouts
    
    @property
    def telemetry(self):
        """Raw telemetry data collection"""
        return self.db.telemetry


mongo_client = MongoClient()
