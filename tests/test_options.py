from hamcrest import assert_that, contains_exactly

from tanka.method import Options


def test_names_itself_options():
    assert_that(
        Options().names(),
        contains_exactly("OPTIONS"),
        "Options must expose a single OPTIONS name",
    )
