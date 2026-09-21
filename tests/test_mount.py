import json

from hamcrest import assert_that, equal_to, has_entry, is_

from fakes import Echo
from tanka.body import Body, Empty
from tanka.headers import Headers
from tanka.method import Get
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
