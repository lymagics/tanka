from hamcrest import assert_that, empty, equal_to

from tanka.body import Empty


async def test_yields_no_chunks():
    assert_that(
        [chunk async for chunk in Empty().chunks()],
        empty(),
        "Empty body must yield nothing",
    )


def test_declares_zero_length():
    assert_that(
        Empty().headers().header("content-length"),
        equal_to("0"),
        "Empty body must declare a zero content length",
    )
