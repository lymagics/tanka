from hamcrest import assert_that, contains_exactly, equal_to

from tanka.body import Raw


async def test_yields_data_as_single_chunk():
    assert_that(
        [chunk async for chunk in Raw(b"\x01\x02\x03", "x/y").chunks()],
        contains_exactly(b"\x01\x02\x03"),
        "Raw body must yield its data as one chunk",
    )


def test_declares_length_of_data():
    assert_that(
        Raw(b"12345", "text/plain").headers().header("content-length"),
        equal_to("5"),
        "Raw body must declare the byte length of the data",
    )


def test_declares_given_mime():
    assert_that(
        Raw(b"", "image/png").headers().header("content-type"),
        equal_to("image/png"),
        "Raw body must declare the given content type",
    )
