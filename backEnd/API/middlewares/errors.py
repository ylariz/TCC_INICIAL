from fastapi import Request
from fastapi.responses import JSONResponse


def register_error_handler(app):

    @app.exception_handler(Exception)
    async def error_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error"
            }
        )