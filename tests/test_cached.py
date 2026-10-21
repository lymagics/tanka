import pathlib
import shutil

import httpx
import pytest
from hamcrest import assert_that, empty, equal_to, is_not, matches_regexp
from hypothesis import given
from hypothesis import strategies as st

from fakes import Fixed
from tanka.asgi import Asgi
from tanka.body import Body, Empty, Raw, Text
from tanka.caching import Cached
from tanka.headers import Headers
from tanka.method import Get, Head, Post
from tanka.request import Request
from tanka.response import Response
from tanka.static import Directory, Static


def workspace(name: str) -> pathlib.Path:
    folder = pathlib.Path(__file__).parent.parent / "tmp" / name
    shutil.rmtree(folder, ignore_errors=True)
    folder.mkdir(parents=True)
    return folder


@given(st.binary(max_size=300))
async def test_tags_any_content_with_quoted_hex_etag(data: bytes):
    assert_that(
        (
            await Cached(Fixed(Response(Raw(data, "x/any")))).response(
                Request(Get(), "/", Headers(), Empty())
            )
        )
        .headers()
        .header("etag"),
        matches_regexp(r'^"[0-9a-f]{32}"$'),
        "Cached must tag any content with a quoted hexadecimal etag",
    )


async def test_tags_equal_content_with_equal_etag():
    assert_that(
        (
            await Cached(Fixed(Response(Text("same ünïcode")))).response(
                Request(Get(), "/one", Headers(), Empty())
            )
        )
        .headers()
        .header("etag"),
        equal_to(
            (
                await Cached(Fixed(Response(Text("same ünïcode")))).response(
                    Request(Get(), "/two", Headers(), Empty())
                )
            )
            .headers()
            .header("etag")
        ),
        "Cached must give equal content the same etag",
    )


async def test_tags_different_content_with_different_etag():
    assert_that(
        (
            await Cached(Fixed(Response(Raw(b"\x00", "x/a")))).response(
                Request(Get(), "/", Headers(), Empty())
            )
        )
        .headers()
        .header("etag"),
        is_not(
            equal_to(
                (
                    await Cached(
                        Fixed(Response(Raw(b"\x00\x00", "x/a")))
                    ).response(Request(Get(), "/", Headers(), Empty()))
                )
                .headers()
                .header("etag")
            )
        ),
        "Cached must give different content a different etag",
    )


@pytest.mark.parametrize(
    "condition",
    ["{}", '"stale", {}', "W/{}", '  {}  ,W/"old"', "*"],
)
async def test_answers_not_modified_when_client_holds_etag(condition: str):
    tag = (
        (
            await Cached(Fixed(Response(Text("css { }")))).response(
                Request(Get(), "/app.css", Headers(), Empty())
            )
        )
        .headers()
        .header("etag")
    )
    assert_that(
        (
            await Cached(Fixed(Response(Text("css { }")))).response(
                Request(
                    Get(),
                    "/app.css",
                    Headers({"if-none-match": condition.format(tag)}),
                    Empty(),
                )
            )
        ).status(),
        equal_to(304),
        f"Cached must answer 304 for if-none-match '{condition}'",
    )


async def test_sends_empty_body_when_not_modified():
    assert_that(
        await Body.Smart(
            (
                await Cached(Fixed(Response(Text("never sent")))).response(
                    Request(
                        Get(), "/", Headers({"if-none-match": "*"}), Empty()
                    )
                )
            ).body()
        ).bytes(),
        equal_to(b""),
        "Cached must send no body with a 304 reply",
    )


async def test_keeps_reply_headers_when_not_modified():
    assert_that(
        (
            await Cached(
                Fixed(
                    Response(
                        200,
                        Headers({"vary": "accept-encoding"}),
                        Text("varied"),
                    )
                )
            ).response(
                Request(Head(), "/", Headers({"if-none-match": "*"}), Empty())
            )
        )
        .headers()
        .values("vary"),
        equal_to(["accept-encoding"]),
        "Cached must keep the reply headers on a 304 reply",
    )


async def test_sends_full_body_when_client_holds_other_etag():
    assert_that(
        await Body.Smart(
            (
                await Cached(Fixed(Response(Text("fresh copy")))).response(
                    Request(
                        Get(),
                        "/",
                        Headers({"if-none-match": '"0123456789abcdef"'}),
                        Empty(),
                    )
                )
            ).body()
        ).text(),
        equal_to("fresh copy"),
        "Cached must send the full body when the etag does not match",
    )


async def test_keeps_content_type_of_full_reply():
    assert_that(
        (
            await Cached(
                Fixed(Response(Raw(b"GIF89a", "image/gif")))
            ).response(Request(Get(), "/", Headers(), Empty()))
        )
        .body()
        .headers()
        .header("content-type"),
        equal_to("image/gif"),
        "Cached must keep the content type of a full reply",
    )


async def test_serves_full_reply_to_unsafe_method_holding_etag():
    assert_that(
        (
            await Cached(Fixed(Response(Text("posted")))).response(
                Request(Post(), "/", Headers({"if-none-match": "*"}), Empty())
            )
        ).status(),
        equal_to(200),
        "Cached must serve a full reply to a POST request holding the etag",
    )


async def test_asks_clients_to_revalidate_by_default():
    assert_that(
        (
            await Cached(Fixed(Response(Text("revalidate me")))).response(
                Request(Get(), "/", Headers(), Empty())
            )
        )
        .headers()
        .header("cache-control"),
        equal_to("no-cache"),
        "Cached must ask clients to revalidate with no-cache by default",
    )


async def test_lets_clients_keep_reply_for_given_seconds():
    assert_that(
        (
            await Cached(Fixed(Response(Text("keep me"))), 86400).response(
                Request(Get(), "/", Headers(), Empty())
            )
        )
        .headers()
        .header("cache-control"),
        equal_to("max-age=86400"),
        "Cached must let clients keep the reply for the given seconds",
    )


async def test_sends_given_cache_control_verbatim():
    assert_that(
        (
            await Cached(
                Fixed(Response(Text("forever"))),
                "public, max-age=31536000, immutable",
            ).response(Request(Get(), "/", Headers(), Empty()))
        )
        .headers()
        .header("cache-control"),
        equal_to("public, max-age=31536000, immutable"),
        "Cached must send the given cache-control value unchanged",
    )


@pytest.mark.parametrize("status", [201, 206, 302, 404, 500])
async def test_adds_no_etag_to_non_200_reply(status: int):
    assert_that(
        (
            await Cached(Fixed(Response(status, Text("other")))).response(
                Request(Get(), "/", Headers(), Empty())
            )
        )
        .headers()
        .values("etag"),
        empty(),
        f"Cached must add no etag to a non-200 reply with status {status}",
    )


async def test_answers_not_modified_for_unchanged_static_file():
    folder = workspace("cached-static")
    (folder / "site.css").write_text("body { margin: 0 }")
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(
            app=Asgi(Cached(Static(Directory(str(folder)))))
        ),
        base_url="http://testserver",
    ) as http:
        assert_that(
            (
                await http.get(
                    "/site.css",
                    headers={
                        "if-none-match": (await http.get("/site.css")).headers[
                            "etag"
                        ]
                    },
                )
            ).status_code,
            equal_to(304),
            "Cached must answer 304 for an unchanged static file over ASGI",
        )
