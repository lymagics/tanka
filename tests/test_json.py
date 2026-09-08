import json

from hamcrest import assert_that, equal_to, has_entries

from tanka.body import Body, Json


async def test_serializes_value():
    assert_that(
        json.loads(await Body.Smart(Json({"k": [1, None]})).text()),
        has_entries(k=[1, None]),
        "Json body must serialize the value as JSON",
    )


def test_declares_json_type():
    assert_that(
        Json([]).headers().header("content-type"),
        equal_to("application/json"),
        "Json body must declare a JSON content type",
    )
