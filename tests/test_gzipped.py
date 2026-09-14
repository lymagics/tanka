import gzip

from hamcrest import assert_that, empty, equal_to

from tanka.body import Body, Gzipped, Html, Raw, Stream


async def pieces():
    yield b"alpha,"
    yield b""
    yield b"omega"


async def test_compresses_bytes_of_origin():
    assert_that(
        gzip.decompress(
            await Body.Smart(Gzipped(Html("<p>zip me</p>"))).bytes()
        ),
        equal_to(b"<p>zip me</p>"),
        "Gzipped body must decompress back to the origin bytes",
    )


async def test_compresses_stream_without_buffering_it_first():
    assert_that(
        gzip.decompress(
            await Body.Smart(Gzipped(Stream(pieces(), "text/csv"))).bytes()
        ),
        equal_to(b"alpha,omega"),
        "Gzipped body must compress every chunk of a stream",
    )


def test_declares_gzip_encoding():
    assert_that(
        Gzipped(Raw(b"\x00\xff", "x/y")).headers().header("content-encoding"),
        equal_to("gzip"),
        "Gzipped body must declare gzip content encoding",
    )


def test_drops_length_of_origin():
    assert_that(
        Gzipped(Raw(b"1234567", "a/b")).headers().values("content-length"),
        empty(),
        "Gzipped body must not declare the length of the origin",
    )


def test_keeps_type_of_origin():
    assert_that(
        Gzipped(Raw(b"{}", "application/vnd.api+json"))
        .headers()
        .header("content-type"),
        equal_to("application/vnd.api+json"),
        "Gzipped body must keep the content type of the origin",
    )
