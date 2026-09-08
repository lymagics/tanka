from abc import ABC, abstractmethod
from types import EllipsisType

from plum import dispatch

from tanka.abort import Abort
from tanka.endpoint import Endpoint
from tanka.request import Request
from tanka.response import Reply


class Codes(ABC):
    @abstractmethod
    def matches(self, code: int) -> bool:
        pass


class Code(Codes):
    def __init__(self, value: int):
        self.value = value

    def matches(self, code: int) -> bool:
        return code == self.value


class Listed(Codes):
    def __init__(self, *values: int):
        self.values = values

    def matches(self, code: int) -> bool:
        return code in self.values


class Range(Codes):
    def __init__(self, start: int, end: int):
        self.start = start
        self.end = end

    def matches(self, code: int) -> bool:
        return self.start <= code <= self.end


class Every(Codes):
    def matches(self, code: int) -> bool:
        return True


class Fallback(ABC):
    @abstractmethod
    async def response(self, request: Request, error: Abort) -> Reply:
        pass


class Indifferent(Fallback):
    def __init__(self, endpoint: Endpoint):
        self.endpoint = endpoint

    async def response(self, request: Request, error: Abort) -> Reply:
        return await self.endpoint.response(request)


class On(Fallback):
    @dispatch
    def __init__(self, code: int, fallback: Endpoint | Fallback):
        self.__init__(Code(code), fallback)

    @dispatch
    def __init__(self, codes: tuple, fallback: Endpoint | Fallback):
        self.__init__(Listed(*codes), fallback)

    @dispatch
    def __init__(self, codes: EllipsisType, fallback: Endpoint | Fallback):
        self.__init__(Every(), fallback)

    @dispatch
    def __init__(self, codes: Codes, endpoint: Endpoint):
        self.__init__(codes, Indifferent(endpoint))

    @dispatch
    def __init__(self, codes: Codes, fallback: Fallback):
        self.codes = codes
        self.fallback = fallback

    def matches(self, code: int) -> bool:
        return self.codes.matches(code)

    async def response(self, request: Request, error: Abort) -> Reply:
        return await self.fallback.response(request, error)


class Catch(Endpoint):
    def __init__(self, origin: Endpoint, *fallbacks: On):
        self.origin = origin
        self.fallbacks = fallbacks

    async def response(self, request: Request) -> Reply:
        try:
            result = await self.origin.response(request)
        except Abort as error:
            result = await self._recovered(request, error.status(), error)
        except Exception as error:
            result = await self._recovered(request, 500, error)
        return result

    async def _recovered(
        self,
        request: Request,
        code: int,
        error: Exception,
    ) -> Reply:
        for fallback in self.fallbacks:
            if fallback.matches(code):
                return await fallback.response(
                    request,
                    Abort(code, str(error)),
                )
        raise error
