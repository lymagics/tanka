from hamcrest import assert_that, equal_to

from tanka.flash import Success


def test_names_itself_success():
    assert_that(
        Success().name(),
        equal_to("success"),
        "Success kind must be named success",
    )
