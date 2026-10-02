from fastapi import FastAPI
import uvicorn

from API.routes.predictionRoute import router as prediciton_router
from API.routes.interpreterRoute import router as interpreter_router
from API.middlewares.errors import register_error_handler

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(prediciton_router)
app.include_router(interpreter_router)
register_error_handler(app)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8080)