import asyncio

from hamcrest import (
    assert_that,
    calling,
    equal_to,
    has_property,
    raises,
)

from tanka.abort import Abort
from tanka.body import Body, Capped, Empty, Raw, Stream, Text


async def endless():
    yield "ж".encode() * 6
    raise Exception("Capped read past the oversized chunk")


async def drip():
    yield b"\x00"
    yield b""
    yield b"\xfe\xff"


async def test_passes_body_of_exactly_limit_size():
    assert_that(
        await Body.Smart(Capped(Raw(b"\x01\x02\x03", "a/b"), 3)).bytes(),
        equal_to(b"\x01\x02\x03"),
        "Capped body must pass a body that is exactly the limit size",
    )


async def test_passes_every_chunk_of_small_stream():
    assert_that(
        await Body.Smart(Capped(Stream(drip(), "x/drip"), 1024)).bytes(),
        equal_to(b"\x00\xfe\xff"),
        "Capped body must pass every chunk of a stream within the limit",
    )


async def test_passes_empty_body_under_zero_limit():
    assert_that(
        await Body.Smart(Capped(Empty(), 0)).bytes(),
        equal_to(b""),
        "Capped body must accept an empty body even with a zero limit",
    )


def test_aborts_with_content_too_large_one_byte_past_limit():
    assert_that(
        calling(asyncio.run).with_args(
            Body.Smart(Capped(Text("seven!!"), 6)).bytes()
        ),
        raises(Abort, matching=has_property("code", equal_to(413))),
        "Capped body must abort with 413 once a single byte is too many",
    )


def test_stops_reading_as_soon_as_limit_is_exceeded():
    assert_that(
        calling(asyncio.run).with_args(
            Body.Smart(Capped(Stream(endless(), "x/zh"), 11)).bytes()
        ),
        raises(Abort, "11 bytes"),
        "Capped body must abort before reading the chunk after the limit",
    )


def test_keeps_headers_of_origin():
    assert_that(
        Capped(Raw(b"\x07" * 9, "image/x-odd"), 2)
        .headers()
        .header("content-type"),
        equal_to("image/x-odd"),
        "Capped body must keep the headers of its origin",
    )
