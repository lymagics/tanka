from hamcrest import assert_that, empty, equal_to, has_item

from tanka.body import Empty
from tanka.cors import AllowOrigins
from tanka.headers import Headers
from tanka.method import Get
from tanka.request import Request


def test_echoes_listed_origin():
    assert_that(
        AllowOrigins("https://one.example", "https://two.example")
        .headers(
            Request(
                Get(), "/", Headers({"origin": "https://two.example"}), Empty()
            )
        )
        .header("access-control-allow-origin"),
        equal_to("https://two.example"),
        "AllowOrigins must echo a listed origin",
    )


def test_varies_on_origin_for_listed_origin():
    assert_that(
        AllowOrigins("https://v.example")
        .headers(
            Request(
                Get(), "/", Headers({"origin": "https://v.example"}), Empty()
            )
        )
        .header("vary"),
        equal_to("Origin"),
        "AllowOrigins must add a Vary header for a specific origin",
    )


def test_uses_wildcard_for_any_origin():
    assert_that(
        AllowOrigins("*")
        .headers(
            Request(
                Get(), "/", Headers({"origin": "https://any.example"}), Empty()
            )
        )
        .header("access-control-allow-origin"),
        equal_to("*"),
        "AllowOrigins must answer with a wildcard when configured so",
    )


def test_withholds_allow_origin_from_unlisted_origin():
    assert_that(
        AllowOrigins("https://ok.example")
        .headers(
            Request(
                Get(),
                "/",
                Headers({"origin": "https://evil.example"}),
                Empty(),
            )
        )
        .values("access-control-allow-origin"),
        empty(),
        "AllowOrigins must not allow an unlisted origin",
    )


def test_varies_on_origin_for_unlisted_origin():
    assert_that(
        AllowOrigins("https://shelf.example")
        .headers(
            Request(
                Get(),
                "/books?page=-1",
                Headers({"origin": "https://stranger.example:8443"}),
                Empty(),
            )
        )
        .values("vary"),
        has_item("Origin"),
        "AllowOrigins with listed origins must send Vary: Origin to an"
        " unlisted origin, or shared caches serve that reply to allowed"
        " origins",
    )


def test_stays_silent_without_origin():
    assert_that(
        list(
            AllowOrigins("*").headers(Request(Get(), "/", Headers(), Empty()))
        ),
        empty(),
        "AllowOrigins must add nothing to a same-origin request",
    )


def test_varies_on_origin_when_request_has_no_origin():
    assert_that(
        AllowOrigins("https://cache.example")
        .headers(Request(Get(), "/feed", Headers(), Empty()))
        .values("vary"),
        has_item("Origin"),
        "AllowOrigins with listed origins must send Vary: Origin even"
        " without an Origin header, or shared caches serve the reply"
        " without CORS headers to allowed origins",
    )
