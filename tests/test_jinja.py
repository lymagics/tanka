import asyncio
import pathlib
import shutil

from hamcrest import (
    assert_that,
    calling,
    equal_to,
    has_property,
    instance_of,
    raises,
)
from jinja2 import DictLoader, Environment, TemplateNotFound

from tanka.body import Body
from tanka.jinja import Jinja
from tanka.templates import Context, Pair, Template


def scratch(name: str) -> pathlib.Path:
    folder = pathlib.Path(__file__).parent.parent / "tmp" / name
    shutil.rmtree(folder, ignore_errors=True)
    folder.mkdir(parents=True)
    return folder


async def test_renders_template_from_directory():
    folder = scratch("jinja-render")
    (folder / "hello.html").write_text(
        "<h1>{{ title }}</h1><p>Page {{ page }}</p>"
    )
    assert_that(
        await Jinja(str(folder)).markup(
            "hello.html", {"title": "Welcome", "page": 1}
        ),
        equal_to("<h1>Welcome</h1><p>Page 1</p>"),
        "Jinja must render a template found in its directory",
    )


async def test_escapes_markup_in_values():
    folder = scratch("jinja-escape")
    (folder / "unsafe.html").write_text("{{ text }}")
    assert_that(
        await Jinja(str(folder)).markup("unsafe.html", {"text": "<b>&</b>"}),
        equal_to("&lt;b&gt;&amp;&lt;/b&gt;"),
        "Jinja must escape values rendered into an HTML template",
    )


async def test_reaches_nested_values():
    folder = scratch("jinja-nested")
    (folder / "card.html").write_text("{{ user.name }} ({{ user.id }})")
    assert_that(
        await Jinja(str(folder)).markup(
            "card.html", {"user": {"name": "Ann", "id": 42}}
        ),
        equal_to("Ann (42)"),
        "Jinja must reach nested dict values by attribute syntax",
    )


async def test_renders_page_through_template():
    folder = scratch("jinja-template")
    (folder / "index.html").write_text(
        "<h1>{{ title }}</h1>\n<p>Page {{ page }}</p>"
    )
    assert_that(
        await Body.Smart(
            await Template(Jinja(str(folder)), "index.html").html(
                Context(Pair("title", "Welcome"), Pair("page", 1))
            )
        ).text(),
        equal_to("<h1>Welcome</h1>\n<p>Page 1</p>"),
        "Jinja must serve as the engine behind Template",
    )


def test_fails_on_missing_template():
    folder = scratch("jinja-missing")
    assert_that(
        calling(asyncio.run).with_args(
            Jinja(str(folder)).markup("ghost.html", {})
        ),
        raises(
            Exception,
            "Can't render",
            matching=has_property("__cause__", instance_of(TemplateNotFound)),
        ),
        "Jinja must fail with an exception chained from the engine error",
    )


def test_fails_on_broken_template():
    folder = scratch("jinja-broken")
    (folder / "broken.html").write_text("{% if %}")
    assert_that(
        calling(asyncio.run).with_args(
            Jinja(str(folder)).markup("broken.html", {})
        ),
        raises(Exception, "Can't render"),
        "Jinja must fail on a template with a syntax error",
    )


async def test_accepts_ready_environment():
    assert_that(
        await Jinja(
            Environment(loader=DictLoader({"twice.txt": "{{ n * 2 }}"}))
        ).markup("twice.txt", {"n": 21}),
        equal_to("42"),
        "Jinja must render through a ready environment",
    )
