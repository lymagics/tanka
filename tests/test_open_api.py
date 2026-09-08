import asyncio
import json
import pathlib
import shutil

from hamcrest import (
    assert_that,
    calling,
    contains_string,
    equal_to,
    has_entry,
    has_properties,
    raises,
)

from fakes import Echo, Fixed
from tanka.abort import Abort
from tanka.body import Body, Empty, Json, Text
from tanka.endpoint import Endpoint
from tanka.headers import Headers
from tanka.method import Get, Post
from tanka.openapi import OpenApi
from tanka.request import Request
from tanka.response import Reply, Response


def specification(title: str) -> dict:
    return {
        "openapi": "3.0.3",
        "info": {"title": title, "version": "1.0.0"},
        "paths": {
            "/users": {
                "post": {
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["name"],
                                    "properties": {"name": {"type": "string"}},
                                }
                            }
                        },
                    },
                    "responses": {
                        "201": {
                            "description": "Created",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "required": ["id"],
                                        "properties": {
                                            "id": {"type": "integer"}
                                        },
                                    }
                                }
                            },
                        }
                    },
                }
            }
        },
    }


def templated(title: str) -> dict:
    return {
        "openapi": "3.0.3",
        "info": {"title": title, "version": "1.0.0"},
        "paths": {
            "/items/{id}": {
                "parameters": [
                    {
                        "name": "id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                    }
                ],
                "get": {"responses": {"200": {"description": "OK"}}},
            }
        },
    }


def secured(title: str) -> dict:
    return {
        "openapi": "3.0.3",
        "info": {"title": title, "version": "1.0.0"},
        "components": {
            "securitySchemes": {
                "bearer": {"type": "http", "scheme": "bearer"},
            }
        },
        "paths": {
            "/vault": {
                "get": {
                    "security": [{"bearer": []}],
                    "responses": {"200": {"description": "OK"}},
                }
            }
        },
    }


class Created(Endpoint):
    async def response(self, request: Request) -> Reply:
        return Response(
            201, Json({"id": 1, "echo": await request.body().text()})
        )


def posted(payload: str) -> Request:
    return Request(
        Post(),
        "/users",
        Headers({"content-type": "application/json"}),
        Text(payload),
    )


def scratch(name: str) -> pathlib.Path:
    folder = pathlib.Path(__file__).parent.parent / "tmp" / name
    shutil.rmtree(folder, ignore_errors=True)
    folder.mkdir(parents=True)
    return folder


async def test_serves_specification_as_json():
    assert_that(
        json.loads(
            await Body.Smart(
                (
                    await OpenApi(
                        specification("Spec Title"), Echo()
                    ).response(
                        Request(Get(), "/openapi.json", Headers(), Empty())
                    )
                ).body()
            ).text()
        ),
        has_entry("info", has_entry("title", "Spec Title")),
        "OpenApi must serve the specification at /openapi.json",
    )


async def test_serves_documentation_page():
    assert_that(
        await Body.Smart(
            (
                await OpenApi(specification("Docs"), Echo()).response(
                    Request(Get(), "/docs", Headers(), Empty())
                )
            ).body()
        ).text(),
        contains_string("<elements-api"),
        "OpenApi must serve a Stoplight Elements page at /docs",
    )


async def test_lets_documentation_keep_cookies():
    assert_that(
        await Body.Smart(
            (
                await OpenApi(specification("Cookies"), Echo()).response(
                    Request(Get(), "/docs", Headers(), Empty())
                )
            ).body()
        ).text(),
        contains_string("tryItCredentialsPolicy='same-origin'"),
        "OpenApi must let the Try It panel store and send cookies",
    )


def test_rejects_request_violating_schema():
    assert_that(
        calling(asyncio.run).with_args(
            OpenApi(specification("Strict"), Echo()).response(
                posted('{"name": 42}')
            )
        ),
        raises(Abort, "Request does not match"),
        "OpenApi must abort with 400 on an invalid request body",
    )


async def test_passes_valid_request_to_endpoint():
    assert_that(
        (
            await OpenApi(
                specification("Valid"), Fixed(Response(201, Json({"id": 7})))
            ).response(posted('{"name": "Ann"}'))
        ).status(),
        equal_to(201),
        "OpenApi must delegate a valid request",
    )


async def test_keeps_body_readable_for_endpoint():
    assert_that(
        json.loads(
            await Body.Smart(
                (
                    await OpenApi(
                        specification("Buffered"), Created()
                    ).response(posted('{"name": "Bob"}'))
                ).body()
            ).text()
        ),
        has_entry("echo", '{"name": "Bob"}'),
        "OpenApi must hand the endpoint a body that is still readable",
    )


def test_rejects_response_violating_schema():
    assert_that(
        calling(asyncio.run).with_args(
            OpenApi(
                specification("Checked"),
                Fixed(Response(201, Json({"id": "not-an-integer"}))),
            ).response(posted('{"name": "Cid"}'))
        ),
        raises(Abort, "Response does not match"),
        "OpenApi must abort with 500 on an invalid response",
    )


async def test_skips_validation_for_undescribed_path():
    assert_that(
        (
            await OpenApi(specification("Loose"), Echo()).response(
                Request(Get(), "/health", Headers(), Empty())
            )
        ).status(),
        equal_to(200),
        "OpenApi must pass through paths absent from the specification",
    )


def test_answers_unauthorized_without_required_security():
    assert_that(
        calling(asyncio.run).with_args(
            OpenApi(secured("Locked"), Echo()).response(
                Request(Get(), "/vault", Headers(), Empty())
            )
        ),
        raises(Abort, "Security", matching=has_properties(code=401)),
        "OpenApi must abort with 401 when a security requirement is unmet",
    )


async def test_reads_path_parameter_from_matched_template():
    assert_that(
        (
            await OpenApi(templated("Templated"), Echo()).response(
                Request(Get(), "/items/abc-123", Headers(), Empty())
            )
        ).status(),
        equal_to(200),
        "OpenApi must keep the path parameters it matched for validation",
    )


async def test_loads_specification_from_file():
    folder = scratch("openapi-file")
    (folder / "spec.json").write_text(json.dumps(specification("From File")))
    assert_that(
        json.loads(
            await Body.Smart(
                (
                    await OpenApi(str(folder / "spec.json"), Echo()).response(
                        Request(Get(), "/openapi.json", Headers(), Empty())
                    )
                ).body()
            ).text()
        ),
        has_entry("info", has_entry("title", "From File")),
        "OpenApi must load the specification from a file path",
    )
