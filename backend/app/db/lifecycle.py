from app.db.mongo import client as mongo_client
from app.db.redis import close_redis
from app.db.sql import engine


async def close_connections() -> None:
    await engine.dispose()
    mongo_client.close()
    await close_redis()
