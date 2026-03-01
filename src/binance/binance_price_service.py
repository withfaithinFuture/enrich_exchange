import httpx
import ujson
from aiobreaker import CircuitBreaker
from datetime import timedelta
from tenacity import retry, stop_after_attempt, retry_if_exception_type, wait_exponential_jitter
from src.exchange.exceptions import UnavailableServiceError, Server500Error


binance_breaker = CircuitBreaker(fail_max=3, timeout_duration=timedelta(seconds=15))


class BinancePriceService:

    BASE_URL = "https://api.binance.com/api/v3/ticker/price"
    SYMBOLS_STR = '["BTCUSDT","ETHUSDT","SOLUSDT"]'

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=15)


    @binance_breaker
    @retry(
        stop=stop_after_attempt(2),
        wait=wait_exponential_jitter(1, max=5),
        retry=retry_if_exception_type((httpx.RequestError, Server500Error)),
        reraise=True
    )
    async def get_prices(self) -> dict:
        prices = {}

        response = await self.client.get(self.BASE_URL, params={"symbols": self.SYMBOLS_STR})

        if response.status_code >= 500:
            raise Server500Error(service_name="Binance", status_code=response.status_code)

        elif response.status_code >= 400:
            raise UnavailableServiceError(service_name="Binance")

        data = ujson.loads(response.text)
        for item in data:
            prices[item["symbol"]] = float(item["price"])

        return prices