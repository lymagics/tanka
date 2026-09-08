from hamcrest import assert_that, calling, equal_to, raises

from tanka.abort import Abort


def test_exposes_status():
    assert_that(
        Abort(409, "Already taken").status(),
        equal_to(409),
        "Abort must expose its status code",
    )


def test_prints_message():
    assert_that(
        str(Abort(410, "Gone fishing")),
        equal_to("Gone fishing"),
        "Abort must print the given message",
    )


def test_uses_phrase_as_default_message():
    assert_that(
        str(Abort(503)),
        equal_to("Service Unavailable"),
        "Abort must default its message to the status phrase",
    )


def test_breaks_on_unsupported_code():
    assert_that(
        calling(Abort(200, "fine").status),
        raises(Exception, "not supported"),
        "Abort must refuse a non-error status code",
    )
