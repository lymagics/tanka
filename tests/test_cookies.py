from hamcrest import assert_that, calling, contains_exactly, equal_to, raises

from tanka.cookies import Cookies


def test_reads_named_cookie():
    assert_that(
        Cookies("theme=dark; session=xyz").cookie("session"),
        equal_to("xyz"),
        "Cookies must find a cookie by name",
    )


def test_strips_quotes_around_value():
    assert_that(
        Cookies('token="a b"').cookie("token"),
        equal_to("a b"),
        "Cookies must strip double quotes around a value",
    )


def test_fails_on_absent_cookie():
    assert_that(
        calling(Cookies("one=1").cookie).with_args("two"),
        raises(Exception, "absent"),
        "Cookies must fail fast on a missing cookie",
    )


def test_ignores_parts_without_equals_sign():
    assert_that(
        list(Cookies("garbage; k=v")),
        contains_exactly(("k", "v")),
        "Cookies must skip malformed parts",
    )
