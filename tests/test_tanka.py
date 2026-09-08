import asyncio

import httpx
from hamcrest import assert_that, calling, contains_string, equal_to, raises

from fakes import Failing, Fixed
from tanka.abort import Abort
from tanka.application import Silence, Tanka
from tanka.asgi import Asgi
from tanka.body import Text
from tanka.method import Get
from tanka.response import Response
from tanka.routes import Route, Routes
from tanka.server import Server


class Marker(Server):
    async def serve(self, asgi: Asgi) -> None:
        raise RuntimeError(f"served {type(asgi).__name__}")


def client(application: Tanka) -> httpx.AsyncClient:
    return httpx.AsyncClient(
        transport=httpx.ASGITransport(app=application.asgi()),
        base_url="http://tanka",
    )


async def test_serves_matching_route():
    async with client(
        Tanka(
            Routes(Route(Get(), "/hello", Fixed(Response(Text("hi"))))),
            Silence(),
        )
    ) as http:
        assert_that(
            (await http.get("/hello")).text,
            equal_to("hi"),
            "Tanka must serve the response of a matching route",
        )


async def test_answers_unknown_route_with_not_found_page():
    async with client(Tanka(Routes(), Silence())) as http:
        assert_that(
            (await http.get("/nowhere")).text,
            contains_string("<h1>Not Found</h1>"),
            "Tanka must render a default 404 page",
        )


async def test_answers_abort_with_its_status():
    async with client(
        Tanka(Failing(Abort(429, "slow down")), Silence())
    ) as http:
        assert_that(
            (await http.get("/")).status_code,
            equal_to(429),
            "Tanka must convert Abort into a response",
        )


async def test_answers_crash_with_server_error_page():
    async with client(
        Tanka(Failing(ValueError("unexpected")), Silence())
    ) as http:
        assert_that(
            (await http.get("/")).text,
            contains_string("<h1>Internal Server Error</h1>"),
            "Tanka must render a default 500 page",
        )


async def test_answers_unsupported_abort_with_server_error():
    async with client(Tanka(Failing(Abort(200, "odd")), Silence())) as http:
        assert_that(
            (await http.get("/")).status_code,
            equal_to(500),
            "Tanka must route an unsupported abort code to 500",
        )


async def test_logs_by_default():
    async with client(Tanka(Fixed(Response(Text("default"))))) as http:
        assert_that(
            (await http.get("/")).text,
            equal_to("default"),
            "Tanka must work with the default log",
        )


def test_runs_on_given_server():
    assert_that(
        calling(asyncio.run).with_args(
            Tanka(Fixed(Response(Text(""))), Silence()).run(Marker())
        ),
        raises(RuntimeError, "served Asgi"),
        "Tanka must hand its ASGI application to the server",
    )
