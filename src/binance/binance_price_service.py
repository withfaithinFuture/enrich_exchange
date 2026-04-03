import httpx
import ujson
from aiobreaker import CircuitBreaker
from datetime import timedelta
from tenacity import retry, stop_after_attempt, retry_if_exception_type, wait_exponential_jitter
from src.exceptions import UnavailableServiceError
from src.binance.utils import check_status
from src.settings import settings


class BinancePriceService:

    BASE_URL = settings.BASE_URL
    SYMBOLS_STR = settings.SYMBOLS_STR
    SERVICE_NAME = settings.SERVICE_NAME
    SERVICE_TYPE = settings.SERVICE_TYPE

    breaker = CircuitBreaker(fail_max=3, timeout_duration=timedelta(seconds=15))

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=15)


    @breaker
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential_jitter(1, max=5),
        retry=retry_if_exception_type(UnavailableServiceError),
        reraise=True
    )
    async def get_prices(self) -> dict:
        prices = {}
        response = await self.client.get(self.BASE_URL)

        check_status(response=response, object_name=self.SERVICE_NAME, object_type=self.SERVICE_TYPE)

        data = ujson.loads(response.text)
        for item in data:
            prices[item["symbol"]] = float(item["price"])

        return prices