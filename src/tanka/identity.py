from abc import ABC, abstractmethod


class Identity(ABC):
    @abstractmethod
    def id(self) -> str:
        pass

    @abstractmethod
    def roles(self) -> list[str]:
        pass


class Principal(Identity):
    def __init__(self, id: str, *roles: str):
        self.label = id
        self.grants = roles

    def id(self) -> str:
        return self.label

    def roles(self) -> list[str]:
        return list(self.grants)


class Anonymous(Identity):
    def id(self) -> str:
        raise Exception("Request is not authenticated, identity is unknown")

    def roles(self) -> list[str]:
        return []
