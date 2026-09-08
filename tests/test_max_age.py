from hamcrest import assert_that, empty, equal_to

from tanka.body import Empty
from tanka.cors import MaxAge
from tanka.headers import Headers
from tanka.method import Get, Options
from tanka.request import Request


def test_sets_max_age_on_preflight():
    assert_that(
        MaxAge(600)
        .headers(
            Request(
                Options(),
                "/",
                Headers(
                    {
                        "origin": "https://age.example",
                        "access-control-request-method": "PATCH",
                    }
                ),
                Empty(),
            )
        )
        .header("access-control-max-age"),
        equal_to("600"),
        "MaxAge must set the max age on preflight",
    )


def test_stays_silent_on_actual_request():
    assert_that(
        list(MaxAge(5).headers(Request(Get(), "/", Headers(), Empty()))),
        empty(),
        "MaxAge must add nothing to an actual request",
    )
