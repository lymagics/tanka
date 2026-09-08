from hamcrest import assert_that, contains_exactly

from tanka.method import Delete


def test_names_itself_delete():
    assert_that(
        Delete().names(),
        contains_exactly("DELETE"),
        "Delete must expose a single DELETE name",
    )
