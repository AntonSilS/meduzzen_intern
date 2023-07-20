import redis.asyncio as redis
from sqlmodel.ext.asyncio.session import AsyncSession, AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine

from utils.service_config import settings

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

engine = AsyncEngine(create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True, future=True))

Base = declarative_base()


async def init_postgres_db():
    try:
        await engine.connect()
        print("Connection to db is successful")

    except Exception as e:
        print(f"Database connection error: {e}")


async def init_redis_db():
    connection = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, password=None)
    print(f"Ping successful: {await connection.ping()}")
    await connection.close()


async def get_session() -> AsyncSession:
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session
