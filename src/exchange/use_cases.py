import uuid
from binance.binance_price_service import BinancePriceService
from exchange.exchange_entities import Exchange
from exchange.portfolio_interface import IExchangeRepo
from first_service.exchange_api_service import ExchangeApiService


class CreateExchangeUseCase:

    def __init__(self, repo: IExchangeRepo, exchange_api_service: ExchangeApiService, binance_service: BinancePriceService):
        self.repo = repo
        self.exchange_api = exchange_api_service
        self.binance_service = binance_service


    async def execute(self, exchange_name: str) -> Exchange | None:
        external_exchanges = await self.exchange_api.get_exchanges()
        external_exchange = None
        for exchange in external_exchanges:
            if exchange["exchange_name"] == exchange_name:
                external_exchange = exchange
                break

        if not external_exchange:
            return None

        prices = await self.binance_service.get_prices()

        local_exchange = Exchange(
            id=uuid.uuid4(),
            exchange_name=external_exchange["exchange_name"],
            work_in_russia=external_exchange["work_in_Russia"],
            volume=external_exchange["volume"],
            owner_first_name=external_exchange["owner"]["first_name"],
            owner_last_name=external_exchange["owner"]["last_name"],
            btc_price=prices.get("BTCUSDT"),
            eth_price=prices.get("ETHUSDT"),
            sol_price=prices.get("SOLUSDT")
        )

        await self.repo.create(local_exchange)

        return local_exchange



class GetExchangeUseCase:

    def __init__(self, repo: IExchangeRepo, exchange_api_service: ExchangeApiService, binance_service: BinancePriceService):
        self.repo = repo
        self.exchange_api = exchange_api_service
        self.binance_service = binance_service


    async def execute(self, exchange_name: str) -> Exchange | None:

        external_exchanges = await self.exchange_api.get_exchanges()
        external_exchange = None
        for exchange in external_exchanges:
            if exchange["exchange_name"] == exchange_name:
                external_exchange = exchange
                break

        if not external_exchange:
            await self.repo.delete_by_name(exchange_name)
            return None

        local_exchange = await self.repo.get_by_name(exchange_name)

        if not local_exchange:
            local_exchange = Exchange(
                id=uuid.uuid4(),
                exchange_name=external_exchange["exchange_name"],
                work_in_russia=external_exchange["work_in_Russia"],
                volume=external_exchange["volume"],
                owner_first_name=external_exchange["owner"]["first_name"],
                owner_last_name=external_exchange["owner"]["last_name"]
            )

            await self.repo.create(local_exchange)

        prices = await self.binance_service.get_prices()

        local_exchange.work_in_russia = external_exchange["work_in_Russia"]
        local_exchange.volume = external_exchange["volume"]
        local_exchange.owner_first_name = external_exchange["owner"]["first_name"]
        local_exchange.owner_last_name = external_exchange["owner"]["last_name"]
        local_exchange.btc_price = prices.get("BTCUSDT")
        local_exchange.eth_price = prices.get("ETHUSDT")
        local_exchange.sol_price = prices.get("SOLUSDT")

        await self.repo.update(local_exchange)

        return local_exchange



class UpdateExchangeUseCase:

    def __init__(self, get_use_case: GetExchangeUseCase):
        self.get_use_case = get_use_case


    async def execute(self, exchange_name: str):
        return await self.get_use_case.execute(exchange_name)



class DeleteExchangeUseCase:

    def __init__(self, repo):
        self.repo = repo


    async def execute(self, exchange_name: str):
        await self.repo.delete_by_name(exchange_name)