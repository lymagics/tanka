import asyncio
import pathlib
import shutil

from hamcrest import assert_that, calling, equal_to, raises

from tanka.body import Body, File


def scratch(name: str) -> pathlib.Path:
    folder = pathlib.Path(__file__).parent.parent / "tmp" / name
    shutil.rmtree(folder, ignore_errors=True)
    folder.mkdir(parents=True)
    return folder


async def test_streams_file_content():
    folder = scratch("file-content")
    (folder / "data.bin").write_bytes(b"\x00" * 70000 + b"\x01")
    assert_that(
        await Body.Smart(File(str(folder / "data.bin"))).bytes(),
        equal_to(b"\x00" * 70000 + b"\x01"),
        "File body must stream the whole file in chunks",
    )


def test_guesses_mime_from_extension():
    folder = scratch("file-mime")
    (folder / "style.css").write_text("body{}")
    assert_that(
        File(str(folder / "style.css")).headers().header("content-type"),
        equal_to("text/css"),
        "File body must guess the content type from the extension",
    )


def test_falls_back_to_octet_stream():
    folder = scratch("file-unknown")
    (folder / "blob.unknownext").write_bytes(b"?")
    assert_that(
        File(str(folder / "blob.unknownext")).headers().header("content-type"),
        equal_to("application/octet-stream"),
        "File body must fall back to a binary content type",
    )


def test_declares_size_of_file():
    folder = scratch("file-size")
    (folder / "n.txt").write_text("12345678")
    assert_that(
        File(str(folder / "n.txt")).headers().header("content-length"),
        equal_to("8"),
        "File body must declare the file size",
    )


def test_fails_on_missing_file_headers():
    folder = scratch("file-missing")
    assert_that(
        calling(File(str(folder / "ghost.txt")).headers),
        raises(Exception, "Can't read"),
        "File body must fail fast when the file is absent",
    )


def test_fails_on_missing_file_chunks():
    folder = scratch("file-missing-chunks")
    assert_that(
        calling(asyncio.run).with_args(
            Body.Smart(File(str(folder / "ghost.bin"))).bytes()
        ),
        raises(Exception, "Can't open"),
        "File body must fail fast when streaming an absent file",
    )
