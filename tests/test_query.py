from hamcrest import assert_that, calling, contains_exactly, equal_to, raises

from tanka.target import Query


def test_reads_first_value_of_parameter():
    assert_that(
        Query("page=3&page=4").parameter("page"),
        equal_to("3"),
        "Query must return the first value of a repeated parameter",
    )


def test_decodes_encoded_value():
    assert_that(
        Query("q=caf%C3%A9+au+lait").parameter("q"),
        equal_to("café au lait"),
        "Query must decode percent-encoded values",
    )


def test_keeps_blank_value():
    assert_that(
        Query("flag=&other=1").values("flag"),
        contains_exactly(""),
        "Query must keep blank values",
    )


def test_fails_on_absent_parameter():
    assert_that(
        calling(Query("a=1").parameter).with_args("b"),
        raises(Exception, "absent"),
        "Query must fail fast on a missing parameter",
    )


def test_prints_raw_text():
    assert_that(
        str(Query("x=1&y=2")),
        equal_to("x=1&y=2"),
        "Query must print the raw text",
    )
