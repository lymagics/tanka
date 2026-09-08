from hamcrest import assert_that, equal_to

from tanka.cookies import SameSite


def test_prints_same_site_policy():
    assert_that(
        SameSite("Strict").text(),
        equal_to("SameSite=Strict"),
        "SameSite must print its policy",
    )
