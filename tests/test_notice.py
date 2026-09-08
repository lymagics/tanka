from hamcrest import assert_that, equal_to

from tanka.flash import Notice


def test_names_itself_notice():
    assert_that(
        Notice().name(),
        equal_to("notice"),
        "Notice kind must be named notice",
    )
