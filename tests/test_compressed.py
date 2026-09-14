import gzip

import httpx
import pytest
from hamcrest import assert_that, empty, equal_to

from fakes import Fixed
from tanka.asgi import Asgi
from tanka.body import Body, Empty, Html, Raw, Text
from tanka.compression import Compressed
from tanka.headers import Headers
from tanka.method import Get
from tanka.request import Request
from tanka.response import Redirect, Response


def asking(encoding: str) -> Request:
    return Request(Get(), "/", Headers({"accept-encoding": encoding}), Empty())


@pytest.mark.parametrize(
    "encoding",
    ["gzip", "GZIP", "deflate, gzip;q=0.5", "*", "identity;q=1, *;q=0.1"],
)
async def test_compresses_body_when_client_accepts_gzip(encoding: str):
    assert_that(
        gzip.decompress(
            await Body.Smart(
                (
                    await Compressed(
                        Fixed(Response(Html("<i>" * 300)))
                    ).response(asking(encoding))
                ).body()
            ).bytes()
        ),
        equal_to(b"<i>" * 300),
        f"Compressed must gzip the body for accept-encoding '{encoding}'",
    )


@pytest.mark.parametrize(
    "encoding",
    ["br", "gzip;q=0", "*;q=0", "gzip;q=0.000, *", "identity"],
)
async def test_passes_body_through_when_client_declines_gzip(
    encoding: str,
):
    assert_that(
        await Body.Smart(
            (
                await Compressed(
                    Fixed(Response(Text("plain " * 200)))
                ).response(asking(encoding))
            ).body()
        ).text(),
        equal_to("plain " * 200),
        f"Compressed must keep the body for accept-encoding '{encoding}'",
    )


async def test_passes_body_through_without_accept_encoding_header():
    assert_that(
        await Body.Smart(
            (
                await Compressed(Fixed(Response(Text("x" * 900)))).response(
                    Request(Get(), "/", Headers(), Empty())
                )
            ).body()
        ).text(),
        equal_to("x" * 900),
        "Compressed must keep the body when the client says nothing",
    )


async def test_passes_small_body_through():
    assert_that(
        await Body.Smart(
            (
                await Compressed(Fixed(Response(Text("tiny")))).response(
                    asking("gzip")
                )
            ).body()
        ).text(),
        equal_to("tiny"),
        "Compressed must keep a body shorter than the minimum",
    )


async def test_compresses_body_of_given_minimum():
    assert_that(
        gzip.decompress(
            await Body.Smart(
                (
                    await Compressed(
                        Fixed(Response(Text("seven77"))), 7
                    ).response(asking("gzip"))
                ).body()
            ).bytes()
        ),
        equal_to(b"seven77"),
        "Compressed must gzip a body as long as the given minimum",
    )


async def test_passes_already_encoded_body_through():
    assert_that(
        await Body.Smart(
            (
                await Compressed(
                    Fixed(
                        Response(
                            200,
                            Headers({"content-encoding": "br"}),
                            Raw(b"\x1b" * 600, "text/html"),
                        )
                    )
                ).response(asking("gzip"))
            ).body()
        ).bytes(),
        equal_to(b"\x1b" * 600),
        "Compressed must not gzip a body that is already encoded",
    )


async def test_declares_gzip_encoding():
    assert_that(
        (
            await Compressed(Fixed(Response(Text("y" * 501)))).response(
                asking("gzip")
            )
        )
        .body()
        .headers()
        .header("content-encoding"),
        equal_to("gzip"),
        "Compressed must declare gzip content encoding",
    )


async def test_tells_caches_to_vary_by_accept_encoding():
    assert_that(
        (
            await Compressed(Fixed(Response(Text("v" * 777)))).response(
                asking("gzip, br")
            )
        )
        .headers()
        .header("vary"),
        equal_to("accept-encoding"),
        "Compressed must add a vary header for accept-encoding",
    )


async def test_drops_length_from_headers_of_origin():
    assert_that(
        (
            await Compressed(
                Fixed(
                    Response(
                        200,
                        Headers({"content-length": "1024"}),
                        Text("z" * 1024),
                    )
                )
            ).response(asking("gzip"))
        )
        .headers()
        .values("content-length"),
        empty(),
        "Compressed must drop the content length of the origin",
    )


async def test_keeps_other_headers_of_origin():
    assert_that(
        (
            await Compressed(
                Fixed(
                    Response(
                        200,
                        Headers({"x-trace": "0xdeadbeef"}),
                        Text("w" * 640),
                    )
                )
            ).response(asking("gzip"))
        )
        .headers()
        .header("x-trace"),
        equal_to("0xdeadbeef"),
        "Compressed must keep the other headers of the origin",
    )


async def test_keeps_status_of_origin():
    assert_that(
        (
            await Compressed(Fixed(Response(226, Text("k" * 512)))).response(
                asking("gzip")
            )
        ).status(),
        equal_to(226),
        "Compressed must keep the status of the origin",
    )


async def test_keeps_headers_of_declined_origin():
    assert_that(
        list(
            (
                await Compressed(Fixed(Redirect("/elsewhere", 307))).response(
                    asking("gzip")
                )
            ).headers()
        ),
        equal_to([("location", "/elsewhere")]),
        "Compressed must keep the headers of a reply it passes through",
    )


async def test_serves_gzip_over_asgi():
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(
            app=Asgi(Compressed(Fixed(Response(Html("<hr>" * 250)))))
        ),
        base_url="http://testserver",
    ) as http:
        assert_that(
            (await http.get("/", headers={"accept-encoding": "gzip"})).headers[
                "content-encoding"
            ],
            equal_to("gzip"),
            "Compressed must announce gzip encoding over ASGI",
        )


async def test_serves_readable_text_over_asgi():
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(
            app=Asgi(Compressed(Fixed(Response(Text("readable " * 100)))))
        ),
        base_url="http://testserver",
    ) as http:
        assert_that(
            (await http.get("/", headers={"accept-encoding": "gzip"})).text,
            equal_to("readable " * 100),
            "Compressed must serve a body the client can decode",
        )
