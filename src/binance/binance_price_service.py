import httpx
from aiobreaker import CircuitBreaker
from datetime import timedelta


binance_breaker = CircuitBreaker(fail_max=3, timeout_duration=timedelta(seconds=15))


class BinancePriceService:

    BASE_URL = "https://api.binance.com/api/v3/ticker/price_LFSLDDLFSLF"
    SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]

    @binance_breaker
    async def get_prices(self) -> dict:
        prices = {}

        async with httpx.AsyncClient(timeout=15) as client:
            responce = await client.get(self.BASE_URL, params={"symbol": self.SYMBOLS})
            responce.raise_for_status()

            data = responce.json()
            for item in data:
                prices[item["symbol"]] = float(item["price"])

        return prices