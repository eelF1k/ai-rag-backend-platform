from app.db.mongo import client as mongo_client
from app.db.sql import engine


async def close_connections() -> None:
    await engine.dispose()
    mongo_client.close()
