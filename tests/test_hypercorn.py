import asyncio
import socket

import httpx
import pytest
from hamcrest import assert_that, equal_to

from fakes import Fixed
from tanka.application import Silence, Tanka
from tanka.body import Text
from tanka.response import Response
from tanka.server import Hypercorn


def free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


async def fetched(url: str) -> str:
    async with httpx.AsyncClient() as http:
        for _ in range(100):
            try:
                return (await http.get(url)).text
            except httpx.TransportError:
                await asyncio.sleep(0.1)
    raise Exception(f"Server at {url} never answered")


@pytest.mark.deep
async def test_serves_application_over_http():
    port = free_port()
    task = asyncio.create_task(
        Tanka(Fixed(Response(Text("from hypercorn"))), Silence()).run(
            Hypercorn("127.0.0.1", port)
        )
    )
    try:
        text = await asyncio.wait_for(
            fetched(f"http://127.0.0.1:{port}/"), timeout=15
        )
    finally:
        task.cancel()
        await asyncio.wait([task], timeout=5)
    assert_that(
        text,
        equal_to("from hypercorn"),
        "Hypercorn must serve the application on the given port",
    )
