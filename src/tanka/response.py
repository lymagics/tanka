from abc import ABC, abstractmethod

from plum import dispatch

from tanka.body import Body, Empty
from tanka.cookies import SetCookie
from tanka.headers import Headers


class Reply(ABC):
    @abstractmethod
    def status(self) -> int:
        pass

    @abstractmethod
    def headers(self) -> Headers:
        pass

    @abstractmethod
    def body(self) -> Body:
        pass


class Response(Reply):
    @dispatch
    def __init__(self, body: Body):
        self.__init__(200, Headers(), body)

    @dispatch
    def __init__(self, status: int, body: Body):
        self.__init__(status, Headers(), body)

    @dispatch
    def __init__(self, status: int, headers: Headers, body: Body):
        self.code = status
        self.fields = headers
        self.payload = body

    def status(self) -> int:
        return self.code

    def headers(self) -> Headers:
        return self.fields

    def body(self) -> Body:
        return self.payload


class Redirect(Reply):
    @dispatch
    def __init__(self, location: str):
        self.__init__(location, 302)

    @dispatch
    def __init__(self, location: str, status: int):
        self.location = location
        self.code = status

    def status(self) -> int:
        return self.code

    def headers(self) -> Headers:
        return Headers({"location": self.location})

    def body(self) -> Body:
        return Empty()


class WithHeaders(Reply):
    def __init__(self, origin: Reply, headers: Headers):
        self.origin = origin
        self.extra = headers

    def status(self) -> int:
        return self.origin.status()

    def headers(self) -> Headers:
        return Headers([*self.origin.headers(), *self.extra])

    def body(self) -> Body:
        return self.origin.body()


class WithCookie(Reply):
    def __init__(self, origin: Reply, cookie: SetCookie):
        self.origin = origin
        self.cookie = cookie

    def status(self) -> int:
        return self.origin.status()

    def headers(self) -> Headers:
        return WithHeaders(
            self.origin,
            Headers({"set-cookie": self.cookie.text()}),
        ).headers()

    def body(self) -> Body:
        return self.origin.body()
