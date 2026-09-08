from http import HTTPStatus

from plum import dispatch


class Status:
    def __init__(self, code: int):
        self.value = code

    def code(self) -> int:
        supported = {
            400, 401, 403, 404, 405, 406, 408, 409, 410, 411, 412, 413,
            414, 415, 416, 417, 418, 421, 422, 423, 424, 428, 429, 431,
            451, 500, 501, 502, 503, 504, 505,
        }  # fmt: skip
        if self.value not in supported:
            raise Exception(f"Status code {self.value} is not supported")
        return self.value

    def phrase(self) -> str:
        return HTTPStatus(self.code()).phrase


class Abort(Exception):
    @dispatch
    def __init__(self, code: int):
        self.__init__(code, Status(code).phrase())

    @dispatch
    def __init__(self, code: int, message: str):
        super().__init__(message)
        self.code = code

    def status(self) -> int:
        return Status(self.code).code()
