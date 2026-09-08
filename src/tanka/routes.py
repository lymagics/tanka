from abc import abstractmethod

from parse import parse

from tanka.abort import Abort
from tanka.endpoint import Endpoint
from tanka.method import Method
from tanka.request import Request
from tanka.response import Reply
from tanka.target import Path, Target


class Rule(Endpoint):
    @abstractmethod
    def matches(self, request: Request) -> bool:
        pass


class Route(Rule):
    def __init__(self, method: Method, pattern: str, endpoint: Endpoint):
        self.method = method
        self.pattern = pattern
        self.endpoint = endpoint

    def matches(self, request: Request) -> bool:
        allowed = set(self.method.names()) & set(request.method().names())
        return bool(allowed) and self._parsed(request) is not None

    async def response(self, request: Request) -> Reply:
        return await self.endpoint.response(
            Request(
                request.method(),
                Target(
                    Path(str(request.target().path()), self.pattern),
                    request.target().query(),
                ),
                request.headers(),
                request.body(),
                request.identity(),
            )
        )

    def _parsed(self, request: Request) -> object:
        return parse(
            self.pattern,
            str(request.target().path()),
            case_sensitive=True,
        )


class Routes(Rule):
    def __init__(self, *rules: Rule):
        self.rules = rules

    def matches(self, request: Request) -> bool:
        return any(rule.matches(request) for rule in self.rules)

    async def response(self, request: Request) -> Reply:
        for rule in self.rules:
            if rule.matches(request):
                return await rule.response(request)
        raise Abort(
            404,
            "No route matches "
            f"{' '.join(request.method().names())} {request.target()}",
        )


class Mount(Rule):
    def __init__(self, prefix: str, endpoint: Endpoint):
        self.prefix = prefix
        self.endpoint = endpoint

    def matches(self, request: Request) -> bool:
        path = str(request.target().path())
        return path == self.prefix or path.startswith(f"{self.prefix}/")

    async def response(self, request: Request) -> Reply:
        return await self.endpoint.response(
            Request(
                request.method(),
                Target(
                    Path(str(request.target().path())[len(self.prefix) :]),
                    request.target().query(),
                ),
                request.headers(),
                request.body(),
                request.identity(),
            )
        )
