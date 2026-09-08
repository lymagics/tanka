import asyncio

from hamcrest import assert_that, calling, equal_to, raises

from fakes import Failing, Fixed
from tanka.abort import Abort
from tanka.application import Aborted
from tanka.body import Empty, Text
from tanka.headers import Headers
from tanka.method import Get
from tanka.request import Request
from tanka.response import Response


async def test_turns_abort_into_error_page():
    assert_that(
        (
            await Aborted(Failing(Abort(404, "gone"))).response(
                Request(Get(), "/", Headers(), Empty())
            )
        ).status(),
        equal_to(404),
        "Aborted must answer an Abort with a page of the same status",
    )


async def test_passes_success_through():
    assert_that(
        (
            await Aborted(Fixed(Response(200, Text("fine")))).response(
                Request(Get(), "/", Headers(), Empty())
            )
        ).status(),
        equal_to(200),
        "Aborted must not touch a normal response",
    )


def test_lets_other_exceptions_propagate():
    assert_that(
        calling(asyncio.run).with_args(
            Aborted(Failing(KeyError("k"))).response(
                Request(Get(), "/", Headers(), Empty())
            )
        ),
        raises(KeyError),
        "Aborted must handle only Abort",
    )


def test_breaks_on_unsupported_abort_code():
    assert_that(
        calling(asyncio.run).with_args(
            Aborted(Failing(Abort(302, "moved"))).response(
                Request(Get(), "/", Headers(), Empty())
            )
        ),
        raises(Exception, "not supported"),
        "Aborted must break on an Abort with a non-error code",
    )
