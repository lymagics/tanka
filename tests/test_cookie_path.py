from hamcrest import assert_that, equal_to

from tanka.cookies import CookiePath


def test_prints_path_attribute():
    assert_that(
        CookiePath("/admin").text(),
        equal_to("Path=/admin"),
        "CookiePath must print the Path attribute",
    )
