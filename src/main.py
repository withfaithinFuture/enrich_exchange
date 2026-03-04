import asyncio
from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import UJSONResponse, JSONResponse
from src.exchange.redis_client import redis_client
from src.exchange.routers import router as exchange_routers
from src.exchange.exception_handler import register_handler


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

    await redis_client.close()


def get_app() -> FastAPI:
    """
    FastAPI application factory.
    """

    app = FastAPI(
        docs_url="/docs",
        openapi_url="/openapi.json",
        default_response_class=UJSONResponse,
        lifespan=lifespan
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(exchange_routers)
    register_handler(app)

    return app



async def main() -> None:
    uvicorn.run(
        "src.main:get_app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        factory=True,
    )


if __name__ == "__main__":
    asyncio.run(main())
