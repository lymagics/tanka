from hamcrest import assert_that, is_
from hypothesis import given
from hypothesis import strategies as st

from tanka.catch import Every


@given(st.integers())
def test_matches_any_code(code):
    assert_that(
        Every().matches(code),
        is_(True),
        "Every must match any code",
    )
