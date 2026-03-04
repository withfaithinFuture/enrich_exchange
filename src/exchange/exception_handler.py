from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from src.exchange.exceptions import UnavailableServiceError


async def unavailable_service_handler(request: Request, exception: UnavailableServiceError):
    return JSONResponse(
        status_code=400,
        content={
            "error": exception.error,
            "message": exception.message
        }
    )


def register_handler(app: FastAPI):
    app.add_exception_handler(UnavailableServiceError, unavailable_service_handler)