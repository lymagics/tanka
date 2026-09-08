import asyncio
import os
import shlex
import subprocess
import sys
from abc import ABC, abstractmethod
from collections.abc import Coroutine

from plum import dispatch

from tanka.asgi import Asgi


class Server(ABC):
    @abstractmethod
    async def serve(self, asgi: Asgi) -> None:
        pass


class Watch(ABC):
    @abstractmethod
    async def serve(self, program: Coroutine[None, None, None]) -> None:
        pass


class Once(Watch):
    async def serve(self, program: Coroutine[None, None, None]) -> None:
        await program


class Reload(Watch):
    async def serve(self, program: Coroutine[None, None, None]) -> None:
        if os.environ.get("TANKA_RELOAD") == "child":
            await program
        else:
            program.close()
            await asyncio.to_thread(self._watch)

    def _watch(self) -> None:
        from watchfiles import run_process

        os.environ["TANKA_RELOAD"] = "child"
        run_process(os.getcwd(), target=self._command(), target_type="command")

    def _command(self) -> str:
        parts = [sys.executable, *sys.argv]
        return (
            subprocess.list2cmdline(parts)
            if os.name == "nt"
            else shlex.join(parts)
        )


class Uvicorn(Server):
    @dispatch
    def __init__(self, host: str, port: int):
        self.__init__(host, port, Once())

    @dispatch
    def __init__(self, host: str, port: int, watch: Watch):
        self.host = host
        self.port = port
        self.watch = watch

    async def serve(self, asgi: Asgi) -> None:
        await self.watch.serve(self._served(asgi))

    async def _served(self, asgi: Asgi) -> None:
        import uvicorn

        await uvicorn.Server(
            uvicorn.Config(asgi, host=self.host, port=self.port),
        ).serve()


class Hypercorn(Server):
    @dispatch
    def __init__(self, host: str, port: int):
        self.__init__(host, port, Once())

    @dispatch
    def __init__(self, host: str, port: int, watch: Watch):
        self.host = host
        self.port = port
        self.watch = watch

    async def serve(self, asgi: Asgi) -> None:
        await self.watch.serve(self._served(asgi))

    async def _served(self, asgi: Asgi) -> None:
        from hypercorn.asyncio import serve
        from hypercorn.config import Config

        config = Config()
        config.bind = [f"{self.host}:{self.port}"]
        await serve(asgi, config)
