from hamcrest import assert_that, equal_to

from tanka.body import Json, Text
from tanka.headers import Headers
from tanka.openapi import CoreResponse
from tanka.response import Response


def test_exposes_status_code():
    assert_that(
        CoreResponse(Response(207, Text("")), b"").status_code,
        equal_to(207),
        "CoreResponse must expose the status code",
    )


def test_takes_content_type_from_body():
    assert_that(
        CoreResponse(Response(Json([1])), b"[1]").content_type,
        equal_to("application/json"),
        "CoreResponse must take the content type from the body",
    )


def test_prefers_explicit_content_type():
    assert_that(
        CoreResponse(
            Response(
                200, Headers({"content-type": "text/x-custom"}), Text("")
            ),
            b"",
        ).content_type,
        equal_to("text/x-custom"),
        "CoreResponse must prefer an explicit content type header",
    )


def test_merges_headers_of_body_and_reply():
    assert_that(
        CoreResponse(
            Response(200, Headers({"x-rate": "9"}), Text("abc")), b"abc"
        ).headers["content-length"],
        equal_to("3"),
        "CoreResponse must include headers of the body",
    )


def test_exposes_data():
    assert_that(
        CoreResponse(Response(Text("raw")), b"raw").data,
        equal_to(b"raw"),
        "CoreResponse must expose the buffered data",
    )
