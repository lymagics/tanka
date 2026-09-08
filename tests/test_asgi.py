import asyncio

import httpx
from hamcrest import (
    assert_that,
    calling,
    contains_exactly,
    equal_to,
    has_entry,
    is_not,
    raises,
)

from fakes import Echo, Fixed
from tanka.asgi import Asgi
from tanka.body import Empty, Stream, Text
from tanka.headers import Headers
from tanka.response import Response


class Feed:
    def __init__(self, messages: list[dict]):
        self.messages = list(messages)

    async def __call__(self) -> dict:
        return self.messages.pop(0)


class Sink:
    def __init__(self, messages: list[dict]):
        self.messages = messages

    async def __call__(self, message: dict) -> None:
        self.messages.append(message)


async def pieces():
    yield b"first,"
    yield b"second"


def client(asgi: Asgi) -> httpx.AsyncClient:
    return httpx.AsyncClient(
        transport=httpx.ASGITransport(app=asgi),
        base_url="http://testserver",
    )


async def test_sends_status_of_reply():
    async with client(Asgi(Fixed(Response(202, Text("ok"))))) as http:
        assert_that(
            (await http.get("/")).status_code,
            equal_to(202),
            "Asgi must send the status of the reply",
        )


async def test_takes_content_type_from_body():
    async with client(Asgi(Fixed(Response(Text("plain"))))) as http:
        assert_that(
            (await http.get("/")).headers["content-type"],
            equal_to("text/plain; charset=utf-8"),
            "Asgi must merge body headers into the response",
        )


async def test_prefers_explicit_header_over_body_header():
    async with client(
        Asgi(
            Fixed(
                Response(
                    200,
                    Headers({"content-type": "text/markdown"}),
                    Text("# title"),
                )
            )
        )
    ) as http:
        assert_that(
            (await http.get("/")).headers["content-type"],
            equal_to("text/markdown"),
            "Asgi must let explicit headers override body headers",
        )


async def test_drops_content_length_for_no_content():
    async with client(Asgi(Fixed(Response(204, Empty())))) as http:
        assert_that(
            (await http.get("/")).headers,
            is_not(has_entry("content-length", "0")),
            "Asgi must not send content-length with 204",
        )


async def test_sends_no_body_for_head():
    async with client(Asgi(Fixed(Response(Text("hidden"))))) as http:
        assert_that(
            (await http.head("/")).content,
            equal_to(b""),
            "Asgi must omit the body for HEAD requests",
        )


async def test_streams_all_chunks():
    async with client(
        Asgi(Fixed(Response(Stream(pieces(), "text/csv"))))
    ) as http:
        assert_that(
            (await http.get("/")).text,
            equal_to("first,second"),
            "Asgi must stream every chunk of the body",
        )


async def test_passes_request_body_to_endpoint():
    async with client(Asgi(Echo())) as http:
        assert_that(
            (await http.post("/in", content=b"payload")).json(),
            has_entry("body", "payload"),
            "Asgi must expose the request body to the endpoint",
        )


async def test_passes_query_string_to_endpoint():
    async with client(Asgi(Echo())) as http:
        assert_that(
            (await http.get("/q?a=1&b=2")).json(),
            has_entry("query", "a=1&b=2"),
            "Asgi must expose the query string to the endpoint",
        )


async def test_completes_lifespan_handshake():
    sent: list[dict] = []
    await Asgi(Echo())(
        {"type": "lifespan"},
        Feed([{"type": "lifespan.startup"}, {"type": "lifespan.shutdown"}]),
        Sink(sent),
    )
    assert_that(
        [message["type"] for message in sent],
        contains_exactly(
            "lifespan.startup.complete", "lifespan.shutdown.complete"
        ),
        "Asgi must acknowledge startup and shutdown",
    )


def test_rejects_unknown_scope():
    assert_that(
        calling(asyncio.run).with_args(
            Asgi(Echo())({"type": "websocket"}, Feed([]), Sink([]))
        ),
        raises(Exception, "not supported"),
        "Asgi must reject scopes other than http and lifespan",
    )
