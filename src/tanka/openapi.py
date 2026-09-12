from functools import lru_cache
from urllib.parse import parse_qsl

import yaml
from openapi_core import OpenAPI
from openapi_core.datatypes import RequestParameters
from openapi_core.exceptions import OpenAPIError
from openapi_core.templating.paths.exceptions import PathError
from openapi_core.validation.request.exceptions import (
    SecurityValidationError,
)
from plum import dispatch
from werkzeug.datastructures import Headers as WerkzeugHeaders
from werkzeug.datastructures import ImmutableMultiDict

from tanka.abort import Abort
from tanka.body import Html, Json, Raw
from tanka.endpoint import Endpoint
from tanka.request import Request
from tanka.response import Reply, Response


class Document:
    def __init__(self, path: str):
        self.path = path

    def content(self) -> dict:
        try:
            with open(self.path, encoding="utf-8") as handle:
                return yaml.safe_load(handle)
        except OSError as error:
            raise Exception(
                f"Can't read OpenAPI specification '{self.path}'"
            ) from error


class CoreRequest:
    @dispatch
    def __init__(self, request: Request, data: bytes):
        self.__init__(
            request,
            data,
            RequestParameters(
                query=ImmutableMultiDict(
                    parse_qsl(str(request.target().query()))
                ),
                header=WerkzeugHeaders(list(request.headers())),
                cookie=ImmutableMultiDict(list(request.cookies())),
            ),
        )

    @dispatch
    def __init__(
        self,
        request: Request,
        data: bytes,
        parameters: RequestParameters,
    ):
        self.request = request
        self.data = data
        self.inputs = parameters

    @property
    def host_url(self) -> str:
        return "http://" + "".join(
            self.request.headers().values("host")[:1] or ["localhost"]
        )

    @property
    def path(self) -> str:
        return str(self.request.target().path())

    @property
    def method(self) -> str:
        return self.request.method().names()[0].lower()

    @property
    def parameters(self) -> RequestParameters:
        return self.inputs

    @property
    def content_type(self) -> str:
        return "".join(
            self.request.headers().values("content-type")[:1]
        ).lower()

    @property
    def body(self) -> bytes:
        return self.data


class CoreResponse:
    def __init__(self, reply: Reply, data: bytes):
        self.reply = reply
        self.data = data

    @property
    def status_code(self) -> int:
        return self.reply.status()

    @property
    def content_type(self) -> str:
        return "".join(
            [
                *self.reply.headers().values("content-type"),
                *self.reply.body().headers().values("content-type"),
            ][:1]
        ).lower()

    @property
    def headers(self) -> WerkzeugHeaders:
        return WerkzeugHeaders(
            [*self.reply.body().headers(), *self.reply.headers()]
        )


class OpenApi(Endpoint):
    @dispatch
    def __init__(self, path: str, origin: Endpoint):
        self.__init__(Document(path).content(), origin)

    @dispatch
    def __init__(self, document: dict, origin: Endpoint):
        self.document = document
        self.origin = origin

    async def response(self, request: Request) -> Reply:
        path = str(request.target().path())
        if path == "/openapi.json":
            result = Response(200, Json(self.document))
        elif path == "/docs":
            result = Response(200, Html(self._docs()))
        else:
            result = await self._validated(request)
        return result

    async def _validated(self, request: Request) -> Reply:
        data = await request.body().bytes()
        buffered = Request(
            request.method(),
            request.target(),
            request.headers(),
            Raw(
                data,
                "".join(
                    request.headers().values("content-type")[:1]
                    or ["application/octet-stream"]
                ),
            ),
            request.identity(),
        )
        core = self._core()
        described = self._checked(core, CoreRequest(buffered, data))
        reply = await self.origin.response(buffered)
        if described:
            reply = await self._verified(
                core,
                CoreRequest(buffered, data),
                reply,
            )
        return reply

    @lru_cache  # noqa: B019
    def _core(self) -> OpenAPI:
        return OpenAPI.from_dict({**self.document, "servers": [{"url": "/"}]})

    def _checked(self, core: OpenAPI, request: CoreRequest) -> bool:
        described = True
        try:
            core.validate_request(request)
        except PathError:
            described = False
        except SecurityValidationError as error:
            raise Abort(
                401,
                f"Request does not match the OpenAPI specification: {error}",
            ) from error
        except OpenAPIError as error:
            raise Abort(
                400,
                f"Request does not match the OpenAPI specification: {error}",
            ) from error
        return described

    async def _verified(
        self,
        core: OpenAPI,
        request: CoreRequest,
        reply: Reply,
    ) -> Reply:
        data = b"".join([chunk async for chunk in reply.body().chunks()])
        try:
            core.validate_response(request, CoreResponse(reply, data))
        except OpenAPIError as error:
            raise Abort(
                500,
                f"Response does not match the OpenAPI specification: {error}",
            ) from error
        return Response(
            reply.status(),
            reply.headers(),
            Raw(data, CoreResponse(reply, data).content_type),
        )

    def _docs(self) -> str:
        return (
            "<!doctype html><html><head><meta charset='utf-8'>"
            "<title>API documentation</title>"
            "<script src='https://unpkg.com/@stoplight/elements/"
            "web-components.min.js'></script>"
            "<link rel='stylesheet' href='https://unpkg.com/@stoplight/"
            "elements/styles.min.css'></head><body>"
            "<elements-api apiDescriptionUrl='openapi.json' "
            "router='hash' layout='sidebar' "
            "tryItCredentialsPolicy='same-origin'></elements-api>"
            "</body></html>"
        )
