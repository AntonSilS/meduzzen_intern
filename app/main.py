import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


from utils.service_config import HOST, PORT, BASE_URL

app = FastAPI()

origins = [
    BASE_URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


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
