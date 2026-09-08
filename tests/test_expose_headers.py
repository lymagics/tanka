from hamcrest import assert_that, empty, equal_to

from tanka.body import Empty
from tanka.cors import ExposeHeaders
from tanka.headers import Headers
from tanka.method import Get, Options
from tanka.request import Request


def test_exposes_headers_on_actual_request():
    assert_that(
        ExposeHeaders("X-Total", "X-Page")
        .headers(Request(Get(), "/", Headers(), Empty()))
        .header("access-control-expose-headers"),
        equal_to("X-Total, X-Page"),
        "ExposeHeaders must list exposed headers on an actual request",
    )


def test_stays_silent_on_preflight():
    assert_that(
        list(
            ExposeHeaders("X-Total").headers(
                Request(
                    Options(),
                    "/",
                    Headers(
                        {
                            "origin": "https://e.example",
                            "access-control-request-method": "GET",
                        }
                    ),
                    Empty(),
                )
            )
        ),
        empty(),
        "ExposeHeaders must add nothing to a preflight",
    )
