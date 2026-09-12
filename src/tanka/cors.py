from abc import ABC, abstractmethod

from tanka.body import Empty
from tanka.endpoint import Endpoint
from tanka.headers import Headers
from tanka.method import Method
from tanka.request import Request
from tanka.response import Reply, Response, WithHeaders


class Preflight:
    def __init__(self, request: Request):
        self.request = request

    def present(self) -> bool:
        return (
            "OPTIONS" in self.request.method().names()
            and bool(self.request.headers().values("origin"))
            and bool(
                self.request.headers().values("access-control-request-method")
            )
        )


class Policy(ABC):
    @abstractmethod
    def headers(self, request: Request) -> Headers:
        pass


class AllowOrigins(Policy):
    def __init__(self, *origins: str):
        self.origins = origins

    def headers(self, request: Request) -> Headers:
        origin = "".join(request.headers().values("origin")[:1])
        if origin and "*" in self.origins:
            result = Headers({"access-control-allow-origin": "*"})
        elif origin in self.origins:
            result = Headers(
                {"access-control-allow-origin": origin, "vary": "Origin"}
            )
        else:
            result = Headers()
        return result


class AllowMethods(Policy):
    def __init__(self, *methods: Method):
        self.methods = methods

    def headers(self, request: Request) -> Headers:
        names = [name for method in self.methods for name in method.names()]
        return (
            Headers({"access-control-allow-methods": ", ".join(names)})
            if Preflight(request).present()
            else Headers()
        )


class AllowHeaders(Policy):
    def __init__(self, *names: str):
        self.names = names

    def headers(self, request: Request) -> Headers:
        return (
            Headers({"access-control-allow-headers": ", ".join(self.names)})
            if Preflight(request).present()
            else Headers()
        )


class AllowCredentials(Policy):
    def headers(self, request: Request) -> Headers:
        return Headers({"access-control-allow-credentials": "true"})


class ExposeHeaders(Policy):
    def __init__(self, *names: str):
        self.names = names

    def headers(self, request: Request) -> Headers:
        return (
            Headers()
            if Preflight(request).present()
            else Headers(
                {"access-control-expose-headers": ", ".join(self.names)}
            )
        )


class MaxAge(Policy):
    def __init__(self, seconds: int):
        self.seconds = seconds

    def headers(self, request: Request) -> Headers:
        return (
            Headers({"access-control-max-age": str(self.seconds)})
            if Preflight(request).present()
            else Headers()
        )


class Cors(Endpoint):
    def __init__(self, origin: Endpoint, *policies: Policy):
        self.origin = origin
        self.policies = policies

    async def response(self, request: Request) -> Reply:
        if Preflight(request).present():
            result = Response(204, self._headers(request), Empty())
        else:
            result = WithHeaders(
                await self.origin.response(request),
                self._headers(request),
            )
        return result

    def _headers(self, request: Request) -> Headers:
        result = Headers(
            [
                pair
                for policy in self.policies
                for pair in policy.headers(request)
            ]
        )
        if "*" in result.values(
            "access-control-allow-origin"
        ) and "true" in result.values("access-control-allow-credentials"):
            raise Exception(
                "Browsers reject a wildcard origin together with credentials;"
                " list the allowed origins explicitly instead of '*'"
            )
        return result
