from hamcrest import assert_that, equal_to

from tanka.body import Empty
from tanka.cors import AllowCredentials
from tanka.headers import Headers
from tanka.method import Get
from tanka.request import Request


def test_allows_credentials():
    assert_that(
        AllowCredentials()
        .headers(Request(Get(), "/", Headers(), Empty()))
        .header("access-control-allow-credentials"),
        equal_to("true"),
        "AllowCredentials must always allow credentials",
    )
