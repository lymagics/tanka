from typing import Any
from urllib.parse import parse_qsl

from parse import parse
from plum import dispatch


class Path:
    @dispatch
    def __init__(self, text: str):
        self.__init__(text, "{}")

    @dispatch
    def __init__(self, text: str, pattern: str):
        self.text = text
        self.pattern = pattern

    def parameter(self, name: str) -> Any:
        found = parse(self.pattern, self.text, case_sensitive=True)
        if found is None:
            raise Exception(
                f"Path '{self.text}' does not match pattern '{self.pattern}'"
            )
        try:
            return found.named[name]
        except KeyError as error:
            raise Exception(
                f"Path parameter '{name}' is absent in '{self.text}'"
            ) from error

    def __str__(self) -> str:
        return self.text


class Query:
    def __init__(self, text: str):
        self.text = text

    def parameter(self, name: str) -> str:
        values = self.values(name)
        if not values:
            raise Exception(f"Query parameter '{name}' is absent")
        return values[0]

    def values(self, name: str) -> list[str]:
        return [
            value
            for label, value in parse_qsl(self.text, keep_blank_values=True)
            if label == name
        ]

    def __str__(self) -> str:
        return self.text


class Target:
    @dispatch
    def __init__(self, raw: str):
        self.__init__(
            Path(raw.partition("?")[0]),
            Query(raw.partition("?")[2]),
        )

    @dispatch
    def __init__(self, path: Path, query: Query):
        self.location = path
        self.search = query

    def path(self) -> Path:
        return self.location

    def query(self) -> Query:
        return self.search

    def __str__(self) -> str:
        text = str(self.search)
        return str(self.location) + (f"?{text}" if text else "")
