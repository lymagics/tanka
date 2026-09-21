import asyncio

import httpx
from hamcrest import (
    assert_that,
    calling,
    equal_to,
    has_property,
    instance_of,
    raises,
)

from fakes import Failing, Fixed, Sleepy
from tanka.abort import Abort
from tanka.application import Silence, Tanka
from tanka.body import Body, Empty, Text
from tanka.headers import Headers
from tanka.method import Get
from tanka.request import Request
from tanka.response import Response
from tanka.timeout import Timeout


def test_aborts_with_gateway_timeout_when_origin_is_slow():
    assert_that(
        calling(asyncio.run).with_args(
            Timeout(Sleepy(Response(Text("late")), 3.5), 0.01).response(
                Request(Get(), "/", Headers(), Empty())
            )
        ),
        raises(Abort, matching=has_property("code", equal_to(504))),
        "Timeout must abort with 504 once the deadline is passed",
    )


def test_names_deadline_in_abort_message():
    assert_that(
        calling(asyncio.run).with_args(
            Timeout(Sleepy(Response(Text("slow")), 7), 0.02).response(
                Request(Get(), "/report", Headers(), Empty())
            )
        ),
        raises(Abort, "0.02 seconds"),
        "Timeout must say how many seconds the origin had",
    )


def test_chains_abort_to_original_timeout_error():
    assert_that(
        calling(asyncio.run).with_args(
            Timeout(Sleepy(Response(Text("z")), 42), 0.005).response(
                Request(Get(), "/z", Headers(), Empty())
            )
        ),
        raises(
            Abort,
            matching=has_property("__cause__", instance_of(TimeoutError)),
        ),
        "Timeout must chain the abort to the error that caused it",
    )


async def test_passes_reply_of_prompt_origin_through():
    assert_that(
        await Body.Smart(
            (
                await Timeout(Fixed(Response(Text("quick"))), 2.5).response(
                    Request(Get(), "/", Headers(), Empty())
                )
            ).body()
        ).text(),
        equal_to("quick"),
        "Timeout must pass through a reply that arrives in time",
    )


async def test_keeps_status_of_prompt_origin():
    assert_that(
        (
            await Timeout(Fixed(Response(226, Text("k"))), 1).response(
                Request(Get(), "/", Headers(), Empty())
            )
        ).status(),
        equal_to(226),
        "Timeout must keep the status of a reply that arrives in time",
    )


def test_lets_abort_of_origin_through():
    assert_that(
        calling(asyncio.run).with_args(
            Timeout(Failing(Abort(418, "no coffee")), 9).response(
                Request(Get(), "/tea", Headers(), Empty())
            )
        ),
        raises(Abort, "no coffee"),
        "Timeout must let an abort of its origin through unchanged",
    )


async def test_serves_gateway_timeout_over_asgi():
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(
            app=Tanka(
                Timeout(Sleepy(Response(Text("never")), 11), 0.01),
                Silence(),
            ).asgi()
        ),
        base_url="http://testserver",
    ) as http:
        assert_that(
            (await http.get("/slow")).status_code,
            equal_to(504),
            "Timeout must answer 504 over ASGI once the deadline is passed",
        )
