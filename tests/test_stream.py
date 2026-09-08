from hamcrest import assert_that, contains_exactly, empty, equal_to

from tanka.body import Stream


async def pieces():
    yield b"one"
    yield b""
    yield b"two"


async def test_relays_chunks_from_source():
    assert_that(
        [chunk async for chunk in Stream(pieces(), "text/plain").chunks()],
        contains_exactly(b"one", b"", b"two"),
        "Stream body must relay every chunk from the source",
    )


def test_declares_no_length():
    assert_that(
        Stream(pieces(), "video/mp4").headers().values("content-length"),
        empty(),
        "Stream body must not declare a content length",
    )


def test_declares_given_mime():
    assert_that(
        Stream(pieces(), "video/mp4").headers().header("content-type"),
        equal_to("video/mp4"),
        "Stream body must declare the given content type",
    )
