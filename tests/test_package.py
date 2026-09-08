from hamcrest import assert_that, calling, equal_to, raises

import tanka


def test_exports_open_api_lazily():
    assert_that(
        tanka.OpenApi.__name__,
        equal_to("OpenApi"),
        "Package must expose OpenApi without importing it eagerly",
    )


def test_rejects_unknown_attribute():
    assert_that(
        calling(getattr).with_args(tanka, "Teapot"),
        raises(AttributeError, "no attribute 'Teapot'"),
        "Package must fail on an unknown attribute",
    )
