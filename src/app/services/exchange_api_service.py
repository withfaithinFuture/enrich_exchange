import httpx


class ExchangeApiService:

    BASE_URL = "http://127.0.0.1:8000/exchange"

    async def get_exchanges(self) -> list:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(self.BASE_URL)

            return response.json()