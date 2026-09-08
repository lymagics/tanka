from hamcrest import assert_that, equal_to

from fakes import Fixed
from tanka.abort import Abort
from tanka.body import Empty, Text
from tanka.catch import Indifferent
from tanka.headers import Headers
from tanka.method import Get
from tanka.request import Request
from tanka.response import Response


async def test_answers_with_endpoint_whatever_the_error():
    assert_that(
        (
            await Indifferent(Fixed(Response(410, Text("gone")))).response(
                Request(Get(), "/", Headers(), Empty()),
                Abort(503, "disk on fire"),
            )
        ).status(),
        equal_to(410),
        "Indifferent must answer with its endpoint regardless of the error",
    )
