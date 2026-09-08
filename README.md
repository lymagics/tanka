# Tanka

<p align="center">
  <i>
    Objects form a tree<br>
    Each small part has its own place<br>
    Nothing owns the whole<br>
    Mount and catch and route and wrap<br>
    The composition is all
  </i>
</p>

[![EO principles respected here](https://www.elegantobjects.org/badge.svg)](https://www.elegantobjects.org)

**True Object-Oriented Python Web Framework.**

Designed for humans by human.

- Elegant
- Fully object oriented
- Embraces declarative style
- Extremely maintainable

A Tanka application is a single tree of objects. There are no decorators on
functions, no global registries, no configuration files. You declare what your
application *is* by composing objects, and the framework runs that
declaration.

```python
import asyncio

from tanka import Endpoint, Get, Html, Response, Route, Routes, Tanka, Uvicorn


class Index(Endpoint):
    async def response(self, request):
        return Response(Html("<h1>Hello, world</h1>"))


asyncio.run(
    Tanka(
        Routes(
            Route(Get(), "/", Index()),
        ),
    ).run(Uvicorn("127.0.0.1", 8080)),
)
```

---

## Table of Contents

1. [Installation](#1-installation)
2. [Core Concepts](#2-core-concepts)
3. [Application](#3-application)
4. [Servers](#4-servers)
5. [Endpoint](#5-endpoint)
6. [Routing](#6-routing)
7. [Request](#7-request)
8. [Response](#8-response)
9. [Bodies](#9-bodies)
10. [Static Files](#10-static-files)
11. [Cookies](#11-cookies)
12. [Flash Messages](#12-flash-messages)
13. [Authentication and Authorization](#13-authentication-and-authorization)
14. [Error Handling](#14-error-handling)
15. [CORS](#15-cors)
16. [OpenAPI](#16-openapi)
17. [Logging](#17-logging)
18. [Testing Your Application](#18-testing-your-application)
19. [How It All Fits Together](#19-how-it-all-fits-together)
20. [Development](#20-development)

---

## 1. Installation

With uv:

```shell
uv add tanka
```

With pip:

```shell
pip install tanka
```

Optional extras add integrations, for example `uv add "tanka[uvicorn]"` or
`pip install "tanka[uvicorn]"`:

| Extra                | Adds                                           |
| -------------------- | ---------------------------------------------- |
| `tanka[uvicorn]`     | `Uvicorn` server                               |
| `tanka[hypercorn]`   | `Hypercorn` server                             |
| `tanka[reload]`      | `Reload()` hot reload through `watchfiles`     |
| `tanka[openapi]`     | `OpenApi` validation through `openapi-core`    |
| `tanka[all]`         | Everything above                               |

---

## 2. Core Concepts

| Concept    | What it is                                              | Examples                                                   |
| ---------- | ------------------------------------------------------- | ---------------------------------------------------------- |
| Tanka      | The complete runnable application                       | `Tanka(Routes(...))`                                       |
| Server     | Something that serves the application                   | `Uvicorn(...)`, `Hypercorn(...)`                           |
| Endpoint   | Anything that turns a `Request` into a `Reply`          | `Index()`, `Routes(...)`, `Authenticated(...)`, `Cors(...)` |
| Route      | Binds an HTTP method and a path pattern to an endpoint  | `Route(Get(), "/users/{id}", UserPage(...))`                |
| Request    | The incoming HTTP message                               | `request.target().path()`, `await request.body().json()`   |
| Reply      | The outgoing HTTP message interface                     | `Response(...)`, `Redirect(...)`, `WithCookie(...)`        |
| Body       | The payload of a message                                | `Html(...)`, `Json(...)`, `File(...)`, `Stream(...)`       |
| Middleware | An endpoint that wraps another endpoint                 | `Authenticated(...)`, `Catch(...)`, `OpenApi(...)`         |
| Identity   | Who is making the request                               | `Principal("42", "admin")`, `Anonymous()`                  |
| Abort      | The one exception that ends a request with a status     | `raise Abort(404, "User not found")`                       |

Every building block is small and immutable. Behaviour is added by wrapping
one object into another, never by modifying an existing one.

---

## 3. Application

`Tanka` wraps a single endpoint. Usually that endpoint is a `Routes`
collection, possibly wrapped in middleware.

```python
from tanka import Delete, Get, Post, Route, Routes, Tanka

app = Tanka(
    Routes(
        Route(Get(), "/", IndexPage(...)),
        Route(Get(), "/users", UsersPage(...)),
        Route(Post(), "/users", CreateUser(...)),
        Route(Delete(), "/users/{id}", DeleteUser(...)),
    ),
)
```

### Running with a built-in server

```python
await app.run(Uvicorn("127.0.0.1", 8080))
```

With no argument, `run()` starts Uvicorn on `127.0.0.1:8000`.

### Running as ASGI

`asgi()` exposes a standard ASGI callable, so any ASGI server can host it.

```python
# myapp.py
asgi = app.asgi()
```

```shell
uvicorn myapp:asgi
```

---

## 4. Servers

`Server` is an interface with two implementations.

```python
from tanka import Hypercorn, Reload, Uvicorn

Uvicorn("127.0.0.1", 8080)
Hypercorn("0.0.0.0", 8443)
Uvicorn("127.0.0.1", 8080, Reload())
```

`Reload()` watches the current directory and restarts the process when a
file changes. Run the script directly for it to work:

```shell
python myapp.py
```

---

## 5. Endpoint

`Endpoint` is the one interface every request handler implements. It has a
single method, `response`, which receives a `Request` and returns a `Reply`.

```python
from tanka import Endpoint, Json, Reply, Request, Response


class UserPage(Endpoint):
    def __init__(self, db):
        self.db = db

    async def response(self, request: Request) -> Reply:
        user = await PgUsers(self.db).user(
            request.target().path().parameter("id")
        )
        return Response(Json({"id": user.id(), "name": user.name()}))
```

Pages, API handlers, static file servers, middleware, CORS, error catching
and OpenAPI validation are all endpoints. Because they share one interface,
any of them can wrap any other.

---

## 6. Routing

### Route

A `Route` maps an HTTP method and a path to an endpoint.

```python
Route(Get(), "/", IndexPage())
Route(Post(), "/users", CreateUser(...))
```

Available methods: `Get`, `Post`, `Put`, `Patch`, `Delete`, `Head`,
`Options`, and `Verb("PURGE")` for anything else.

### Several methods on one route

```python
Route(Methods(Get(), Head()), "/users", UsersPage(...))
```

### Path parameters

Paths declare parameters with curly braces. Parsing is delegated to the
[parse](https://github.com/r1chardj0n3s/parse) library, so its type
suffixes work too.

```python
Route(Get(), "/users/{id}", UserPage(...))
Route(Get(), "/posts/{year:d}/{slug}", PostPage(...))
```

```python
request.target().path().parameter("id")    # "42"
request.target().path().parameter("year")  # 2024
```

### Mount

`Mount` attaches an endpoint under a path prefix. The prefix is stripped
before the inner endpoint sees the request. This is how versioned or grouped
APIs are built.

```python
Routes(
    Mount(
        "/v1",
        Routes(
            Route(Get(), "/users", UsersV1(...)),
            Route(Post(), "/users", CreateUserV1(...)),
        ),
    ),
    Mount(
        "/v2",
        Routes(
            Route(Get(), "/users", UsersV2(...)),
        ),
    ),
)
```

Routes are tried in order. The first one that matches wins. A request that
matches nothing ends with `404`.

---

## 7. Request

A `Request` is the incoming HTTP message.

```python
request.method().names()                    # ["GET"]
request.target().path()                     # Path, str() gives "/users"
request.target().path().parameter("id")     # path parameter
request.target().query().parameter("page")  # first value, fails if absent
request.target().query().values("tag")      # all values, maybe empty
request.headers().header("accept")          # first value, fails if absent
request.headers().values("accept")          # all values, maybe empty
request.cookies().cookie("session")         # cookie value, fails if absent
request.identity()                          # see Authentication
```

The body is decoded on demand.

```python
raw = await request.body().bytes()
text = await request.body().text()
data = await request.body().json()
```

You can build a `Request` yourself, for example in tests.

```python
from tanka import Empty, Get, Headers, Request, Text

Request(Get(), "/users?page=2", Headers({"accept": "text/html"}), Empty())
Request(Post(), "/users", Headers(), Text('{"name": "Ann"}'))
```

---

## 8. Response

`Reply` is the interface of an outgoing message: a status, headers and a
body. `Response` is the plain implementation.

```python
Response(Html("<h1>Hello</h1>"))                       # status 200
Response(201, Json({"id": 7}))
Response(200, Headers({"cache-control": "no-store"}), Text("fresh"))
```

### Redirect

```python
Redirect("/login")          # 302
Redirect("/users", 303)
```

### Adding headers

Replies are wrapped, never modified.

```python
WithHeaders(
    Response(Json(items)),
    Headers({"x-total-count": str(len(items))}),
)
```

Cookies and flash messages are added the same way, see below.

---

## 9. Bodies

| Body                       | Purpose                                      |
| -------------------------- | -------------------------------------------- |
| `Html("<p>hi</p>")`        | HTML document                                |
| `Json({"ok": True})`       | JSON payload                                 |
| `Text("plain")`            | Plain text                                   |
| `Empty()`                  | No body, for `204` and redirects             |
| `Raw(b"...", "image/png")` | Bytes with an explicit content type          |
| `File("./report.pdf")`     | A single file, content type guessed          |
| `Stream(chunks, "text/csv")` | Chunks from any async iterable             |

Streaming a large export without buffering it:

```python
class Export(Endpoint):
    async def response(self, request):
        return Response(Stream(self.rows(), "text/csv"))

    async def rows(self):
        yield b"id,name\n"
        async for user in PgUsers(self.db).users():
            yield f"{user.id()},{user.name()}\n".encode()
```

Every body contributes its own headers, such as `content-type` and
`content-length`. Headers given to `Response` take precedence.

---

## 10. Static Files

`Static` serves files from a `Files` source. `Directory` is the source for a
local folder. Combine it with `Mount` so paths are relative to the folder.

```python
Routes(
    Mount("/static", Static(Directory("./public"))),
)
```

`GET /static/css/app.css` serves `./public/css/app.css`. A folder serves its
`index.html`. Paths that escape the root or point to nothing end with `404`.

Other sources are added by implementing `Files`, without touching `Static`.

```python
class S3Bucket(Files):
    def __init__(self, bucket: str):
        self.bucket = bucket

    def file(self, path: str) -> Body:
        ...
```

---

## 11. Cookies

### Reading

```python
session = request.cookies().cookie("session")
```

### Writing

Wrap the reply in `WithCookie`.

```python
WithCookie(
    Redirect("/"),
    Cookie(
        "session",
        token,
        HttpOnly(),
        Secure(),
        SameSite("Lax"),
        CookiePath("/"),
        Lifetime(3600),
        Domain("example.com"),
    ),
)
```

### Deleting

```python
WithCookie(Redirect("/login"), ForgetCookie("session", CookiePath("/")))
```

Several cookies are set by nesting `WithCookie`.

---

## 12. Flash Messages

A flash message travels to the next page through a cookie.

```python
WithFlash(
    Redirect("/users"),
    Flash("User created", Success()),
)
```

Kinds: `Success()`, `Failure()`, `Notice()`, `Alert()`.

The next page reads and clears it.

```python
class UsersPage(Endpoint):
    async def response(self, request):
        notes = [
            f"<p class='{flash.kind().name()}'>{flash.text()}</p>"
            for flash in Flashes(request.cookies())
        ]
        return WithCookie(
            Response(Html("".join(notes) + await self.table())),
            ForgetCookie("flash", CookiePath("/")),
        )
```

---

## 13. Authentication and Authorization

Both are middleware: endpoints that wrap another endpoint.

### Identity source

Tanka does not ship identity sources. Your application implements
`IdentitySource`: given a request, return an `Identity` or raise `Abort`.

```python
from tanka import Abort, Identity, IdentitySource, Principal


class SessionIdentity(IdentitySource):
    def __init__(self, db):
        self.db = db

    async def identity(self, request) -> Identity:
        try:
            token = request.cookies().cookie("session")
        except Exception as error:
            raise Abort(401, "Please log in") from error
        user = await PgSessions(self.db).user(token)
        return Principal(user.id(), *user.roles())
```

### Authenticated

`Authenticated` asks the source for an identity, attaches it to the request
and passes the request on.

```python
Route(
    Get(),
    "/profile",
    Authenticated(ProfilePage(...), SessionIdentity(...)),
)
```

Inside the endpoint:

```python
request.identity().id()      # "42"
request.identity().roles()   # ["admin", "editor"]
```

A request that did not pass through `Authenticated` carries `Anonymous()`:
`id()` fails fast and `roles()` is empty.

### Authorized

`Authorized` checks a requirement against the identity and ends with `403`
when it is not met. Place it inside `Authenticated`.

```python
Authenticated(
    Authorized(AdminPage(...), Role("admin")),
    SessionIdentity(...),
)
```

Requirements compose:

```python
Role("admin")                                # exactly this role
Roles("admin", "editor")                     # any of these roles
AnyOf(Role("owner"), Roles("admin", "root")) # any requirement
AllOf(Role("staff"), Role("verified"))       # every requirement
```

Custom rules implement `Requirement`:

```python
class Verified(Requirement):
    def matches(self, identity: Identity) -> bool:
        return "unverified" not in identity.roles()
```

---

## 14. Error Handling

### Abort

`Abort` is the single exception for ending a request with an HTTP error. It
is never caught inside endpoints; it propagates up to the application, which
turns it into a reply.

```python
class UserPage(Endpoint):
    async def response(self, request):
        try:
            user = await PgUsers(self.db).user(
                request.target().path().parameter("id")
            )
        except Exception as error:
            raise Abort(404, "User not found") from error
        return Response(Html(user.page()))
```

`Abort` accepts 4xx and 5xx codes from the standard table (`400`, `401`,
`403`, `404`, `405`, ..., `500`, `501`, `502`, `503`, `504`, `505`). Any
other code breaks the request and ends with `500`.

### Default behaviour

- Any exception that is not `Abort` ends with `500`.
- A request that matches no route ends with `404`.
- Without a custom page, the framework answers with a small HTML page
  naming the error: `Not Found`, `Internal Server Error`, and so on.

### Catch and On

`Catch` maps status codes to your own error endpoints.

```python
Tanka(
    Catch(
        Routes(
            Route(Get(), "/", IndexPage(...)),
        ),
        On(404, NotFoundPage()),
        On((401, 403), AccessDeniedPage()),
        On(Range(500, 599), ServerErrorPage()),
        On(..., AnyErrorPage()),
    ),
)
```

`On` accepts a single code, a tuple of codes, a `Range`, or `...` for
everything. The first matching `On` answers. Codes nothing matches fall
through to the default pages.

### Fallback

An error page that needs to know what went wrong implements `Fallback`
instead of `Endpoint`. Its `response` receives the request and an `Abort`
carrying the status and the message, which is how a JSON API turns every
failure into one error format. A plain exception arrives as `Abort(500,
message)`.

```python
from tanka import Abort, Catch, Fallback, Json, On, Response


class Enveloped(Fallback):
    async def response(self, request, error: Abort):
        return Response(error.status(), Json({"error": str(error)}))


Catch(routes, On(..., Enveloped()))
```

A plain `Endpoint` given to `On` is wrapped in `Indifferent`, which answers
the same way whatever the error was.

---

## 15. CORS

`Cors` wraps an endpoint with a set of policies. Preflight requests are
answered without reaching the wrapped endpoint.

```python
Tanka(
    Cors(
        Routes(
            Route(Get(), "/users", Users(...)),
            Route(Post(), "/users", CreateUser(...)),
        ),
        AllowOrigins("https://app.example.com"),
        AllowMethods(Get(), Post()),
        AllowHeaders("Content-Type", "Authorization"),
        AllowCredentials(),
        ExposeHeaders("X-Total-Count"),
        MaxAge(600),
    ),
)
```

`AllowOrigins("*")` allows every origin.

---

## 16. OpenAPI

`OpenApi` wraps an endpoint with an OpenAPI specification file (YAML or
JSON). It needs the `openapi` extra.

```python
from tanka import OpenApi

Tanka(
    OpenApi(
        "openapi.yaml",
        Routes(
            Route(Get(), "/users", Users(...)),
            Route(Post(), "/users", CreateUser(...)),
        ),
    ),
)
```

It provides three things:

- **Documentation** at `/docs`, rendered with
  [Stoplight Elements](https://stoplight.io/open-source/elements), and the
  specification itself at `/openapi.json`. Its "Try It" panel keeps and
  sends cookies for same-origin calls, so cookie-based flows work from the
  page.
- **Request validation**: a request that violates its operation schema ends
  with `400` before reaching the endpoint; one that misses a declared
  security requirement ends with `401`.
- **Response validation**: a reply that violates the schema ends with `500`.

Paths the specification does not describe pass through untouched. The
endpoint itself stays unaware of validation.

---

## 17. Logging

Unhandled exceptions are logged with their traceback before the `500` page
is sent. `Tanka` logs through the standard `logging` module under the
`tanka` logger by default. Pass a `Log` to change that.

```python
Tanka(routes, Logging("myapp.http"))   # a named stdlib logger
Tanka(routes, Silence())               # nothing, handy in tests
```

---

## 18. Testing Your Application

Endpoints are plain objects. Call them with a hand-made `Request`.

```python
async def test_greets_by_name():
    reply = await Route(Get(), "/hello/{name}", Greeting()).response(
        Request(Get(), "/hello/Ann", Headers(), Empty())
    )
    assert_that(await Body.Smart(reply.body()).text(), equal_to("Hi, Ann"))
```

For the whole tree, drive the ASGI application with `httpx`.

```python
async def test_serves_index():
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=Tanka(routes, Silence()).asgi()),
        base_url="http://test",
    ) as http:
        assert_that((await http.get("/")).status_code, equal_to(200))
```

Replace real dependencies with fake objects that implement the same
interfaces, such as a fake `IdentitySource` or a fake `Files`.

---

## 19. How It All Fits Together

Every piece of Tanka is an `Endpoint` or wraps one. An application is a tree
where each layer adds one concern and delegates the rest inward.

```
Tanka
└── Catch                    error pages
    └── Cors                 cross-origin policy
        └── OpenApi          documentation + validation
            └── Routes       dispatch by method + path
                ├── Route → Authenticated → Authorized → AdminPage
                ├── Mount("/static") → Static(Directory("./public"))
                └── Mount("/v1") → Routes → ...
```

Replies follow the same idea. A plain `Response` is wrapped to add cookies,
headers or flash messages.

```
WithFlash
└── WithCookie
    └── Redirect("/users")
```

The result is an application you can read top-down as a single expression,
and change by swapping or wrapping one object at a time.

---

## 20. Development

```shell
uv sync
make help
```

| Command       | Purpose                                     |
| ------------- | ------------------------------------------- |
| `make unit`   | Unit tests with coverage                    |
| `make deep`   | Integration tests against live servers      |
| `make lint`   | black, flake8 and ruff                      |
