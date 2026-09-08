import pathlib
import shutil

from hamcrest import assert_that, calling, has_entry, raises

from tanka.openapi import Document


def scratch(name: str) -> pathlib.Path:
    folder = pathlib.Path(__file__).parent.parent / "tmp" / name
    shutil.rmtree(folder, ignore_errors=True)
    folder.mkdir(parents=True)
    return folder


def test_reads_yaml_file():
    folder = scratch("document-yaml")
    (folder / "api.yaml").write_text("openapi: 3.0.3\ninfo:\n  title: Y\n")
    assert_that(
        Document(str(folder / "api.yaml")).content(),
        has_entry("openapi", "3.0.3"),
        "Document must parse a YAML specification",
    )


def test_reads_json_file():
    folder = scratch("document-json")
    (folder / "api.json").write_text('{"openapi": "3.1.0", "paths": {}}')
    assert_that(
        Document(str(folder / "api.json")).content(),
        has_entry("openapi", "3.1.0"),
        "Document must parse a JSON specification",
    )


def test_fails_on_missing_file():
    folder = scratch("document-missing")
    assert_that(
        calling(Document(str(folder / "ghost.yaml")).content),
        raises(Exception, "Can't read"),
        "Document must fail fast on a missing file",
    )
