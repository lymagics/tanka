import hashlib

from plum import dispatch

from tanka.body import Body, Buffered, Empty
from tanka.endpoint import Endpoint
from tanka.headers import Headers
from tanka.request import Request
from tanka.response import Reply, Response


class Cached(Endpoint):
    @dispatch
    def __init__(self, origin: Endpoint):
        self.__init__(origin, "no-cache")

    @dispatch
    def __init__(self, origin: Endpoint, seconds: int):
        self.__init__(origin, f"max-age={seconds}")

    @dispatch
    def __init__(self, origin: Endpoint, control: str):
        self.origin = origin
        self.control = control

    async def response(self, request: Request) -> Reply:
        reply = await self.origin.response(request)
        return (
            await self._tagged(request, reply)
            if reply.status() == 200
            else reply
        )

    async def _tagged(self, request: Request, reply: Reply) -> Reply:
        data = await Body.Smart(reply.body()).bytes()
        tag = f'"{hashlib.blake2b(data, digest_size=16).hexdigest()}"'
        headers = Headers(
            [
                *reply.headers(),
                ("etag", tag),
                ("cache-control", self.control),
            ]
        )
        return (
            Response(304, headers, Empty())
            if self._held(request, tag)
            else Response(200, headers, Buffered(reply.body(), data))
        )

    def _held(self, request: Request, tag: str) -> bool:
        tags = [
            item.strip().removeprefix("W/")
            for value in request.headers().values("if-none-match")
            for item in value.split(",")
        ]
        return bool(
            {"GET", "HEAD"} & set(request.method().names())
            and ("*" in tags or tag in tags)
        )
