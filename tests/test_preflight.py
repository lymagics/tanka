from hamcrest import assert_that, is_

from tanka.body import Empty
from tanka.cors import Preflight
from tanka.headers import Headers
from tanka.method import Get, Options
from tanka.request import Request


def test_recognizes_options_with_cors_headers():
    assert_that(
        Preflight(
            Request(
                Options(),
                "/api",
                Headers(
                    {
                        "origin": "https://a.example",
                        "access-control-request-method": "PUT",
                    }
                ),
                Empty(),
            )
        ).present(),
        is_(True),
        "Preflight must recognize OPTIONS with origin and requested method",
    )


def test_ignores_options_without_requested_method():
    assert_that(
        Preflight(
            Request(
                Options(),
                "/",
                Headers({"origin": "https://b.example"}),
                Empty(),
            )
        ).present(),
        is_(False),
        "Preflight must ignore OPTIONS lacking the requested method header",
    )


def test_ignores_other_methods():
    assert_that(
        Preflight(
            Request(
                Get(),
                "/",
                Headers(
                    {
                        "origin": "https://c.example",
                        "access-control-request-method": "GET",
                    }
                ),
                Empty(),
            )
        ).present(),
        is_(False),
        "Preflight must ignore methods other than OPTIONS",
    )
