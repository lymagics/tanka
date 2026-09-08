import asyncio

from hamcrest import assert_that, calling, equal_to, raises

from fakes import Complaint, Failing, Fixed
from tanka.abort import Abort
from tanka.body import Body, Empty, Text
from tanka.catch import Catch, On, Range
from tanka.headers import Headers
from tanka.method import Get
from tanka.request import Request
from tanka.response import Response


async def test_routes_abort_to_matching_fallback():
    assert_that(
        (
            await Catch(
                Failing(Abort(404, "nope")),
                On(500, Fixed(Response(500, Text("boom")))),
                On(404, Fixed(Response(404, Text("lost")))),
            ).response(Request(Get(), "/", Headers(), Empty()))
        ).status(),
        equal_to(404),
        "Catch must pick the fallback matching the abort status",
    )


async def test_routes_plain_exception_to_server_error():
    assert_that(
        (
            await Catch(
                Failing(ValueError("bad state")),
                On(Range(500, 599), Fixed(Response(500, Text("oops")))),
            ).response(Request(Get(), "/", Headers(), Empty()))
        ).status(),
        equal_to(500),
        "Catch must treat any non-Abort exception as 500",
    )


async def test_hands_caught_abort_to_fallback():
    assert_that(
        await Body.Smart(
            (
                await Catch(
                    Failing(Abort(409, "name already taken")),
                    On(..., Complaint()),
                ).response(Request(Get(), "/", Headers(), Empty()))
            ).body()
        ).text(),
        equal_to("name already taken"),
        "Catch must hand the caught abort to the fallback",
    )


async def test_hands_plain_exception_as_server_abort():
    assert_that(
        (
            await Catch(
                Failing(KeyError("owner")),
                On(..., Complaint()),
            ).response(Request(Get(), "/", Headers(), Empty()))
        ).status(),
        equal_to(500),
        "Catch must wrap a plain exception into an abort with status 500",
    )


async def test_passes_successful_response_through():
    assert_that(
        (
            await Catch(
                Fixed(Response(201, Text("made"))),
                On(..., Fixed(Response(500, Text("never")))),
            ).response(Request(Get(), "/", Headers(), Empty()))
        ).status(),
        equal_to(201),
        "Catch must not touch a successful response",
    )


def test_rethrows_unmatched_abort():
    assert_that(
        calling(asyncio.run).with_args(
            Catch(
                Failing(Abort(403, "no way")),
                On(404, Fixed(Response(404, Text("lost")))),
            ).response(Request(Get(), "/", Headers(), Empty()))
        ),
        raises(Abort, "no way"),
        "Catch must re-raise an abort no fallback matches",
    )


def test_rethrows_unmatched_exception():
    assert_that(
        calling(asyncio.run).with_args(
            Catch(
                Failing(RuntimeError("crash")),
                On(404, Fixed(Response(404, Text("lost")))),
            ).response(Request(Get(), "/", Headers(), Empty()))
        ),
        raises(RuntimeError, "crash"),
        "Catch must re-raise an exception no fallback matches",
    )


def test_breaks_on_abort_with_unsupported_code():
    assert_that(
        calling(asyncio.run).with_args(
            Catch(
                Failing(Abort(200, "not an error")),
                On(..., Fixed(Response(500, Text("generic")))),
            ).response(Request(Get(), "/", Headers(), Empty()))
        ),
        raises(Exception, "not supported"),
        "Catch must let an unsupported abort code break through",
    )
