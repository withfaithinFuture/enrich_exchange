import os

import httpx
import ujson
from aiobreaker import CircuitBreaker
from datetime import timedelta
from tenacity import retry, stop_after_attempt, retry_if_exception_type, wait_exponential_jitter
from src.exchange.exceptions import UnavailableServiceError, Server500Error


binance_breaker = CircuitBreaker(fail_max=3, timeout_duration=timedelta(seconds=15))


class BinancePriceService:

    BASE_URL = os.getenv('BASE_BINANCE_URL')
    SYMBOLS_STR = os.getenv('SYMBOLS_STR')

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=15)


    @binance_breaker
    @retry(
        stop=stop_after_attempt(2),
        wait=wait_exponential_jitter(1, max=5),
        retry=retry_if_exception_type(UnavailableServiceError),
        reraise=True
    )
    async def get_prices(self) -> dict:
        prices = {}

        try:
            response = await self.client.get(self.BASE_URL, params={"symbols": self.SYMBOLS_STR})

            data = ujson.loads(response.text)
            for item in data:
                prices[item["symbol"]] = float(item["price"])

            return prices

        except Exception as e:
            raise UnavailableServiceError(service_name="Binance")