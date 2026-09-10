from jinja2 import (
    Environment,
    FileSystemLoader,
    TemplateError,
    select_autoescape,
)
from plum import dispatch

from tanka.templates import Templates


class Jinja(Templates):
    @dispatch
    def __init__(self, directory: str):
        self.__init__(
            Environment(
                loader=FileSystemLoader(directory),
                autoescape=select_autoescape(),
            )
        )

    @dispatch
    def __init__(self, environment: Environment):
        self.environment = environment

    async def markup(self, name: str, values: dict) -> str:
        try:
            return self.environment.get_template(name).render(**values)
        except TemplateError as error:
            raise Exception(f"Can't render template '{name}'") from error
