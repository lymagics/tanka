from hamcrest import assert_that, contains_exactly, equal_to

from tanka.body import Body, Text
from tanka.headers import Headers
from tanka.response import Response, WithHeaders


def test_appends_headers_after_original():
    assert_that(
        list(
            WithHeaders(
                Response(200, Headers({"a": "1"}), Text("")),
                Headers({"b": "2"}),
            ).headers()
        ),
        contains_exactly(("a", "1"), ("b", "2")),
        "WithHeaders must append extra headers after the original ones",
    )


def test_keeps_status():
    assert_that(
        WithHeaders(Response(418, Text("")), Headers()).status(),
        equal_to(418),
        "WithHeaders must keep the original status",
    )


async def test_keeps_body():
    assert_that(
        await Body.Smart(
            WithHeaders(Response(Text("same")), Headers()).body()
        ).text(),
        equal_to("same"),
        "WithHeaders must keep the original body",
    )
