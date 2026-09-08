from hamcrest import assert_that, calling, equal_to, raises

from tanka.target import Path


def test_extracts_named_parameter():
    assert_that(
        Path("/users/42/posts/7", "/users/{user}/posts/{post}").parameter(
            "post"
        ),
        equal_to("7"),
        "Path must extract a named parameter from the pattern",
    )


def test_converts_typed_parameter():
    assert_that(
        Path("/items/13", "/items/{id:d}").parameter("id"),
        equal_to(13),
        "Path must delegate typed parameters to the parse library",
    )


def test_fails_on_unknown_parameter():
    assert_that(
        calling(Path("/books/9", "/books/{id}").parameter).with_args("isbn"),
        raises(Exception, "absent"),
        "Path must fail on a parameter missing from the pattern",
    )


def test_fails_when_pattern_does_not_match():
    assert_that(
        calling(Path("/cars", "/bikes/{id}").parameter).with_args("id"),
        raises(Exception, "does not match"),
        "Path must fail when the text does not match the pattern",
    )


def test_prints_its_text():
    assert_that(
        str(Path("/a/b%20c")),
        equal_to("/a/b%20c"),
        "Path must print the raw text",
    )
