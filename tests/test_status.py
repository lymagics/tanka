import pytest
from hamcrest import assert_that, calling, equal_to, raises

from tanka.abort import Status


def test_names_teapot():
    assert_that(
        Status(418).phrase(),
        equal_to("I'm a Teapot"),
        "Status must give the standard phrase",
    )


def test_returns_supported_code():
    assert_that(
        Status(451).code(),
        equal_to(451),
        "Status must return a supported code unchanged",
    )


@pytest.mark.parametrize("code", [200, 302, 402, 425, 507, 999])
def test_rejects_unsupported_code(code):
    assert_that(
        calling(Status(code).code),
        raises(Exception, "not supported"),
        "Status must reject codes outside the supported table",
    )
