import asyncio

from hamcrest import assert_that, calling, raises

from tanka.server import Once


async def program() -> None:
    raise RuntimeError("program ran once")


def test_runs_program_directly():
    assert_that(
        calling(asyncio.run).with_args(Once().serve(program())),
        raises(RuntimeError, "program ran once"),
        "Once must await the program in the current process",
    )
