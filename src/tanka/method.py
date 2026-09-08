from abc import ABC, abstractmethod


class Method(ABC):
    @abstractmethod
    def names(self) -> list[str]:
        pass


class Get(Method):
    def names(self) -> list[str]:
        return ["GET"]


class Post(Method):
    def names(self) -> list[str]:
        return ["POST"]


class Put(Method):
    def names(self) -> list[str]:
        return ["PUT"]


class Patch(Method):
    def names(self) -> list[str]:
        return ["PATCH"]


class Delete(Method):
    def names(self) -> list[str]:
        return ["DELETE"]


class Head(Method):
    def names(self) -> list[str]:
        return ["HEAD"]


class Options(Method):
    def names(self) -> list[str]:
        return ["OPTIONS"]


class Verb(Method):
    def __init__(self, name: str):
        self.name = name

    def names(self) -> list[str]:
        return [self.name.upper()]


class Methods(Method):
    def __init__(self, *methods: Method):
        self.methods = methods

    def names(self) -> list[str]:
        return [name for method in self.methods for name in method.names()]
