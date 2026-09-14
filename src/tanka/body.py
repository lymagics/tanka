import asyncio
import json
import mimetypes
import os
from abc import ABC, abstractmethod
from collections.abc import AsyncIterable, AsyncIterator
from typing import Any

from tanka.headers import Headers


class Body(ABC):
    @abstractmethod
    def headers(self) -> Headers:
        pass

    @abstractmethod
    def chunks(self) -> AsyncIterator[bytes]:
        pass

    class Smart:
        def __init__(self, origin: "Body"):
            self.origin = origin

        def headers(self) -> Headers:
            return self.origin.headers()

        def chunks(self) -> AsyncIterator[bytes]:
            return self.origin.chunks()

        async def bytes(self) -> bytes:
            return b"".join([chunk async for chunk in self.origin.chunks()])

        async def text(self) -> str:
            return (await self.bytes()).decode(self._charset())

        async def json(self) -> Any:
            return json.loads(await self.text())

        def _charset(self) -> str:
            found = [
                part.strip()[8:].strip()
                for value in self.origin.headers().values("content-type")
                for part in value.split(";")
                if part.strip().lower().startswith("charset=")
            ]
            return next((name for name in found if name), "utf-8")


Body.register(Body.Smart)


class Empty(Body):
    def headers(self) -> Headers:
        return Headers({"content-length": "0"})

    async def chunks(self) -> AsyncIterator[bytes]:
        for chunk in ():
            yield chunk


class Raw(Body):
    def __init__(self, data: bytes, mime: str):
        self.data = data
        self.mime = mime

    def headers(self) -> Headers:
        return Headers(
            {
                "content-type": self.mime,
                "content-length": str(len(self.data)),
            }
        )

    async def chunks(self) -> AsyncIterator[bytes]:
        yield self.data


class Text(Body):
    def __init__(self, text: str):
        self.text = text

    def headers(self) -> Headers:
        return self._raw().headers()

    def chunks(self) -> AsyncIterator[bytes]:
        return self._raw().chunks()

    def _raw(self) -> Raw:
        return Raw(self.text.encode("utf-8"), "text/plain; charset=utf-8")


class Html(Body):
    def __init__(self, markup: str):
        self.markup = markup

    def headers(self) -> Headers:
        return self._raw().headers()

    def chunks(self) -> AsyncIterator[bytes]:
        return self._raw().chunks()

    def _raw(self) -> Raw:
        return Raw(self.markup.encode("utf-8"), "text/html; charset=utf-8")


class Json(Body):
    def __init__(self, value: Any):
        self.value = value

    def headers(self) -> Headers:
        return self._raw().headers()

    def chunks(self) -> AsyncIterator[bytes]:
        return self._raw().chunks()

    def _raw(self) -> Raw:
        return Raw(json.dumps(self.value).encode("utf-8"), "application/json")


class Stream(Body):
    def __init__(self, source: AsyncIterable[bytes], mime: str):
        self.source = source
        self.mime = mime

    def headers(self) -> Headers:
        return Headers({"content-type": self.mime})

    async def chunks(self) -> AsyncIterator[bytes]:
        async for chunk in self.source:
            yield chunk


class File(Body):
    def __init__(self, path: str):
        self.path = path

    def headers(self) -> Headers:
        try:
            size = os.path.getsize(self.path)
        except OSError as error:
            raise Exception(f"Can't read file '{self.path}'") from error
        return Headers(
            {
                "content-type": mimetypes.guess_type(self.path)[0]
                or "application/octet-stream",
                "content-length": str(size),
            }
        )

    async def chunks(self) -> AsyncIterator[bytes]:
        try:
            handle = open(self.path, "rb")
        except OSError as error:
            raise Exception(f"Can't open file '{self.path}'") from error
        with handle:
            while chunk := await asyncio.to_thread(handle.read, 65536):
                yield chunk
