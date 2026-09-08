from hamcrest import assert_that, contains_exactly

from tanka.method import Head


def test_names_itself_head():
    assert_that(
        Head().names(),
        contains_exactly("HEAD"),
        "Head must expose a single HEAD name",
    )
