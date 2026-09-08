from hamcrest import assert_that, equal_to

from tanka.cookies import Secure


def test_prints_secure_flag():
    assert_that(
        Secure().text(),
        equal_to("Secure"),
        "Secure must print the Secure flag",
    )
