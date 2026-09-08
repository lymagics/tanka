from hamcrest import assert_that, contains_exactly, equal_to

from tanka.body import Empty
from tanka.headers import Headers
from tanka.method import Patch
from tanka.openapi import CoreRequest
from tanka.request import Request


def test_builds_host_url_from_host_header():
    assert_that(
        CoreRequest(
            Request(
                Patch(), "/", Headers({"host": "api.example:8443"}), Empty()
            ),
            b"",
        ).host_url,
        equal_to("http://api.example:8443"),
        "CoreRequest must build the host url from the host header",
    )


def test_defaults_host_to_localhost():
    assert_that(
        CoreRequest(Request(Patch(), "/", Headers(), Empty()), b"").host_url,
        equal_to("http://localhost"),
        "CoreRequest must default the host to localhost",
    )


def test_lower_cases_method():
    assert_that(
        CoreRequest(Request(Patch(), "/x", Headers(), Empty()), b"").method,
        equal_to("patch"),
        "CoreRequest must expose the method in lower case",
    )


def test_exposes_path():
    assert_that(
        CoreRequest(
            Request(Patch(), "/pets/3?x=1", Headers(), Empty()), b""
        ).path,
        equal_to("/pets/3"),
        "CoreRequest must expose the path without the query",
    )


def test_lists_query_values():
    assert_that(
        CoreRequest(
            Request(Patch(), "/?tag=a&tag=b", Headers(), Empty()), b""
        ).parameters.query.getlist("tag"),
        contains_exactly("a", "b"),
        "CoreRequest must expose repeated query values",
    )


def test_exposes_cookies():
    assert_that(
        CoreRequest(
            Request(Patch(), "/", Headers({"cookie": "sid=q1"}), Empty()), b""
        ).parameters.cookie["sid"],
        equal_to("q1"),
        "CoreRequest must expose cookies as parameters",
    )


def test_lower_cases_content_type():
    assert_that(
        CoreRequest(
            Request(
                Patch(),
                "/",
                Headers({"content-type": "Application/JSON; Charset=UTF-8"}),
                Empty(),
            ),
            b"",
        ).content_type,
        equal_to("application/json; charset=utf-8"),
        "CoreRequest must lower-case the content type",
    )


def test_exposes_body_bytes():
    assert_that(
        CoreRequest(
            Request(Patch(), "/", Headers(), Empty()), b'{"a":1}'
        ).body,
        equal_to(b'{"a":1}'),
        "CoreRequest must expose the buffered body",
    )
