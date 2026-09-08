import asyncio
import pathlib
import shutil

from hamcrest import assert_that, calling, equal_to, raises

from tanka.abort import Abort
from tanka.body import Body, Empty
from tanka.headers import Headers
from tanka.method import Get
from tanka.request import Request
from tanka.routes import Mount
from tanka.static import Directory, Static


def scratch(name: str) -> pathlib.Path:
    folder = pathlib.Path(__file__).parent.parent / "tmp" / name
    shutil.rmtree(folder, ignore_errors=True)
    folder.mkdir(parents=True)
    return folder


async def test_serves_existing_file():
    folder = scratch("static-file")
    (folder / "logo.svg").write_text("<svg/>")
    assert_that(
        await Body.Smart(
            (
                await Static(Directory(str(folder))).response(
                    Request(Get(), "/logo.svg", Headers(), Empty())
                )
            ).body()
        ).text(),
        equal_to("<svg/>"),
        "Static must serve a file from its source",
    )


async def test_serves_under_mount_prefix():
    folder = scratch("static-mount")
    (folder / "a.txt").write_text("A")
    assert_that(
        (
            await Mount("/assets", Static(Directory(str(folder)))).response(
                Request(Get(), "/assets/a.txt", Headers(), Empty())
            )
        )
        .body()
        .headers()
        .header("content-type"),
        equal_to("text/plain"),
        "Static must resolve files relative to the mount prefix",
    )


def test_aborts_with_not_found_for_missing_file():
    folder = scratch("static-missing")
    assert_that(
        calling(asyncio.run).with_args(
            Static(Directory(str(folder))).response(
                Request(Get(), "/absent.png", Headers(), Empty())
            )
        ),
        raises(Abort, "absent"),
        "Static must abort with 404 for a missing file",
    )
