from tanka.body import Capped
from tanka.endpoint import Endpoint
from tanka.request import Request
from tanka.response import Reply


class Bounded(Endpoint):
    def __init__(self, origin: Endpoint, limit: int):
        self.origin = origin
        self.limit = limit

    async def response(self, request: Request) -> Reply:
        return await self.origin.response(
            Request(
                request.method(),
                request.target(),
                request.headers(),
                Capped(request.body(), self.limit),
                request.identity(),
            )
        )
