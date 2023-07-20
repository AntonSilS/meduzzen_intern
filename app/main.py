import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from session import init_postgres_db, init_redis_db
from utils.service_config import settings

app = FastAPI()

origins = [
    settings.BASE_URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def on_startup():
    await init_postgres_db()
    await init_redis_db()


@app.get("/")
async def health_check():
    return {
        "status_code": 200,
        "detail": "ok",
        "result": "working"
    }


if __name__ == "__main__":
    config = uvicorn.Config("main:app", host=settings.APP_HOST, port=settings.APP_PORT, reload=True)
    server = uvicorn.Server(config)
    server.run()
