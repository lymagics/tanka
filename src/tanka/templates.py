import inspect
from abc import ABC, abstractmethod
from typing import Any, Protocol, runtime_checkable

from tanka.body import Html


class Templates(ABC):
    @abstractmethod
    async def markup(self, name: str, values: dict) -> str:
        pass


@runtime_checkable
class JsonReadable(Protocol):
    async def json(self) -> dict: ...


class Pair:
    def __init__(self, name: str, value: Any):
        self.name = name
        self.value = value

    async def entry(self) -> tuple[str, Any]:
        found = self.value
        readable = isinstance(
            found, JsonReadable
        ) and inspect.iscoroutinefunction(found.json)
        if readable:
            found = await found.json()
        return self.name, found


class Context:
    def __init__(self, *pairs: Pair):
        self.pairs = pairs

    async def values(self) -> dict:
        return dict([await pair.entry() for pair in self.pairs])


class Template:
    def __init__(self, templates: Templates, name: str):
        self.templates = templates
        self.name = name

    async def html(self, context: Context) -> Html:
        return Html(
            await self.templates.markup(self.name, await context.values())
        )
