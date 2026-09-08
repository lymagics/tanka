from hamcrest import assert_that, equal_to

from tanka.flash import Alert


def test_names_itself_alert():
    assert_that(
        Alert().name(),
        equal_to("alert"),
        "Alert kind must be named alert",
    )
