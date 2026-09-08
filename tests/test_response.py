from hamcrest import assert_that, empty, equal_to, instance_of

from tanka.body import Body, Html, Text
from tanka.headers import Headers
from tanka.response import Reply, Response


def test_defaults_status_to_ok():
    assert_that(
        Response(Html("<i>x</i>")).status(),
        equal_to(200),
        "Response without status must default to 200",
    )


def test_keeps_given_status():
    assert_that(
        Response(201, Text("created")).status(),
        equal_to(201),
        "Response must keep the given status",
    )


def test_has_no_headers_by_default():
    assert_that(
        list(Response(202, Text("later")).headers()),
        empty(),
        "Response without headers must have none",
    )


def test_keeps_given_headers():
    assert_that(
        Response(200, Headers({"x-id": "7"}), Text(""))
        .headers()
        .header("x-id"),
        equal_to("7"),
        "Response must keep the given headers",
    )


async def test_exposes_body():
    assert_that(
        await Body.Smart(Response(Text("payload")).body()).text(),
        equal_to("payload"),
        "Response must expose its body",
    )


def test_is_a_reply():
    assert_that(
        Response(Text("")),
        instance_of(Reply),
        "Response must implement the Reply interface",
    )
