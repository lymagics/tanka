import pytest
from hamcrest import assert_that, equal_to, is_

from fakes import Complaint, Fixed
from tanka.abort import Abort
from tanka.body import Body, Empty, Text
from tanka.catch import On, Range
from tanka.headers import Headers
from tanka.method import Get
from tanka.request import Request
from tanka.response import Response


@pytest.mark.parametrize(
    "codes, code",
    [(404, 404), ((401, 403), 403), (Range(500, 599), 502), (..., 418)],
)
def test_matches_code_described_in_any_form(codes, code):
    assert_that(
        On(codes, Fixed(Response(Text("")))).matches(code),
        is_(True),
        "On must accept an int, a tuple, a Range or an ellipsis",
    )


def test_rejects_code_outside_description():
    assert_that(
        On((400, 401), Fixed(Response(Text("")))).matches(402),
        is_(False),
        "On must reject codes outside its description",
    )


async def test_delegates_to_endpoint():
    assert_that(
        (
            await On(500, Fixed(Response(503, Text("down")))).response(
                Request(Get(), "/", Headers(), Empty()),
                Abort(500, "pool exhausted"),
            )
        ).status(),
        equal_to(503),
        "On must respond with its endpoint",
    )


async def test_hands_error_to_fallback():
    assert_that(
        await Body.Smart(
            (
                await On(..., Complaint()).response(
                    Request(Get(), "/", Headers(), Empty()),
                    Abort(418, "teapot is busy"),
                )
            ).body()
        ).text(),
        equal_to("teapot is busy"),
        "On must pass the error to a fallback that wants it",
    )
