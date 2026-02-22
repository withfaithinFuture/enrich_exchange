from datetime import timedelta
import httpx
from aiobreaker import CircuitBreaker


first_service_breaker = CircuitBreaker(fail_max=3, timeout_duration=timedelta(seconds=15))

class ExchangeApiService:

    BASE_URL = "http://127.0.0.1:8000/exchange"
    @first_service_breaker
    async def get_exchanges(self) -> list:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(self.BASE_URL)
            response.raise_for_status()

            return response.json()