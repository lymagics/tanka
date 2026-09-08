from hamcrest import assert_that, contains_exactly, equal_to

from tanka.identity import Principal


def test_exposes_its_id():
    assert_that(
        Principal("u-77").id(),
        equal_to("u-77"),
        "Principal must expose the given id",
    )


def test_lists_its_roles():
    assert_that(
        Principal("u-1", "editor", "viewer").roles(),
        contains_exactly("editor", "viewer"),
        "Principal must list the given roles in order",
    )
