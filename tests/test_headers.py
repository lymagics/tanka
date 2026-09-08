import pytest
from hamcrest import (
    assert_that,
    calling,
    contains_exactly,
    empty,
    equal_to,
    raises,
)
from hypothesis import given
from hypothesis import strategies as st

from tanka.headers import Headers


def test_finds_header_ignoring_case():
    assert_that(
        Headers({"Content-Type": "text/csv"}).header("content-TYPE"),
        equal_to("text/csv"),
        "Headers must match names case-insensitively",
    )


def test_fails_on_absent_header():
    assert_that(
        calling(Headers([("x-one", "1")]).header).with_args("x-two"),
        raises(Exception, "absent"),
        "Headers must fail fast on a missing header",
    )


def test_lists_all_values_of_repeated_header():
    assert_that(
        Headers([("set-cookie", "a=1"), ("set-cookie", "b=2")]).values(
            "Set-Cookie"
        ),
        contains_exactly("a=1", "b=2"),
        "Headers must keep every value of a repeated header",
    )


def test_has_no_values_when_built_empty():
    assert_that(
        Headers().values("accept"),
        empty(),
        "Empty Headers must have no values",
    )


def test_iterates_pairs_in_given_order():
    assert_that(
        list(Headers([("b", "2"), ("a", "1")])),
        contains_exactly(("b", "2"), ("a", "1")),
        "Headers must preserve insertion order",
    )


@pytest.mark.parametrize(
    "source",
    [{"x-token": "abc"}, [("x-token", "abc")], (("x-token", "abc"),)],
)
def test_reads_header_from_any_source(source):
    assert_that(
        Headers(source).header("x-token"),
        equal_to("abc"),
        "Headers must accept dict, list and tuple sources",
    )


@given(st.text(min_size=1), st.text())
def test_returns_any_stored_value(name, value):
    assert_that(
        Headers([(name, value)]).header(name),
        equal_to(value),
        "Headers must return the exact value stored under a name",
    )
