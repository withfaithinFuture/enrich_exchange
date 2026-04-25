from fastapi import FastAPI, Request
from fastapi.responses import UJSONResponse
from starlette import status
from src.exceptions import UnavailableServiceError, BadValueError
from src.exchanges.exceptions import NotFoundByNameError


async def unavailable_service_handler(request: Request, exception: UnavailableServiceError):

    return UJSONResponse(
        status_code=status.HTTP_504_GATEWAY_TIMEOUT,
        content=exception.error_schema.model_dump()
    )


async def not_found_handler(request: Request, exception: NotFoundByNameError):

    return UJSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=exception.error_schema.model_dump()
    )


async def bad_value_handler(request: Request, exception: BadValueError):

    return UJSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=exception.error_schema.model_dump()
    )



def register_handler(app: FastAPI):
    app.add_exception_handler(UnavailableServiceError, unavailable_service_handler)
    app.add_exception_handler(NotFoundByNameError, not_found_handler)
    app.add_exception_handler(BadValueError, bad_value_handler)
