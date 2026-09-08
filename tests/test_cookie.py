from hamcrest import assert_that, equal_to

from tanka.cookies import Cookie, HttpOnly, SameSite, Secure


def test_prints_name_and_value_only():
    assert_that(
        Cookie("lang", "uk").text(),
        equal_to("lang=uk"),
        "Cookie without attributes must print name=value",
    )


def test_appends_attributes_in_order():
    assert_that(
        Cookie("sid", "42", HttpOnly(), Secure(), SameSite("Lax")).text(),
        equal_to("sid=42; HttpOnly; Secure; SameSite=Lax"),
        "Cookie must append attributes separated by semicolons",
    )
