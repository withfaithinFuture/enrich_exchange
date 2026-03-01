import httpx
from aiobreaker import CircuitBreaker
from datetime import timedelta
from tenacity import retry, stop_after_attempt, retry_if_exception_type, wait_exponential_jitter

from exchange.exceptions import UnavailableServiceError

binance_breaker = CircuitBreaker(fail_max=3, timeout_duration=timedelta(seconds=15))


class BinancePriceService:

    BASE_URL = "https://api.binance.com/api/v3/ticker/price"
    SYMBOLS_STR = '["BTCUSDT","ETHUSDT","SOLUSDT"]'

    @binance_breaker
    @retry(
        stop=stop_after_attempt(2),
        wait=wait_exponential_jitter(1, max=5),
        retry=retry_if_exception_type(httpx.RequestError),
        reraise=True
    )
    async def get_prices(self) -> dict:
        prices = {}

        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.get(self.BASE_URL, params={"symbols": self.SYMBOLS_STR})
            if response.status_code != 200:
                raise UnavailableServiceError('Binance')

            data = response.json()
            for item in data:
                prices[item["symbol"]] = float(item["price"])

        return prices