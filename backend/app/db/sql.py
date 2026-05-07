from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.settings import settings


class Base(DeclarativeBase):
    pass


engine: AsyncEngine = create_async_engine(settings.mysql_dsn, pool_pre_ping=True)
