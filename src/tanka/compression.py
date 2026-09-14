import re

from plum import dispatch

from tanka.body import Gzipped
from tanka.endpoint import Endpoint
from tanka.headers import Headers
from tanka.request import Request
from tanka.response import Reply, Response


class Compressed(Endpoint):
    @dispatch
    def __init__(self, origin: Endpoint):
        self.__init__(origin, 500)

    @dispatch
    def __init__(self, origin: Endpoint, minimum: int):
        self.origin = origin
        self.minimum = minimum

    async def response(self, request: Request) -> Reply:
        reply = await self.origin.response(request)
        return (
            Response(
                reply.status(),
                Headers(
                    [
                        *[
                            pair
                            for pair in reply.headers()
                            if pair[0].lower() != "content-length"
                        ],
                        ("vary", "accept-encoding"),
                    ]
                ),
                Gzipped(reply.body()),
            )
            if self._accepted(request)
            and not self._encoded(reply)
            and not self._small(reply)
            else reply
        )

    def _accepted(self, request: Request) -> bool:
        wanted = dict(
            self._preference(item)
            for value in request.headers().values("accept-encoding")
            for item in value.split(",")
        )
        return wanted.get("gzip", wanted.get("*", False))

    def _preference(self, item: str) -> tuple[str, bool]:
        name, *params = [part.strip().lower() for part in item.split(";")]
        return name, not any(
            re.fullmatch(r"q=0(\.0{1,3})?", param) for param in params
        )

    def _encoded(self, reply: Reply) -> bool:
        return bool(
            reply.headers().values("content-encoding")
            or reply.body().headers().values("content-encoding")
        )

    def _small(self, reply: Reply) -> bool:
        lengths = [
            *reply.headers().values("content-length"),
            *reply.body().headers().values("content-length"),
        ]
        return any(int(length) < self.minimum for length in lengths[:1])
