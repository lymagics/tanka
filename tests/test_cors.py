import asyncio

import httpx
import pytest
from hamcrest import assert_that, calling, empty, equal_to, raises

from fakes import Failing, Fixed
from tanka.abort import Abort
from tanka.application import Silence, Tanka
from tanka.body import Empty, Text
from tanka.cors import AllowCredentials, AllowMethods, AllowOrigins, Cors
from tanka.headers import Headers
from tanka.method import Get, Options, Post
from tanka.request import Request
from tanka.response import Response


async def test_answers_preflight_without_calling_origin():
    assert_that(
        (
            await Cors(
                Fixed(Response(500, Text("must not be called"))),
                AllowOrigins("https://app.example"),
                AllowMethods(Post()),
            ).response(
                Request(
                    Options(),
                    "/users",
                    Headers(
                        {
                            "origin": "https://app.example",
                            "access-control-request-method": "POST",
                        }
                    ),
                    Empty(),
                )
            )
        ).status(),
        equal_to(204),
        "Cors must answer preflight itself with 204",
    )


async def test_lists_methods_on_preflight():
    assert_that(
        (
            await Cors(
                Fixed(Response(Text(""))),
                AllowOrigins("*"),
                AllowMethods(Get(), Post()),
            ).response(
                Request(
                    Options(),
                    "/",
                    Headers(
                        {
                            "origin": "https://x.example",
                            "access-control-request-method": "GET",
                        }
                    ),
                    Empty(),
                )
            )
        )
        .headers()
        .header("access-control-allow-methods"),
        equal_to("GET, POST"),
        "Cors must include policy headers on preflight",
    )


async def test_decorates_actual_response():
    assert_that(
        (
            await Cors(
                Fixed(Response(200, Headers({"x-own": "1"}), Text("data"))),
                AllowOrigins("https://site.example"),
            ).response(
                Request(
                    Get(),
                    "/",
                    Headers({"origin": "https://site.example"}),
                    Empty(),
                )
            )
        )
        .headers()
        .header("access-control-allow-origin"),
        equal_to("https://site.example"),
        "Cors must add allow-origin to the actual response",
    )


async def test_keeps_status_of_actual_response():
    assert_that(
        (
            await Cors(
                Fixed(Response(201, Text("made"))), AllowOrigins("*")
            ).response(
                Request(
                    Get(),
                    "/",
                    Headers({"origin": "https://s.example"}),
                    Empty(),
                )
            )
        ).status(),
        equal_to(201),
        "Cors must keep the status of the wrapped response",
    )


def test_refuses_wildcard_origin_with_credentials_on_preflight():
    assert_that(
        calling(asyncio.run).with_args(
            Cors(
                Fixed(Response(Text(""))),
                AllowOrigins("*"),
                AllowCredentials(),
            ).response(
                Request(
                    Options(),
                    "/login",
                    Headers(
                        {
                            "origin": "https://wild.example",
                            "access-control-request-method": "DELETE",
                        }
                    ),
                    Empty(),
                )
            )
        ),
        raises(Exception, "wildcard origin"),
        "Cors must refuse a wildcard origin paired with credentials",
    )


def test_refuses_wildcard_origin_with_credentials_on_actual_request():
    assert_that(
        calling(asyncio.run).with_args(
            Cors(
                Fixed(Response(200, Text("secret"))),
                AllowCredentials(),
                AllowOrigins("https://a.example", "*"),
            ).response(
                Request(
                    Get(),
                    "/me",
                    Headers({"origin": "https://b.example"}),
                    Empty(),
                )
            )
        ),
        raises(Exception, "credentials"),
        "Cors must refuse credentials paired with a wildcard origin",
    )


async def test_allows_credentials_for_listed_origin():
    assert_that(
        (
            await Cors(
                Fixed(Response(200, Text("profile"))),
                AllowOrigins("https://shop.example"),
                AllowCredentials(),
            ).response(
                Request(
                    Get(),
                    "/profile",
                    Headers({"origin": "https://shop.example"}),
                    Empty(),
                )
            )
        )
        .headers()
        .header("access-control-allow-credentials"),
        equal_to("true"),
        "Cors must allow credentials for an explicitly listed origin",
    )


async def test_adds_nothing_for_same_origin_request():
    assert_that(
        list(
            (
                await Cors(
                    Fixed(Response(Text(""))), AllowOrigins("*")
                ).response(Request(Get(), "/", Headers(), Empty()))
            ).headers()
        ),
        empty(),
        "Cors must leave a same-origin response untouched",
    )


async def test_allows_listed_origin_to_read_error_reply():
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(
            app=Tanka(
                Cors(
                    Failing(Abort(422, "Ünprocessable órder")),
                    AllowOrigins("https://shop.example:8443"),
                ),
                Silence(),
            ).asgi()
        ),
        base_url="http://api.example",
    ) as http:
        assert_that(
            (
                await http.post(
                    "/orders",
                    headers={"origin": "https://shop.example:8443"},
                )
            ).headers.get_list("access-control-allow-origin"),
            equal_to(["https://shop.example:8443"]),
            "Cors must let a listed origin read a reply that ends with Abort",
        )
