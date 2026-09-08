from abc import ABC, abstractmethod

from tanka.abort import Abort
from tanka.endpoint import Endpoint
from tanka.identity import Identity
from tanka.request import Request
from tanka.response import Reply


class IdentitySource(ABC):
    @abstractmethod
    async def identity(self, request: Request) -> Identity:
        pass


class Authenticated(Endpoint):
    def __init__(self, origin: Endpoint, source: IdentitySource):
        self.origin = origin
        self.source = source

    async def response(self, request: Request) -> Reply:
        return await self.origin.response(
            Request(
                request.method(),
                request.target(),
                request.headers(),
                request.body(),
                await self.source.identity(request),
            )
        )


class Requirement(ABC):
    @abstractmethod
    def matches(self, identity: Identity) -> bool:
        pass


class Role(Requirement):
    def __init__(self, name: str):
        self.name = name

    def matches(self, identity: Identity) -> bool:
        return self.name in identity.roles()


class Roles(Requirement):
    def __init__(self, *names: str):
        self.names = names

    def matches(self, identity: Identity) -> bool:
        return AnyOf(*[Role(name) for name in self.names]).matches(identity)


class AnyOf(Requirement):
    def __init__(self, *requirements: Requirement):
        self.requirements = requirements

    def matches(self, identity: Identity) -> bool:
        return any(
            requirement.matches(identity) for requirement in self.requirements
        )


class AllOf(Requirement):
    def __init__(self, *requirements: Requirement):
        self.requirements = requirements

    def matches(self, identity: Identity) -> bool:
        return all(
            requirement.matches(identity) for requirement in self.requirements
        )


class Authorized(Endpoint):
    def __init__(self, origin: Endpoint, requirement: Requirement):
        self.origin = origin
        self.requirement = requirement

    async def response(self, request: Request) -> Reply:
        if not self.requirement.matches(request.identity()):
            raise Abort(403, "Identity does not meet the requirement")
        return await self.origin.response(request)
