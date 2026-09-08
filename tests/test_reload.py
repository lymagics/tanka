import asyncio

from hamcrest import assert_that, calling, contains_string, raises

from tanka.server import Reload


async def program() -> None:
    raise RuntimeError("program ran in child")


def test_runs_program_in_child_process(monkeypatch):
    monkeypatch.setenv("TANKA_RELOAD", "child")
    assert_that(
        calling(asyncio.run).with_args(Reload().serve(program())),
        raises(RuntimeError, "program ran in child"),
        "Reload must run the program when it is the child process",
    )


def test_builds_command_from_interpreter_and_arguments(monkeypatch):
    monkeypatch.setattr("sys.argv", ["app.py", "--flag"])
    assert_that(
        Reload()._command(),
        contains_string("app.py"),
        "Reload must restart the same script",
    )
