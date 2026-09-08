from hamcrest import assert_that, contains_exactly

from tanka.method import Post


def test_names_itself_post():
    assert_that(
        Post().names(),
        contains_exactly("POST"),
        "Post must expose a single POST name",
    )
