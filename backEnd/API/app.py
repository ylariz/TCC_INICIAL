from fastapi import FastAPI
import uvicorn

from API.routes.predictionRoute import router
from API.middlewares.errors import register_error_handler

app = FastAPI()

app.include_router(router)
register_error_handler(app)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8080)