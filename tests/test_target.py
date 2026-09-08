from hamcrest import assert_that, equal_to

from tanka.target import Path, Query, Target


def test_splits_path_from_query():
    assert_that(
        str(Target("/users?page=2&size=10").path()),
        equal_to("/users"),
        "Target must split the path before the question mark",
    )


def test_keeps_query_after_question_mark():
    assert_that(
        Target("/search?q=a?b").query().parameter("q"),
        equal_to("a?b"),
        "Target must split only on the first question mark",
    )


def test_prints_path_without_empty_query():
    assert_that(
        str(Target(Path("/plain"), Query(""))),
        equal_to("/plain"),
        "Target must omit the question mark when the query is empty",
    )


def test_prints_path_with_query():
    assert_that(
        str(Target(Path("/list"), Query("sort=asc"))),
        equal_to("/list?sort=asc"),
        "Target must print path and query joined by a question mark",
    )
