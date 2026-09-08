from hamcrest import assert_that, equal_to

from tanka.cookies import Lifetime


def test_prints_max_age_attribute():
    assert_that(
        Lifetime(3600).text(),
        equal_to("Max-Age=3600"),
        "Lifetime must print the Max-Age attribute",
    )
