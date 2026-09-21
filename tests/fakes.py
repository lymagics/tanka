import asyncio

from tanka.abort import Abort
from tanka.application import Log
from tanka.auth import IdentitySource
from tanka.body import Json, Text
from tanka.catch import Fallback
from tanka.endpoint import Endpoint
from tanka.identity import Identity
from tanka.request import Request
from tanka.response import Reply, Response
from tanka.templates import Templates


class Fixed(Endpoint):
    def __init__(self, reply: Reply):
        self.reply = reply

    async def response(self, request: Request) -> Reply:
        return self.reply


class Failing(Endpoint):
    def __init__(self, error: Exception):
        self.error = error

    async def response(self, request: Request) -> Reply:
        raise self.error


class Echo(Endpoint):
    async def response(self, request: Request) -> Reply:
        return Response(
            200,
            Json(
                {
                    "method": request.method().names(),
                    "path": str(request.target().path()),
                    "query": str(request.target().query()),
                    "roles": request.identity().roles(),
                    "body": await request.body().text(),
                }
            ),
        )


class Complaint(Fallback):
    async def response(self, request: Request, error: Abort) -> Reply:
        return Response(error.status(), Text(str(error)))


class Known(IdentitySource):
    def __init__(self, identity: Identity):
        self.identity_ = identity

    async def identity(self, request: Request) -> Identity:
        return self.identity_


class Notebook(Log):
    def __init__(self, lines: list[str]):
        self.lines = lines

    def write(self, message: str) -> None:
        self.lines.append(message)


class Braces(Templates):
    async def markup(self, name: str, values: dict) -> str:
        return name.format(**values)


class Tally(dict):
    def __init__(self, content: dict, hits: list[int]):
        super().__init__(content)
        self.hits = hits

    def __iter__(self):
        return super().__iter__()

    def keys(self):
        self.hits.append(1)
        return super().keys()


class Record:
    def __init__(self, fields: dict):
        self.fields = fields

    async def json(self) -> dict:
        return self.fields


class Sheet:
    def __init__(self, cells: dict):
        self.cells = cells

    def json(self) -> dict:
        return self.cells


class Sleepy(Endpoint):
    def __init__(self, reply: Reply, seconds: float):
        self.reply = reply
        self.seconds = seconds

    async def response(self, request: Request) -> Reply:
        await asyncio.sleep(self.seconds)
        return self.reply
