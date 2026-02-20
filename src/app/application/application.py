from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import UJSONResponse
from src.routers.get_exchange_router import router as get_router
from src.routers.create_exchange_router import router as create_router
from src.routers.update_exchange_router import router as update_router
from src.routers.delete_exchange_router import router as delete_router


def get_app() -> FastAPI:
    """
    FastAPI application factory.
    """

    app = FastAPI(
        docs_url="/docs",
        openapi_url="/openapi.json",
        default_response_class=UJSONResponse,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(get_router)
    app.include_router(create_router)
    app.include_router(update_router)
    app.include_router(delete_router)

    return app
