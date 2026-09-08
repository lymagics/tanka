from hamcrest import assert_that, is_

from tanka.catch import Listed


def test_matches_listed_code():
    assert_that(
        Listed(401, 403, 404).matches(403),
        is_(True),
        "Listed must match any listed code",
    )


def test_rejects_unlisted_code():
    assert_that(
        Listed(401, 403).matches(402),
        is_(False),
        "Listed must reject an unlisted code",
    )
