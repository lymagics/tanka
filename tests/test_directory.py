import pathlib
import shutil

from hamcrest import assert_that, calling, equal_to, raises

from tanka.body import Body
from tanka.static import Directory


def scratch(name: str) -> pathlib.Path:
    folder = pathlib.Path(__file__).parent.parent / "tmp" / name
    shutil.rmtree(folder, ignore_errors=True)
    folder.mkdir(parents=True)
    return folder


async def test_serves_file_by_relative_path():
    folder = scratch("directory-file")
    (folder / "app.js").write_text("console.log(1)")
    assert_that(
        await Body.Smart(Directory(str(folder)).file("/app.js")).text(),
        equal_to("console.log(1)"),
        "Directory must serve a file under its root",
    )


async def test_serves_index_for_folder():
    folder = scratch("directory-index")
    (folder / "docs").mkdir()
    (folder / "docs" / "index.html").write_text("<h1>Docs</h1>")
    assert_that(
        await Body.Smart(Directory(str(folder)).file("/docs")).text(),
        equal_to("<h1>Docs</h1>"),
        "Directory must serve index.html for a folder",
    )


def test_refuses_path_outside_root():
    folder = scratch("directory-escape")
    (folder / "public").mkdir()
    (folder / "secret.txt").write_text("keys")
    assert_that(
        calling(Directory(str(folder / "public")).file).with_args(
            "/../secret.txt"
        ),
        raises(Exception, "absent"),
        "Directory must refuse paths escaping the root",
    )


def test_fails_on_missing_file():
    folder = scratch("directory-missing")
    assert_that(
        calling(Directory(str(folder)).file).with_args("/nothing.css"),
        raises(Exception, "absent"),
        "Directory must fail on a missing file",
    )
