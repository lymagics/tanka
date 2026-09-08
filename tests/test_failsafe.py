from hamcrest import assert_that, equal_to, has_item, string_contains_in_order

from fakes import Failing, Fixed, Notebook
from tanka.application import Failsafe, Silence
from tanka.body import Empty
from tanka.headers import Headers
from tanka.method import Get
from tanka.request import Request
from tanka.response import Response


async def test_answers_exception_with_server_error():
    assert_that(
        (
            await Failsafe(Failing(ZeroDivisionError()), Silence()).response(
                Request(Get(), "/", Headers(), Empty())
            )
        ).status(),
        equal_to(500),
        "Failsafe must answer any exception with 500",
    )


async def test_logs_traceback():
    lines: list[str] = []
    await Failsafe(
        Failing(RuntimeError("disk on fire")), Notebook(lines)
    ).response(Request(Get(), "/", Headers(), Empty()))
    assert_that(
        lines,
        has_item(
            string_contains_in_order("Traceback", "RuntimeError: disk on fire")
        ),
        "Failsafe must log the traceback of the exception",
    )


async def test_passes_success_through():
    assert_that(
        (
            await Failsafe(Fixed(Response(204, Empty())), Silence()).response(
                Request(Get(), "/", Headers(), Empty())
            )
        ).status(),
        equal_to(204),
        "Failsafe must not touch a normal response",
    )
