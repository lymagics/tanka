from hamcrest import assert_that, calling, empty, raises

from tanka.identity import Anonymous


def test_refuses_to_tell_id():
    assert_that(
        calling(Anonymous().id),
        raises(Exception, "not authenticated"),
        "Anonymous identity must fail fast on id",
    )


def test_has_no_roles():
    assert_that(
        Anonymous().roles(),
        empty(),
        "Anonymous identity must have no roles",
    )
