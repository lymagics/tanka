from hamcrest import assert_that, equal_to

from tanka.flash import Named


def test_keeps_given_name():
    assert_that(
        Named("custom-kind").name(),
        equal_to("custom-kind"),
        "Named kind must keep the given name",
    )
