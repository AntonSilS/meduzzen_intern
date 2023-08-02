import logging
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.log_config import LoggingConfig
from routers import users, auth
from db.connect import init_postgres_db, init_redis_db
from utils.service_config import settings

app = FastAPI()

LoggingConfig.configure_logging()

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

app.include_router(auth.router)
app.include_router(users.router)



@app.on_event("startup")
async def on_startup():
    await init_postgres_db()
    await init_redis_db()


@app.get("/", tags=["healthcheck"])
async def health_check():
    logging.info("Request to the root route")
    return {
        "status_code": 200,
        "detail": "ok",
        "result": "working"
    }


if __name__ == "__main__":
    config = uvicorn.Config("main:app", host=settings.APP_HOST, port=settings.APP_PORT, reload=True)
    server = uvicorn.Server(config)
    server.run()
