import json

import httpx
import pytest
from hamcrest import assert_that, equal_to, has_entry, is_

from fakes import Echo, Known
from tanka.asgi import Asgi
from tanka.auth import Authenticated
from tanka.body import Body, Empty, Text
from tanka.headers import Headers
from tanka.identity import Principal
from tanka.method import Get, Post
from tanka.request import Request
from tanka.routes import Mount, Route, Routes


def test_matches_paths_under_prefix():
    assert_that(
        Mount("/v2", Echo()).matches(
            Request(Get(), "/v2/users", Headers(), Empty())
        ),
        is_(True),
        "Mount must match paths under its prefix",
    )


def test_matches_prefix_itself():
    assert_that(
        Mount("/api", Echo()).matches(
            Request(Get(), "/api", Headers(), Empty())
        ),
        is_(True),
        "Mount must match the bare prefix",
    )


def test_rejects_longer_segment():
    assert_that(
        Mount("/v1", Echo()).matches(
            Request(Get(), "/v10/users", Headers(), Empty())
        ),
        is_(False),
        "Mount must not match a segment that merely starts with the prefix",
    )


async def test_matches_nested_paths_when_prefix_is_root():
    assert_that(
        Mount("/", Echo()).matches(
            Request(Get(), "/orders/7", Headers(), Empty())
        ),
        is_(True),
        "Mount must match paths under the root prefix '/'",
    )


async def test_dispatches_bare_prefix_to_nested_root_route():
    assert_that(
        (
            await Mount(
                "/gallery", Routes(Route(Get(), "/", Echo()))
            ).response(Request(Get(), "/gallery", Headers(), Empty()))
        ).status(),
        equal_to(200),
        "Mount must dispatch its bare prefix to a nested route pattern '/'",
    )


async def test_strips_prefix_for_nested_routes():
    assert_that(
        json.loads(
            await Body.Smart(
                (
                    await Mount(
                        "/v3", Routes(Route(Get(), "/users", Echo()))
                    ).response(
                        Request(Get(), "/v3/users?p=1", Headers(), Empty())
                    )
                ).body()
            ).text()
        ),
        has_entry("path", "/users"),
        "Mount must strip its prefix before delegating",
    )


@pytest.mark.parametrize("prefix", ["/catalog", "/catalog/"])
async def test_dispatches_trailing_prefix_with_query_intact(prefix):
    assert_that(
        json.loads(
            await Body.Smart(
                (
                    await Routes(
                        Mount(
                            prefix,
                            Routes(Route(Get(), "/items/{number}", Echo())),
                        )
                    ).response(
                        Request(
                            Get(),
                            "/catalog/items/19?view=brief",
                            Headers(),
                            Empty(),
                        )
                    )
                ).body()
            ).text()
        ),
        equal_to(
            {
                "method": ["GET"],
                "path": "/items/19",
                "query": "view=brief",
                "roles": [],
                "body": "",
            }
        ),
        "Mount must preserve path and query with either prefix spelling",
    )


async def test_dispatches_root_mount_to_nested_route():
    assert_that(
        json.loads(
            await Body.Smart(
                (
                    await Routes(
                        Mount(
                            "/",
                            Routes(Route(Get(), "/books/{number}", Echo())),
                        )
                    ).response(
                        Request(
                            Get(),
                            "/books/23?edition=second",
                            Headers(),
                            Empty(),
                        )
                    )
                ).body()
            ).text()
        ),
        has_entry("path", "/books/23"),
        "Mount must preserve the leading slash when mounted at the root",
    )


@pytest.mark.parametrize("target", ["/shop", "/shop/"])
async def test_dispatches_trailing_prefix_itself_to_child_root(target):
    assert_that(
        (
            await Routes(
                Mount("/shop/", Routes(Route(Get(), "/", Echo())))
            ).response(Request(Get(), target, Headers(), Empty()))
        ).status(),
        equal_to(200),
        "Mount must dispatch either prefix spelling to the child root",
    )


def test_rejects_longer_segment_with_trailing_prefix():
    assert_that(
        Mount("/part/", Echo()).matches(
            Request(Get(), "/partial/item", Headers(), Empty())
        ),
        is_(False),
        "Mount must retain segment boundaries after trimming the slash",
    )


def test_rejects_empty_path_under_root_mount():
    assert_that(
        Mount("/", Echo()).matches(Request(Get(), "", Headers(), Empty())),
        is_(False),
        "Mount must not turn an empty path into a root request",
    )


@pytest.mark.parametrize("prefix", ["/", "/api/"])
async def test_dispatches_http_request_through_mount_to_dynamic_route(prefix):
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(
            app=Asgi(
                Routes(
                    Mount(
                        prefix, Routes(Route(Get(), "/articles/{id}", Echo()))
                    )
                )
            )
        ),
        base_url="http://testserver",
    ) as http:
        assert_that(
            (await http.get(f"{prefix}articles/37?format=short")).json(),
            equal_to(
                {
                    "method": ["GET"],
                    "path": "/articles/37",
                    "query": "format=short",
                    "roles": [],
                    "body": "",
                }
            ),
            "Mount must deliver the HTTP request to its nested dynamic route",
        )


async def test_preserves_authenticated_post_through_nested_mounts():
    assert_that(
        json.loads(
            await Body.Smart(
                (
                    await Authenticated(
                        Routes(
                            Mount(
                                "/",
                                Routes(
                                    Mount(
                                        "/records/",
                                        Routes(
                                            Route(Post(), "/{key}", Echo())
                                        ),
                                    )
                                ),
                            )
                        ),
                        Known(Principal("synthetic-editor", "editor")),
                    ).response(
                        Request(
                            Post(),
                            "/records/41?mode=preview",
                            Headers(),
                            Text("synthetic payload"),
                        )
                    )
                ).body()
            ).text()
        ),
        equal_to(
            {
                "method": ["POST"],
                "path": "/41",
                "query": "mode=preview",
                "roles": ["editor"],
                "body": "synthetic payload",
            }
        ),
        "Nested mounts must preserve the authenticated POST request",
    )
