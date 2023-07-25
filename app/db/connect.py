import logging
import redis.asyncio as redis
from sqlmodel.ext.asyncio.session import AsyncSession, AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine

from core.log_config import LoggingConfig
from utils.service_config import settings

SQLALCHEMY_POSTGRES_URL = settings.POSTGRES_URL

engine = AsyncEngine(create_async_engine(SQLALCHEMY_POSTGRES_URL, echo=True, future=True))

Base = declarative_base()

LoggingConfig.configure_logging()


async def init_postgres_db():
    try:
        await engine.connect()
        logging.info("Ping successful to Postgres: True")

    except Exception as e:
        logging.info(f"Exception during conn to Postgres: {e}")


async def init_redis_db():
    try:
        connection = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, password=None)
        logging.info(f"Ping successful to Redis: {await connection.ping()}")
        await connection.close()
    except Exception as e:
        logging.info(f"Exception during conn to Redis: {e}")

async def get_session() -> AsyncSession:
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session
