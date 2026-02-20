from src.app.use_cases.get_exchange import GetExchangeUseCase


class UpdateExchangeUseCase:

    def __init__(self, get_use_case: GetExchangeUseCase):
        self.get_use_case = get_use_case


    async def execute(self, exchange_name: str):
        return await self.get_use_case.execute(exchange_name)
