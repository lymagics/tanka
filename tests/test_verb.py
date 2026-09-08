from hamcrest import assert_that, contains_exactly

from tanka.method import Verb


def test_upper_cases_custom_name():
    assert_that(
        Verb("purge").names(),
        contains_exactly("PURGE"),
        "Verb must normalize its name to upper case",
    )
