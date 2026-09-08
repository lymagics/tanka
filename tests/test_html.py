from hamcrest import assert_that, contains_exactly, equal_to

from tanka.body import Html


async def test_encodes_markup():
    assert_that(
        [chunk async for chunk in Html("<p>hi</p>").chunks()],
        contains_exactly(b"<p>hi</p>"),
        "Html body must yield the encoded markup",
    )


def test_declares_html_type():
    assert_that(
        Html("<b>x</b>").headers().header("content-type"),
        equal_to("text/html; charset=utf-8"),
        "Html body must declare an HTML content type",
    )
