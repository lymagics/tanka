from hamcrest import assert_that, equal_to, instance_of

from fakes import Braces, Record
from tanka.body import Body, Html
from tanka.templates import Context, Pair, Template


async def test_builds_html_body():
    assert_that(
        await Template(Braces(), "{greeting}").html(
            Context(Pair("greeting", "hi"))
        ),
        instance_of(Html),
        "Template must build an Html body",
    )


async def test_renders_context_into_markup():
    assert_that(
        await Body.Smart(
            await Template(Braces(), "<h1>{title}</h1>").html(
                Context(Pair("title", "Welcome"))
            )
        ).text(),
        equal_to("<h1>Welcome</h1>"),
        "Template must render the context through its engine",
    )


async def test_declares_html_content_type():
    assert_that(
        (await Template(Braces(), "{n}").html(Context(Pair("n", 1))))
        .headers()
        .header("content-type"),
        equal_to("text/html; charset=utf-8"),
        "Template must declare an HTML content type",
    )


async def test_unwraps_json_readable_before_rendering():
    assert_that(
        await Body.Smart(
            await Template(Braces(), "<p>{user[name]}</p>").html(
                Context(Pair("user", Record({"name": "Bob"})))
            )
        ).text(),
        equal_to("<p>Bob</p>"),
        "Template must let the engine see the dict of a readable value",
    )


async def test_renders_with_empty_context():
    assert_that(
        await Body.Smart(
            await Template(Braces(), "static page").html(Context())
        ).text(),
        equal_to("static page"),
        "Template must render a template needing no values",
    )
