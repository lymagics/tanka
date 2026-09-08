import logging
import traceback
from abc import ABC, abstractmethod
from collections.abc import Awaitable

from plum import dispatch

from tanka.abort import Abort, Status
from tanka.asgi import Asgi
from tanka.body import Body, Html
from tanka.endpoint import Endpoint
from tanka.headers import Headers
from tanka.request import Request
from tanka.response import Reply
from tanka.server import Server, Uvicorn


class Log(ABC):
    @abstractmethod
    def write(self, message: str) -> None:
        pass


class Logging(Log):
    def __init__(self, name: str):
        self.name = name

    def write(self, message: str) -> None:
        logging.getLogger(self.name).error(message)


class Silence(Log):
    def write(self, message: str) -> None:
        pass


class ErrorPage(Reply):
    def __init__(self, code: int):
        self.code = code

    def status(self) -> int:
        return self.code

    def headers(self) -> Headers:
        return Headers()

    def body(self) -> Body:
        phrase = Status(self.code).phrase()
        return Html(
            "<!doctype html><html><head>"
            f"<title>{phrase}</title></head>"
            f"<body><h1>{phrase}</h1></body></html>"
        )


class Aborted(Endpoint):
    def __init__(self, origin: Endpoint):
        self.origin = origin

    async def response(self, request: Request) -> Reply:
        try:
            result = await self.origin.response(request)
        except Abort as error:
            result = ErrorPage(error.status())
        return result


class Failsafe(Endpoint):
    def __init__(self, origin: Endpoint, log: Log):
        self.origin = origin
        self.log = log

    async def response(self, request: Request) -> Reply:
        try:
            result = await self.origin.response(request)
        except Exception:
            self.log.write(traceback.format_exc())
            result = ErrorPage(500)
        return result


class Tanka:
    @dispatch
    def __init__(self, endpoint: Endpoint):
        self.__init__(endpoint, Logging("tanka"))

    @dispatch
    def __init__(self, endpoint: Endpoint, log: Log):
        self.endpoint = endpoint
        self.log = log

    def asgi(self) -> Asgi:
        return Asgi(Failsafe(Aborted(self.endpoint), self.log))

    @dispatch
    async def run(self) -> Awaitable[None]:
        await self.run(Uvicorn("127.0.0.1", 8000))

    @dispatch
    async def run(self, server: Server) -> Awaitable[None]:
        await server.serve(self.asgi())
