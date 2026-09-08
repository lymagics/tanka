from hamcrest import assert_that, is_

from tanka.auth import Role
from tanka.identity import Anonymous, Principal


def test_matches_identity_with_role():
    assert_that(
        Role("admin").matches(Principal("1", "user", "admin")),
        is_(True),
        "Role must match an identity holding the role",
    )


def test_rejects_identity_without_role():
    assert_that(
        Role("admin").matches(Principal("2", "user")),
        is_(False),
        "Role must reject an identity lacking the role",
    )


def test_rejects_anonymous():
    assert_that(
        Role("guest").matches(Anonymous()),
        is_(False),
        "Role must reject an anonymous identity",
    )
