from hamcrest import assert_that, none

from tanka.application import Silence


def test_swallows_message():
    assert_that(
        Silence().write("ignored"),
        none(),
        "Silence must accept a message and do nothing",
    )
