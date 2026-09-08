from hamcrest import assert_that, is_

from tanka.auth import Roles
from tanka.identity import Principal


def test_matches_identity_with_any_listed_role():
    assert_that(
        Roles("owner", "editor").matches(Principal("3", "editor")),
        is_(True),
        "Roles must match when the identity holds any listed role",
    )


def test_rejects_identity_with_no_listed_role():
    assert_that(
        Roles("owner", "editor").matches(Principal("4", "viewer")),
        is_(False),
        "Roles must reject when no listed role is held",
    )


def test_rejects_everyone_when_empty():
    assert_that(
        Roles().matches(Principal("5", "root")),
        is_(False),
        "Empty Roles must match nobody",
    )
