import asyncio

from hamcrest import assert_that, calling, contains_exactly, equal_to, raises

from tanka.asgi import AsgiBody
from tanka.body import Body
from tanka.headers import Headers


class Feed:
    def __init__(self, messages: list[dict]):
        self.messages = list(messages)

    async def __call__(self) -> dict:
        return self.messages.pop(0)


async def test_joins_chunks_until_last_message():
    assert_that(
        await Body.Smart(
            AsgiBody(
                Feed(
                    [
                        {
                            "type": "http.request",
                            "body": b"ab",
                            "more_body": True,
                        },
                        {"type": "http.request", "body": b"cd"},
                    ]
                ),
                Headers(),
            )
        ).bytes(),
        equal_to(b"abcd"),
        "AsgiBody must read messages until more_body is false",
    )


def test_keeps_only_content_headers():
    assert_that(
        list(
            AsgiBody(
                Feed([]),
                Headers(
                    [
                        ("host", "x"),
                        ("Content-Type", "text/csv"),
                        ("content-length", "3"),
                    ]
                ),
            ).headers()
        ),
        contains_exactly(
            ("Content-Type", "text/csv"), ("content-length", "3")
        ),
        "AsgiBody must expose only headers describing the body",
    )


def test_refuses_second_read():
    body = AsgiBody(Feed([{"type": "http.request", "body": b"1"}]), Headers())
    asyncio.run(Body.Smart(body).bytes())
    assert_that(
        calling(asyncio.run).with_args(Body.Smart(body).bytes()),
        raises(Exception, "already been consumed"),
        "AsgiBody must fail fast when read twice",
    )


def test_fails_on_disconnect():
    assert_that(
        calling(asyncio.run).with_args(
            Body.Smart(
                AsgiBody(Feed([{"type": "http.disconnect"}]), Headers())
            ).bytes()
        ),
        raises(Exception, "disconnected"),
        "AsgiBody must fail when the client disconnects",
    )
