import asyncio
import uvicorn


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
