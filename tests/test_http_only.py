from hamcrest import assert_that, equal_to

from tanka.cookies import HttpOnly


def test_prints_http_only_flag():
    assert_that(
        HttpOnly().text(),
        equal_to("HttpOnly"),
        "HttpOnly must print the HttpOnly flag",
    )
