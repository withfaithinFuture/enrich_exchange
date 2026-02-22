import asyncio
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import UJSONResponse
from exchange.enrich_exchange_routers import router as exchange_routers


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

    app.include_router(exchange_routers)

    return app



async def main() -> None:
    uvicorn.run(
        "src.app.application.application:get_app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        factory=True,
    )


if __name__ == "__main__":
    asyncio.run(main())
