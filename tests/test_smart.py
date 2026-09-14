from hamcrest import assert_that, equal_to, has_entries, instance_of

from tanka.body import Body, Raw, Text


async def test_joins_chunks_into_bytes():
    assert_that(
        await Body.Smart(Raw(b"\x00\xff", "application/octet-stream")).bytes(),
        equal_to(b"\x00\xff"),
        "Smart body must join all chunks into bytes",
    )


async def test_decodes_text_with_declared_charset():
    assert_that(
        await Body.Smart(
            Raw("привіт".encode("cp1251"), "text/plain; charset=cp1251")
        ).text(),
        equal_to("привіт"),
        "Smart body must honour the charset from content-type",
    )


async def test_decodes_text_as_utf8_by_default():
    assert_that(
        await Body.Smart(Raw("ñ".encode(), "text/plain")).text(),
        equal_to("ñ"),
        "Smart body must default to UTF-8 without a charset",
    )


async def test_decodes_text_as_utf8_when_charset_parameter_is_empty():
    assert_that(
        await Body.Smart(Raw("café".encode(), "text/plain; charset=")).text(),
        equal_to("café"),
        "Smart body must default to UTF-8 when charset parameter is empty",
    )


async def test_parses_json():
    assert_that(
        await Body.Smart(Text('{"answer": 42, "ok": true}')).json(),
        has_entries(answer=42, ok=True),
        "Smart body must parse JSON from text",
    )


def test_delegates_headers_to_origin():
    assert_that(
        Body.Smart(Raw(b"abc", "text/csv")).headers().header("content-type"),
        equal_to("text/csv"),
        "Smart body must expose the headers of the origin",
    )


def test_counts_as_body():
    assert_that(
        Body.Smart(Text("x")),
        instance_of(Body),
        "Smart body must be usable wherever a Body is expected",
    )
