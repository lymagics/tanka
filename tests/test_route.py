import json

from hamcrest import assert_that, equal_to, has_entry, is_

from fakes import Echo, Fixed
from tanka.body import Body, Empty, Text
from tanka.endpoint import Endpoint
from tanka.headers import Headers
from tanka.identity import Principal
from tanka.method import Get, Head, Methods, Post
from tanka.request import Request
from tanka.response import Reply, Response
from tanka.routes import Route


class Named(Endpoint):
    async def response(self, request: Request) -> Reply:
        return Response(Text(request.target().path().parameter("name")))


def test_matches_method_and_path():
    assert_that(
        Route(Get(), "/users/{id}", Echo()).matches(
            Request(Get(), "/users/5", Headers(), Empty())
        ),
        is_(True),
        "Route must match the same method and a fitting path",
    )


def test_rejects_other_method():
    assert_that(
        Route(Get(), "/users", Echo()).matches(
            Request(Post(), "/users", Headers(), Empty())
        ),
        is_(False),
        "Route must reject a different method",
    )


def test_rejects_other_path():
    assert_that(
        Route(Get(), "/users", Echo()).matches(
            Request(Get(), "/users/1", Headers(), Empty())
        ),
        is_(False),
        "Route must reject a path outside the pattern",
    )


def test_is_case_sensitive():
    assert_that(
        Route(Get(), "/Users", Echo()).matches(
            Request(Get(), "/users", Headers(), Empty())
        ),
        is_(False),
        "Route must match paths case-sensitively",
    )


def test_matches_any_of_several_methods():
    assert_that(
        Route(Methods(Get(), Head()), "/", Echo()).matches(
            Request(Head(), "/", Headers(), Empty())
        ),
        is_(True),
        "Route must match any of the bound methods",
    )


async def test_binds_path_parameters_for_endpoint():
    assert_that(
        await Body.Smart(
            (
                await Route(Get(), "/hello/{name}", Named()).response(
                    Request(Get(), "/hello/world", Headers(), Empty())
                )
            ).body()
        ).text(),
        equal_to("world"),
        "Route must bind path parameters before delegating",
    )


async def test_keeps_query_for_endpoint():
    assert_that(
        json.loads(
            await Body.Smart(
                (
                    await Route(Get(), "/q", Echo()).response(
                        Request(Get(), "/q?k=v", Headers(), Empty())
                    )
                ).body()
            ).text()
        ),
        has_entry("query", "k=v"),
        "Route must pass the query string through",
    )


async def test_delegates_to_endpoint():
    assert_that(
        (
            await Route(Post(), "/", Fixed(Response(204, Empty()))).response(
                Request(Post(), "/", Headers(), Empty())
            )
        ).status(),
        equal_to(204),
        "Route must return the response of its endpoint",
    )


async def test_keeps_identity_of_request():
    assert_that(
        json.loads(
            await Body.Smart(
                (
                    await Route(Get(), "/me", Echo()).response(
                        Request(
                            Get(),
                            "/me",
                            Headers(),
                            Empty(),
                            Principal("1", "x"),
                        )
                    )
                ).body()
            ).text()
        ),
        has_entry("roles", ["x"]),
        "Route must keep the identity of the request",
    )
