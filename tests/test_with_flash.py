from hamcrest import assert_that, equal_to, starts_with

from tanka.body import Body, Text
from tanka.flash import Flash, Success, WithFlash
from tanka.response import Redirect, Response


def test_stores_flash_in_cookie():
    assert_that(
        WithFlash(Redirect("/users"), Flash("User created", Success()))
        .headers()
        .header("set-cookie"),
        starts_with("flash="),
        "WithFlash must store the flash in a cookie named flash",
    )


def test_scopes_cookie_to_root_path():
    assert_that(
        WithFlash(Redirect("/"), Flash("Saved", Success()))
        .headers()
        .header("set-cookie"),
        equal_to(
            "flash=%7B%22text%22%3A%20%22Saved%22%2C%20%22kind%22%3A%20"
            "%22success%22%7D; Path=/; HttpOnly"
        ),
        "WithFlash must encode the flash and scope the cookie to /",
    )


def test_keeps_status():
    assert_that(
        WithFlash(Redirect("/", 303), Flash("Done", Success())).status(),
        equal_to(303),
        "WithFlash must keep the status of the origin",
    )


async def test_keeps_body():
    assert_that(
        await Body.Smart(
            WithFlash(Response(Text("page")), Flash("Hi", Success())).body()
        ).text(),
        equal_to("page"),
        "WithFlash must keep the body of the origin",
    )
