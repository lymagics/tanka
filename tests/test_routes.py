import asyncio

from hamcrest import assert_that, calling, equal_to, is_, raises

from fakes import Fixed
from tanka.body import Empty, Text
from tanka.headers import Headers
from tanka.method import Get, Post
from tanka.request import Request
from tanka.response import Response
from tanka.routes import Route, Routes


async def test_dispatches_to_first_matching_route():
    assert_that(
        (
            await Routes(
                Route(Get(), "/a", Fixed(Response(201, Text("first")))),
                Route(Get(), "/a", Fixed(Response(202, Text("second")))),
            ).response(Request(Get(), "/a", Headers(), Empty()))
        ).status(),
        equal_to(201),
        "Routes must pick the first matching route",
    )


async def test_skips_routes_that_do_not_match():
    assert_that(
        (
            await Routes(
                Route(Post(), "/b", Fixed(Response(200, Text("post")))),
                Route(Get(), "/b", Fixed(Response(203, Text("get")))),
            ).response(Request(Get(), "/b", Headers(), Empty()))
        ).status(),
        equal_to(203),
        "Routes must skip routes whose method differs",
    )


def test_aborts_with_not_found_when_nothing_matches():
    assert_that(
        calling(asyncio.run).with_args(
            Routes(Route(Get(), "/", Fixed(Response(Text(""))))).response(
                Request(Get(), "/missing", Headers(), Empty())
            )
        ),
        raises(Exception, "No route matches GET /missing"),
        "Routes must abort with 404 when no route matches",
    )


def test_matches_when_any_route_matches():
    assert_that(
        Routes(
            Route(Get(), "/x", Fixed(Response(Text("")))),
            Route(Get(), "/y", Fixed(Response(Text("")))),
        ).matches(Request(Get(), "/y", Headers(), Empty())),
        is_(True),
        "Routes must match when any nested route matches",
    )


def test_does_not_match_when_empty():
    assert_that(
        Routes().matches(Request(Get(), "/", Headers(), Empty())),
        is_(False),
        "Empty Routes must match nothing",
    )
