import asyncio

import pytest
from hamcrest import (
    assert_that,
    contains_exactly,
    equal_to,
    has_entry,
    instance_of,
)
from hypothesis import given
from hypothesis import strategies as st

from fakes import Record, Sheet
from tanka.templates import Pair


async def test_replaces_json_readable_with_its_dict():
    assert_that(
        await Pair("user", Record({"name": "Ann", "id": 42})).entry(),
        contains_exactly("user", has_entry("name", "Ann")),
        "Pair must replace a value offering json() by the dict it returns",
    )


async def test_passes_value_with_plain_json_method_through_unchanged():
    assert_that(
        await Pair("row", Sheet({"total": 13.5, "unit": "kg"})).entry(),
        contains_exactly("row", instance_of(Sheet)),
        "Pair must pass a value with a plain json() method through unchanged",
    )


async def test_passes_dict_through_unchanged():
    assert_that(
        await Pair("meta", {"json": "not a method"}).entry(),
        contains_exactly("meta", equal_to({"json": "not a method"})),
        "Pair must not treat a dict with a json key as readable",
    )


@pytest.mark.parametrize(
    "value",
    ["Welcome", 0, -2.5, [1, "two"], b"raw", ("a", "b")],
)
async def test_passes_plain_value_through_unchanged(value):
    assert_that(
        await Pair("plain", value).entry(),
        contains_exactly("plain", value),
        "Pair must pass a plain value through unchanged",
    )


@given(st.text(min_size=1), st.one_of(st.integers(), st.text()))
def test_keeps_any_name_and_value(name, value):
    assert_that(
        asyncio.run(Pair(name, value).entry()),
        equal_to((name, value)),
        "Pair must keep the exact name and value it was given",
    )
