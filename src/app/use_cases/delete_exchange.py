class DeleteExchangeUseCase:

    def __init__(self, repo):
        self.repo = repo


    async def execute(self, exchange_name: str):
        await self.repo.delete_by_name(exchange_name)

