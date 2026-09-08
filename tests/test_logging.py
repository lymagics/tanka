import logging

from hamcrest import assert_that, has_item

from tanka.application import Logging


def test_writes_error_to_named_logger(caplog):
    with caplog.at_level(logging.ERROR, logger="tanka.probe"):
        Logging("tanka.probe").write("something broke")
    assert_that(
        [record.getMessage() for record in caplog.records],
        has_item("something broke"),
        "Logging must write the message to the named logger",
    )
