from hamcrest import assert_that, equal_to

from tanka.cookies import CookiePath, ForgetCookie


def test_expires_cookie_immediately():
    assert_that(
        ForgetCookie("session").text(),
        equal_to("session=; Max-Age=0"),
        "ForgetCookie must blank the value and set a zero lifetime",
    )


def test_keeps_extra_attributes():
    assert_that(
        ForgetCookie("cart", CookiePath("/shop")).text(),
        equal_to("cart=; Max-Age=0; Path=/shop"),
        "ForgetCookie must append given attributes",
    )
