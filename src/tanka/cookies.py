from abc import ABC, abstractmethod
from collections.abc import Iterator


class Cookies:
    def __init__(self, text: str):
        self.text = text

    def cookie(self, name: str) -> str:
        values = [value for label, value in self if label == name]
        if not values:
            raise Exception(f"Cookie '{name}' is absent")
        return values[0]

    def __iter__(self) -> Iterator[tuple[str, str]]:
        for part in self.text.split(";"):
            name, separator, value = part.strip().partition("=")
            if separator:
                yield name.strip(), value.strip().strip('"')


class Attribute(ABC):
    @abstractmethod
    def text(self) -> str:
        pass


class HttpOnly(Attribute):
    def text(self) -> str:
        return "HttpOnly"


class Secure(Attribute):
    def text(self) -> str:
        return "Secure"


class SameSite(Attribute):
    def __init__(self, policy: str):
        self.policy = policy

    def text(self) -> str:
        return f"SameSite={self.policy}"


class Domain(Attribute):
    def __init__(self, name: str):
        self.name = name

    def text(self) -> str:
        return f"Domain={self.name}"


class CookiePath(Attribute):
    def __init__(self, prefix: str):
        self.prefix = prefix

    def text(self) -> str:
        return f"Path={self.prefix}"


class Lifetime(Attribute):
    def __init__(self, seconds: int):
        self.seconds = seconds

    def text(self) -> str:
        return f"Max-Age={self.seconds}"


class SetCookie(ABC):
    @abstractmethod
    def text(self) -> str:
        pass


class Cookie(SetCookie):
    def __init__(self, name: str, value: str, *attributes: Attribute):
        self.name = name
        self.value = value
        self.attributes = attributes

    def text(self) -> str:
        return "; ".join(
            [
                f"{self.name}={self.value}",
                *[attribute.text() for attribute in self.attributes],
            ]
        )


class ForgetCookie(SetCookie):
    def __init__(self, name: str, *attributes: Attribute):
        self.name = name
        self.attributes = attributes

    def text(self) -> str:
        return Cookie(self.name, "", Lifetime(0), *self.attributes).text()
