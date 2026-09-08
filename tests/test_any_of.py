from hamcrest import assert_that, is_

from tanka.auth import AnyOf, Role
from tanka.identity import Principal


def test_matches_when_one_requirement_matches():
    assert_that(
        AnyOf(Role("a"), Role("b")).matches(Principal("6", "b")),
        is_(True),
        "AnyOf must match when at least one requirement matches",
    )


def test_rejects_when_none_matches():
    assert_that(
        AnyOf(Role("a"), Role("b")).matches(Principal("7", "c")),
        is_(False),
        "AnyOf must reject when no requirement matches",
    )
