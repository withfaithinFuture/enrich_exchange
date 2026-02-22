from datetime import timedelta
import httpx
from aiobreaker import CircuitBreaker
from tenacity import retry, stop_after_attempt, wait_exponential_jitter, retry_if_exception_type


first_service_breaker = CircuitBreaker(fail_max=3, timeout_duration=timedelta(seconds=15))

class ExchangeApiService:

    BASE_URL = "http://127.0.0.1:8000/exchange"

    @first_service_breaker
    @retry(
        stop=stop_after_attempt(2),
        wait=wait_exponential_jitter(1, max=5),
        retry=retry_if_exception_type(httpx.RequestError),
        reraise=True
    )
    async def get_exchanges(self) -> list:
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.get(self.BASE_URL)
            response.raise_for_status()

            return response.json()