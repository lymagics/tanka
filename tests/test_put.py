from hamcrest import assert_that, contains_exactly

from tanka.method import Put


def test_names_itself_put():
    assert_that(
        Put().names(),
        contains_exactly("PUT"),
        "Put must expose a single PUT name",
    )
