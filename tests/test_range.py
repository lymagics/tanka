import pytest
from hamcrest import assert_that, is_

from tanka.catch import Range


@pytest.mark.parametrize("code", [500, 542, 599])
def test_matches_code_inside_bounds(code):
    assert_that(
        Range(500, 599).matches(code),
        is_(True),
        "Range must match codes within inclusive bounds",
    )


@pytest.mark.parametrize("code", [499, 600])
def test_rejects_code_outside_bounds(code):
    assert_that(
        Range(500, 599).matches(code),
        is_(False),
        "Range must reject codes outside the bounds",
    )
