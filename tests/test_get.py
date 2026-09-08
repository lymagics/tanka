from hamcrest import assert_that, contains_exactly

from tanka.method import Get


def test_names_itself_get():
    assert_that(
        Get().names(),
        contains_exactly("GET"),
        "Get must expose a single GET name",
    )
