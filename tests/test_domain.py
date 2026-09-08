from hamcrest import assert_that, equal_to

from tanka.cookies import Domain


def test_prints_domain_attribute():
    assert_that(
        Domain("example.org").text(),
        equal_to("Domain=example.org"),
        "Domain must print the Domain attribute",
    )
