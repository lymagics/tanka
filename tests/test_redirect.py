from hamcrest import assert_that, empty, equal_to

from tanka.response import Redirect


def test_points_to_location():
    assert_that(
        Redirect("/login").headers().header("location"),
        equal_to("/login"),
        "Redirect must set the location header",
    )


def test_uses_found_status_by_default():
    assert_that(
        Redirect("/home").status(),
        equal_to(302),
        "Redirect must default to 302",
    )


def test_keeps_given_status():
    assert_that(
        Redirect("/done", 303).status(),
        equal_to(303),
        "Redirect must keep the given status",
    )


async def test_has_empty_body():
    assert_that(
        [chunk async for chunk in Redirect("/").body().chunks()],
        empty(),
        "Redirect must have no body",
    )
