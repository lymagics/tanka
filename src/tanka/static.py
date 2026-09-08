import pathlib
from abc import ABC, abstractmethod

from tanka.abort import Abort
from tanka.body import Body, File
from tanka.endpoint import Endpoint
from tanka.request import Request
from tanka.response import Reply, Response


class Files(ABC):
    @abstractmethod
    def file(self, path: str) -> Body:
        pass


class Directory(Files):
    def __init__(self, root: str):
        self.root = root

    def file(self, path: str) -> Body:
        base = pathlib.Path(self.root).resolve()
        found = (base / path.lstrip("/")).resolve()
        if found.is_dir():
            found = found / "index.html"
        if not found.is_relative_to(base) or not found.is_file():
            raise Exception(f"File '{path}' is absent in '{self.root}'")
        return File(str(found))


class Static(Endpoint):
    def __init__(self, files: Files):
        self.files = files

    async def response(self, request: Request) -> Reply:
        try:
            body = self.files.file(str(request.target().path()))
        except Exception as error:
            raise Abort(404, str(error)) from error
        return Response(200, body)
