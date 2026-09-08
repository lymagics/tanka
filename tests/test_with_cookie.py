from hamcrest import assert_that, contains_exactly, equal_to

from tanka.body import Body, Text
from tanka.cookies import Cookie, ForgetCookie, HttpOnly
from tanka.response import Redirect, Response, WithCookie


def test_sets_cookie_header():
    assert_that(
        WithCookie(Response(Text("")), Cookie("sid", "abc", HttpOnly()))
        .headers()
        .header("set-cookie"),
        equal_to("sid=abc; HttpOnly"),
        "WithCookie must add a set-cookie header",
    )


def test_stacks_multiple_cookies():
    assert_that(
        WithCookie(
            WithCookie(Response(Text("")), Cookie("a", "1")),
            ForgetCookie("b"),
        )
        .headers()
        .values("set-cookie"),
        contains_exactly("a=1", "b=; Max-Age=0"),
        "WithCookie must keep set-cookie headers of the origin",
    )


def test_keeps_status_of_origin():
    assert_that(
        WithCookie(Redirect("/next"), Cookie("k", "v")).status(),
        equal_to(302),
        "WithCookie must keep the status of the origin",
    )


async def test_keeps_body_of_origin():
    assert_that(
        await Body.Smart(
            WithCookie(Response(Text("origin")), Cookie("k", "v")).body()
        ).text(),
        equal_to("origin"),
        "WithCookie must keep the body of the origin",
    )
