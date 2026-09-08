from hamcrest import assert_that, contains_exactly

from tanka.method import Patch


def test_names_itself_patch():
    assert_that(
        Patch().names(),
        contains_exactly("PATCH"),
        "Patch must expose a single PATCH name",
    )
