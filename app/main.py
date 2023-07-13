import uvicorn
from fastapi import FastAPI

from utils.service_config import HOST, PORT

app = FastAPI()


@app.get("/")
async def health_check():
    return {
        "status_code": 200,
        "detail": "ok",
        "result": "working"
    }


if __name__ == "__main__":
    config = uvicorn.Config("main:app", host=HOST, port=PORT, reload=True)
    server = uvicorn.Server(config)
    server.run()
