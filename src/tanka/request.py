from plum import dispatch

from tanka.body import Body
from tanka.cookies import Cookies
from tanka.headers import Headers
from tanka.identity import Anonymous, Identity
from tanka.method import Method
from tanka.target import Target


class Request:
    @dispatch
    def __init__(
        self,
        method: Method,
        target: str,
        headers: Headers,
        body: Body,
    ):
        self.__init__(method, Target(target), headers, body, Anonymous())

    @dispatch
    def __init__(
        self,
        method: Method,
        target: Target,
        headers: Headers,
        body: Body,
    ):
        self.__init__(method, target, headers, body, Anonymous())

    @dispatch
    def __init__(
        self,
        method: Method,
        target: str,
        headers: Headers,
        body: Body,
        identity: Identity,
    ):
        self.__init__(method, Target(target), headers, body, identity)

    @dispatch
    def __init__(
        self,
        method: Method,
        target: Target,
        headers: Headers,
        body: Body,
        identity: Identity,
    ):
        self.verb = method
        self.uri = target
        self.fields = headers
        self.payload = body
        self.owner = identity

    def method(self) -> Method:
        return self.verb

    def target(self) -> Target:
        return self.uri

    def headers(self) -> Headers:
        return self.fields

    def body(self) -> Body.Smart:
        return Body.Smart(self.payload)

    def cookies(self) -> Cookies:
        return Cookies("; ".join(self.fields.values("cookie")))

    def identity(self) -> Identity:
        return self.owner
