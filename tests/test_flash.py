from hamcrest import assert_that, equal_to

from tanka.flash import Alert, Flash


def test_exposes_text():
    assert_that(
        Flash("Disk is almost full", Alert()).text(),
        equal_to("Disk is almost full"),
        "Flash must expose its text",
    )


def test_exposes_kind():
    assert_that(
        Flash("Careful", Alert()).kind().name(),
        equal_to("alert"),
        "Flash must expose its kind",
    )
