from hamcrest import assert_that, equal_to

from tanka.flash import Failure


def test_names_itself_failure():
    assert_that(
        Failure().name(),
        equal_to("failure"),
        "Failure kind must be named failure",
    )
