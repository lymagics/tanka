from hamcrest import assert_that, empty, equal_to

from tanka.body import Empty
from tanka.cors import AllowMethods
from tanka.headers import Headers
from tanka.method import Delete, Get, Options, Post
from tanka.request import Request


def test_lists_methods_on_preflight():
    assert_that(
        AllowMethods(Get(), Post(), Delete())
        .headers(
            Request(
                Options(),
                "/",
                Headers(
                    {
                        "origin": "https://m.example",
                        "access-control-request-method": "DELETE",
                    }
                ),
                Empty(),
            )
        )
        .header("access-control-allow-methods"),
        equal_to("GET, POST, DELETE"),
        "AllowMethods must list allowed methods on preflight",
    )


def test_stays_silent_on_actual_request():
    assert_that(
        list(
            AllowMethods(Get()).headers(
                Request(
                    Get(),
                    "/",
                    Headers({"origin": "https://m.example"}),
                    Empty(),
                )
            )
        ),
        empty(),
        "AllowMethods must add nothing to an actual request",
    )
