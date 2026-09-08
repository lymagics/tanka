from hamcrest import assert_that, contains_string, empty, equal_to

from tanka.application import ErrorPage
from tanka.body import Body


def test_carries_status():
    assert_that(
        ErrorPage(404).status(),
        equal_to(404),
        "ErrorPage must carry its status",
    )


async def test_names_error_in_html():
    assert_that(
        await Body.Smart(ErrorPage(502).body()).text(),
        contains_string("<h1>Bad Gateway</h1>"),
        "ErrorPage must show the status phrase",
    )


def test_has_no_extra_headers():
    assert_that(
        list(ErrorPage(500).headers()),
        empty(),
        "ErrorPage must not add headers",
    )
