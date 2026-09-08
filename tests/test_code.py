from hamcrest import assert_that, is_

from tanka.catch import Code


def test_matches_equal_code():
    assert_that(
        Code(404).matches(404),
        is_(True),
        "Code must match the same code",
    )


def test_rejects_other_code():
    assert_that(
        Code(404).matches(403),
        is_(False),
        "Code must reject a different code",
    )
