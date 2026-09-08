import json
from abc import ABC, abstractmethod
from collections.abc import Iterator
from urllib.parse import quote, unquote

from tanka.body import Body
from tanka.cookies import Cookie, CookiePath, Cookies, HttpOnly
from tanka.headers import Headers
from tanka.response import Reply, WithCookie


class Kind(ABC):
    @abstractmethod
    def name(self) -> str:
        pass


class Success(Kind):
    def name(self) -> str:
        return "success"


class Failure(Kind):
    def name(self) -> str:
        return "failure"


class Notice(Kind):
    def name(self) -> str:
        return "notice"


class Alert(Kind):
    def name(self) -> str:
        return "alert"


class Named(Kind):
    def __init__(self, name: str):
        self.label = name

    def name(self) -> str:
        return self.label


class Flash:
    def __init__(self, text: str, kind: Kind):
        self.message = text
        self.tone = kind

    def text(self) -> str:
        return self.message

    def kind(self) -> Kind:
        return self.tone


class WithFlash(Reply):
    def __init__(self, origin: Reply, flash: Flash):
        self.origin = origin
        self.flash = flash

    def status(self) -> int:
        return self.origin.status()

    def headers(self) -> Headers:
        return WithCookie(
            self.origin,
            Cookie(
                "flash",
                quote(
                    json.dumps(
                        {
                            "text": self.flash.text(),
                            "kind": self.flash.kind().name(),
                        }
                    )
                ),
                CookiePath("/"),
                HttpOnly(),
            ),
        ).headers()

    def body(self) -> Body:
        return self.origin.body()


class Flashes:
    def __init__(self, cookies: Cookies):
        self.cookies = cookies

    def __iter__(self) -> Iterator[Flash]:
        for name, value in self.cookies:
            if name == "flash":
                data = json.loads(unquote(value))
                yield Flash(data["text"], Named(data["kind"]))
