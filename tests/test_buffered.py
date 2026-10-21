from hamcrest import assert_that, contains_exactly, equal_to

from tanka.body import Buffered, Raw, Text


async def test_yields_given_data_as_single_chunk():
    assert_that(
        [
            chunk
            async for chunk in Buffered(Text("ignored"), b"\xff\x00").chunks()
        ],
        contains_exactly(b"\xff\x00"),
        "Buffered body must yield its data as one chunk",
    )


def test_declares_content_type_of_wrapped_body():
    assert_that(
        Buffered(Raw(b"wOF2", "font/woff2"), b"wOF2")
        .headers()
        .header("content-type"),
        equal_to("font/woff2"),
        "Buffered must declare the content type of the body it wraps",
    )
