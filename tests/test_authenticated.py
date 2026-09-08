import asyncio
import json

from hamcrest import assert_that, calling, has_entry, raises

from fakes import Echo, Known
from tanka.abort import Abort
from tanka.auth import Authenticated, IdentitySource
from tanka.body import Body, Empty
from tanka.headers import Headers
from tanka.identity import Identity, Principal
from tanka.method import Get
from tanka.request import Request


class Refusing(IdentitySource):
    async def identity(self, request: Request) -> Identity:
        raise Abort(401, "Token is missing")


async def test_attaches_identity_to_request():
    assert_that(
        json.loads(
            await Body.Smart(
                (
                    await Authenticated(
                        Echo(), Known(Principal("u", "staff"))
                    ).response(Request(Get(), "/", Headers(), Empty()))
                ).body()
            ).text()
        ),
        has_entry("roles", ["staff"]),
        "Authenticated must pass the identity to the wrapped endpoint",
    )


def test_lets_abort_of_source_propagate():
    assert_that(
        calling(asyncio.run).with_args(
            Authenticated(Echo(), Refusing()).response(
                Request(Get(), "/", Headers(), Empty())
            )
        ),
        raises(Abort, "Token is missing"),
        "Authenticated must not swallow Abort from the identity source",
    )
