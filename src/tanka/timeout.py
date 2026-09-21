import asyncio

from tanka.abort import Abort
from tanka.endpoint import Endpoint
from tanka.request import Request
from tanka.response import Reply


class Timeout(Endpoint):
    def __init__(self, origin: Endpoint, seconds: float):
        self.origin = origin
        self.seconds = seconds

    async def response(self, request: Request) -> Reply:
        try:
            return await asyncio.wait_for(
                self.origin.response(request), self.seconds
            )
        except TimeoutError as error:
            raise Abort(
                504,
                f"Endpoint did not answer within {self.seconds} seconds",
            ) from error
