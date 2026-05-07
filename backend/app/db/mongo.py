from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.core.settings import settings

client = AsyncIOMotorClient(settings.mongodb_dsn)
database: AsyncIOMotorDatabase = client[settings.mongodb_db]
