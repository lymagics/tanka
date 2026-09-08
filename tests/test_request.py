from hamcrest import assert_that, calling, contains_exactly, equal_to, raises

from tanka.body import Empty, Text
from tanka.headers import Headers
from tanka.identity import Principal
from tanka.method import Delete, Get, Post
from tanka.request import Request
from tanka.target import Path, Query, Target


def test_parses_target_from_text():
    assert_that(
        Request(Get(), "/items?sort=name", Headers(), Empty())
        .target()
        .query()
        .parameter("sort"),
        equal_to("name"),
        "Request must parse a textual target",
    )


def test_keeps_given_target_object():
    assert_that(
        str(
            Request(
                Post(), Target(Path("/a"), Query("b=c")), Headers(), Empty()
            ).target()
        ),
        equal_to("/a?b=c"),
        "Request must keep a Target object as given",
    )


def test_exposes_method():
    assert_that(
        Request(Delete(), "/x", Headers(), Empty()).method().names(),
        contains_exactly("DELETE"),
        "Request must expose its method",
    )


def test_exposes_headers():
    assert_that(
        Request(Get(), "/", Headers({"accept": "*/*"}), Empty())
        .headers()
        .header("accept"),
        equal_to("*/*"),
        "Request must expose its headers",
    )


async def test_decodes_body_on_demand():
    assert_that(
        await Request(Post(), "/", Headers(), Text('{"n": 5}')).body().json(),
        equal_to({"n": 5}),
        "Request must expose a smart body that decodes JSON",
    )


def test_reads_cookies_from_header():
    assert_that(
        Request(Get(), "/", Headers({"Cookie": "a=1; sid=zz"}), Empty())
        .cookies()
        .cookie("sid"),
        equal_to("zz"),
        "Request must derive cookies from the cookie header",
    )


def test_joins_multiple_cookie_headers():
    assert_that(
        list(
            Request(
                Get(),
                "/",
                Headers([("cookie", "a=1"), ("cookie", "b=2")]),
                Empty(),
            ).cookies()
        ),
        contains_exactly(("a", "1"), ("b", "2")),
        "Request must merge repeated cookie headers",
    )


def test_is_anonymous_by_default():
    assert_that(
        calling(Request(Get(), "/", Headers(), Empty()).identity().id),
        raises(Exception, "not authenticated"),
        "Request without identity must be anonymous",
    )


def test_carries_given_identity():
    assert_that(
        Request(Get(), "/", Headers(), Empty(), Principal("p-9"))
        .identity()
        .id(),
        equal_to("p-9"),
        "Request must expose the given identity",
    )


def test_carries_identity_with_textual_target():
    assert_that(
        Request(Get(), "/me", Headers(), Empty(), Principal("p-3", "vip"))
        .identity()
        .roles(),
        contains_exactly("vip"),
        "Request must accept identity together with a textual target",
    )
