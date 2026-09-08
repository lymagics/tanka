from hamcrest import assert_that, contains_exactly, equal_to

from tanka.body import Text


async def test_encodes_text_as_utf8():
    assert_that(
        [chunk async for chunk in Text("żółw").chunks()],
        contains_exactly("żółw".encode()),
        "Text body must encode its text as UTF-8",
    )


def test_declares_plain_text_type():
    assert_that(
        Text("hello").headers().header("content-type"),
        equal_to("text/plain; charset=utf-8"),
        "Text body must declare a plain text content type",
    )


def test_counts_bytes_not_characters():
    assert_that(
        Text("€").headers().header("content-length"),
        equal_to("3"),
        "Text body must declare the encoded length",
    )
