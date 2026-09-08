from hamcrest import assert_that, contains_exactly, empty

from tanka.method import Get, Head, Methods, Verb


def test_joins_names_of_nested_methods():
    assert_that(
        Methods(Get(), Head(), Verb("link")).names(),
        contains_exactly("GET", "HEAD", "LINK"),
        "Methods must concatenate names of nested methods in order",
    )


def test_has_no_names_when_empty():
    assert_that(
        Methods().names(),
        empty(),
        "Empty Methods must expose no names",
    )
