import httpx


class BinancePriceService:

    BASE_URL = "https://api.binance.com/api/v3/ticker/price"
    SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]

    async def get_prices(self) -> dict:
        prices = {}

        async with httpx.AsyncClient(timeout=15) as client:
            for symbol in self.SYMBOLS:
                response = await client.get(self.BASE_URL, params={"symbol": symbol})

                data = response.json()

                prices[symbol] = float(data["price"])

        return prices