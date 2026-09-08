from collections.abc import AsyncIterator, Awaitable, Callable

from tanka.body import Body
from tanka.endpoint import Endpoint
from tanka.headers import Headers
from tanka.method import Verb
from tanka.request import Request
from tanka.response import Reply
from tanka.target import Path, Query, Target


class AsgiBody(Body):
    def __init__(
        self,
        receive: Callable[[], Awaitable[dict]],
        headers: Headers,
    ):
        self.receive = receive
        self.fields = headers
        self.drained = False

    def headers(self) -> Headers:
        return Headers(
            [
                (name, value)
                for name, value in self.fields
                if name.lower() in ("content-type", "content-length")
            ]
        )

    async def chunks(self) -> AsyncIterator[bytes]:
        if self.drained:
            raise Exception("Request body has already been consumed")
        self.drained = True
        more = True
        while more:
            message = await self.receive()
            if message["type"] == "http.disconnect":
                raise Exception("Client disconnected before the body ended")
            more = message.get("more_body", False)
            yield message.get("body", b"")


class Asgi:
    def __init__(self, endpoint: Endpoint):
        self.endpoint = endpoint

    async def __call__(
        self,
        scope: dict,
        receive: Callable[[], Awaitable[dict]],
        send: Callable[[dict], Awaitable[None]],
    ) -> None:
        if scope["type"] == "lifespan":
            await self._lifespan(receive, send)
        elif scope["type"] == "http":
            await self._http(scope, receive, send)
        else:
            raise Exception(f"ASGI scope '{scope['type']}' is not supported")

    async def _lifespan(
        self,
        receive: Callable[[], Awaitable[dict]],
        send: Callable[[dict], Awaitable[None]],
    ) -> None:
        running = True
        while running:
            message = await receive()
            if message["type"] == "lifespan.startup":
                await send({"type": "lifespan.startup.complete"})
            elif message["type"] == "lifespan.shutdown":
                await send({"type": "lifespan.shutdown.complete"})
                running = False

    async def _http(
        self,
        scope: dict,
        receive: Callable[[], Awaitable[dict]],
        send: Callable[[dict], Awaitable[None]],
    ) -> None:
        headers = Headers(
            [
                (name.decode("latin-1"), value.decode("latin-1"))
                for name, value in scope["headers"]
            ]
        )
        reply = await self.endpoint.response(
            Request(
                Verb(scope["method"]),
                Target(
                    Path(scope["path"]),
                    Query(scope.get("query_string", b"").decode("latin-1")),
                ),
                headers,
                AsgiBody(receive, headers),
            )
        )
        await send(
            {
                "type": "http.response.start",
                "status": reply.status(),
                "headers": self._headers(reply),
            }
        )
        if scope["method"].upper() != "HEAD":
            async for chunk in reply.body().chunks():
                await send(
                    {
                        "type": "http.response.body",
                        "body": chunk,
                        "more_body": True,
                    }
                )
        await send({"type": "http.response.body", "body": b""})

    def _headers(self, reply: Reply) -> list[tuple[bytes, bytes]]:
        own = list(reply.headers())
        taken = {name.lower() for name, _ in own}
        bare = reply.status() < 200 or reply.status() in (204, 304)
        return [
            (name.lower().encode("latin-1"), value.encode("latin-1"))
            for name, value in [
                *[
                    pair
                    for pair in reply.body().headers()
                    if pair[0].lower() not in taken
                ],
                *own,
            ]
            if not (
                bare and name.lower() in ("content-length", "content-type")
            )
        ]
