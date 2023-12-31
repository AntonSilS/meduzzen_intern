import os
from dotenv import load_dotenv


load_dotenv()


class Settings:
    APP_HOST = os.getenv("APP_HOST")
    APP_PORT = int(os.getenv("APP_PORT"))
    BASE_URL = f"http://{APP_HOST}:{APP_PORT}"

    POSTGRES_USER: str = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "tdd")
    POSTGRES_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"

    REDIS_PORT = int(os.getenv("REDIS_PORT"))
    REDIS_HOST = os.getenv("REDIS_HOST")

    SECRET_KEY = os.getenv("SECRET_KEY")
    ALGORITHM = os.getenv("ALGORITHM")
    EXPIRE_TOKEN = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

    DOMAIN = os.getenv("DOMAIN")
    API_AUDIENCE = os.getenv("API_AUDIENCE")
    ISSUER = os.getenv("ISSUER")
    ALGORITHMS = os.getenv("ALGORITHMS"),



settings = Settings()
