import asyncio

from hamcrest import assert_that, calling, equal_to, raises

from fakes import Fixed
from tanka.abort import Abort
from tanka.auth import Authorized, Role
from tanka.body import Empty, Text
from tanka.headers import Headers
from tanka.identity import Principal
from tanka.method import Get
from tanka.request import Request
from tanka.response import Response


async def test_lets_matching_identity_through():
    assert_that(
        (
            await Authorized(
                Fixed(Response(200, Text("secret"))), Role("admin")
            ).response(
                Request(
                    Get(),
                    "/admin",
                    Headers(),
                    Empty(),
                    Principal("a", "admin"),
                )
            )
        ).status(),
        equal_to(200),
        "Authorized must delegate when the requirement is met",
    )


def test_forbids_identity_without_role():
    assert_that(
        calling(asyncio.run).with_args(
            Authorized(Fixed(Response(Text(""))), Role("admin")).response(
                Request(Get(), "/admin", Headers(), Empty(), Principal("b"))
            )
        ),
        raises(Abort, "does not meet"),
        "Authorized must abort with 403 when the requirement is not met",
    )


def test_forbids_anonymous_request():
    assert_that(
        calling(asyncio.run).with_args(
            Authorized(Fixed(Response(Text(""))), Role("any")).response(
                Request(Get(), "/", Headers(), Empty())
            )
        ),
        raises(Abort),
        "Authorized must abort for an anonymous request",
    )
