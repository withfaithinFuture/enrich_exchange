from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.infrastructure.kafka_consumer_handler import KafkaConsumerHandler
from src.settings import settings
from src.infrastructure.redis_client import redis_client
from src.exchanges.routers import router as exchange_routers
from src.exchanges.exception_handler import register_handler
from src.infrastructure.kafka_consumer import EnrichConsumer


consumer_handler = KafkaConsumerHandler()
kafka_consumer = EnrichConsumer(servers=settings.KAFKA_URL, consumer_handler=consumer_handler)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await kafka_consumer.start()

    yield

    await kafka_consumer.stop()
    await redis_client.close()


def get_app() -> FastAPI:
    """
    FastAPI application factory.
    """

    app = FastAPI(
        docs_url="/docs",
        openapi_url="/openapi.json",
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