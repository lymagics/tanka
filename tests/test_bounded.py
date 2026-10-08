import asyncio

import httpx
from hamcrest import (
    assert_that,
    calling,
    equal_to,
    has_entry,
    has_property,
    raises,
)

from fakes import Echo, Fixed
from tanka.abort import Abort
from tanka.application import Silence, Tanka
from tanka.body import Body, Raw, Text
from tanka.bounded import Bounded
from tanka.headers import Headers
from tanka.identity import Principal
from tanka.method import Post, Put
from tanka.request import Request
from tanka.response import Response


async def test_passes_body_within_limit_to_origin():
    assert_that(
        await Body.Smart(
            (
                await Bounded(Echo(), 64).response(
                    Request(Post(), "/notes", Headers(), Text("épée"))
                )
            ).body()
        ).json(),
        has_entry("body", "épée"),
        "Bounded must pass a body within the limit to its origin",
    )


async def test_keeps_identity_of_request():
    assert_that(
        await Body.Smart(
            (
                await Bounded(Echo(), 500).response(
                    Request(
                        Put(),
                        "/vault",
                        Headers(),
                        Text("{}"),
                        Principal("u-9", "keeper"),
                    )
                )
            ).body()
        ).json(),
        has_entry("roles", ["keeper"]),
        "Bounded must keep the identity of the request it wraps",
    )


async def test_lets_origin_ignore_oversized_body():
    assert_that(
        (
            await Bounded(Fixed(Response(207, Text("ok"))), 1).response(
                Request(Post(), "/ping", Headers(), Raw(b"\xaa" * 99, "x/y"))
            )
        ).status(),
        equal_to(207),
        "Bounded must not abort when the origin never reads the body",
    )


def test_aborts_with_content_too_large_when_origin_reads_oversized_body():
    assert_that(
        calling(asyncio.run).with_args(
            Bounded(Echo(), 4).response(
                Request(Post(), "/upload", Headers(), Text("12345"))
            )
        ),
        raises(Abort, matching=has_property("code", equal_to(413))),
        "Bounded must abort with 413 when the origin reads too many bytes",
    )


async def test_serves_content_too_large_over_asgi():
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(
            app=Tanka(Bounded(Echo(), 16), Silence()).asgi()
        ),
        base_url="http://testserver",
    ) as http:
        assert_that(
            (
                await http.post("/photos", content=b"\x89PNG" + b"\x00" * 13)
            ).status_code,
            equal_to(413),
            "Bounded must answer 413 over ASGI for an oversized body",
        )
