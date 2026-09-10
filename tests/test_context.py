from hamcrest import assert_that, empty, equal_to, has_entry

from fakes import Record
from tanka.templates import Context, Pair


async def test_maps_names_to_values():
    assert_that(
        await Context(Pair("title", "Account"), Pair("page", 3)).values(),
        equal_to({"title": "Account", "page": 3}),
        "Context must map every pair name to its value",
    )


async def test_has_no_values_when_built_empty():
    assert_that(
        await Context().values(),
        empty(),
        "Empty Context must have no values",
    )


async def test_lets_later_pair_win_over_earlier():
    assert_that(
        await Context(Pair("lang", "en"), Pair("lang", "uk")).values(),
        has_entry("lang", "uk"),
        "Context must let a later pair override an earlier one by name",
    )


async def test_unwraps_json_readable_values():
    assert_that(
        await Context(Pair("user", Record({"id": 7}))).values(),
        has_entry("user", has_entry("id", 7)),
        "Context must hand over the dict a readable value produces",
    )


async def test_builds_fresh_values_on_every_call():
    context = Context(Pair("count", 1))
    (await context.values()).clear()
    assert_that(
        await context.values(),
        has_entry("count", 1),
        "Context must stay unchanged when a caller mutates its values",
    )
