from abc import ABC, abstractmethod

from tanka.request import Request
from tanka.response import Reply


class Endpoint(ABC):
    @abstractmethod
    async def response(self, request: Request) -> Reply:
        pass
