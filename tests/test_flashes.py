from hamcrest import assert_that, contains_exactly, empty, equal_to

from tanka.cookies import Cookies
from tanka.flash import Failure, Flash, Flashes, WithFlash
from tanka.response import Redirect


def test_reads_flash_written_by_with_flash():
    assert_that(
        [
            flash.text()
            for flash in Flashes(
                Cookies(
                    WithFlash(
                        Redirect("/"), Flash("Wrong password", Failure())
                    )
                    .headers()
                    .header("set-cookie")
                    .split(";")[0]
                )
            )
        ],
        contains_exactly("Wrong password"),
        "Flashes must decode a flash written by WithFlash",
    )


def test_restores_kind_by_name():
    assert_that(
        next(
            iter(
                Flashes(
                    Cookies(
                        "flash=%7B%22text%22%3A%20%22x%22%2C%20%22kind%22%3A"
                        "%20%22failure%22%7D"
                    )
                )
            )
        )
        .kind()
        .name(),
        equal_to("failure"),
        "Flashes must restore the kind name",
    )


def test_finds_nothing_without_flash_cookie():
    assert_that(
        list(Flashes(Cookies("session=abc; theme=dark"))),
        empty(),
        "Flashes must be empty when no flash cookie exists",
    )
