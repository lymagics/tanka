from hamcrest import assert_that, is_

from tanka.auth import AllOf, Role
from tanka.identity import Principal


def test_matches_when_every_requirement_matches():
    assert_that(
        AllOf(Role("x"), Role("y")).matches(Principal("8", "y", "x")),
        is_(True),
        "AllOf must match when every requirement matches",
    )


def test_rejects_when_one_requirement_fails():
    assert_that(
        AllOf(Role("x"), Role("y")).matches(Principal("9", "x")),
        is_(False),
        "AllOf must reject when any requirement fails",
    )
