from hamcrest import assert_that, empty, equal_to

from tanka.body import Empty
from tanka.cors import AllowHeaders
from tanka.headers import Headers
from tanka.method import Options, Post
from tanka.request import Request


def test_lists_headers_on_preflight():
    assert_that(
        AllowHeaders("Content-Type", "X-Trace")
        .headers(
            Request(
                Options(),
                "/",
                Headers(
                    {
                        "origin": "https://h.example",
                        "access-control-request-method": "POST",
                    }
                ),
                Empty(),
            )
        )
        .header("access-control-allow-headers"),
        equal_to("Content-Type, X-Trace"),
        "AllowHeaders must list allowed headers on preflight",
    )


def test_stays_silent_on_actual_request():
    assert_that(
        list(
            AllowHeaders("X-Trace").headers(
                Request(
                    Post(),
                    "/",
                    Headers({"origin": "https://h.example"}),
                    Empty(),
                )
            )
        ),
        empty(),
        "AllowHeaders must add nothing to an actual request",
    )
