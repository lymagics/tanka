from collections.abc import Iterator

from plum import dispatch


class Headers:
    @dispatch
    def __init__(self):
        self.__init__(())

    @dispatch
    def __init__(self, pairs: dict):
        self.__init__(tuple(pairs.items()))

    @dispatch
    def __init__(self, pairs: list):
        self.__init__(tuple(pairs))

    @dispatch
    def __init__(self, pairs: tuple):
        self.pairs = pairs

    def header(self, name: str) -> str:
        values = self.values(name)
        if not values:
            raise Exception(f"Header '{name}' is absent")
        return values[0]

    def values(self, name: str) -> list[str]:
        return [
            value
            for label, value in self.pairs
            if label.lower() == name.lower()
        ]

    def __iter__(self) -> Iterator[tuple[str, str]]:
        return iter(self.pairs)
