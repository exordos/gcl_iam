# gcl_iam

`gcl_iam` is a Python library for adding JWT authentication and policy-based
authorization to RESTAlchemy services. It provides:

- HS256 and RS256 token verification, including previous-key fallback during
  key rotation;
- remote JWKS discovery and token introspection through an IAM service;
- request-scoped identity, project and permission data;
- wildcard permissions in the `service.resource.action` format;
- project-aware, nested, projectless and OTP-aware RESTAlchemy controllers;
- permission-driven field visibility; and
- OAuth-style HTTP error responses.

The library requires Python 3.10 or newer and is licensed under Apache 2.0.

## Documentation

The complete documentation is available in four languages. Every language has
the same files, section order and code examples:

- [English](docs/en/index.md)
- [Русский](docs/ru/index.md)
- [Deutsch](docs/de/index.md)
- [中文](docs/zh/index.md)

New users should start with [installation](docs/en/installation.md) and the
[getting-started guide](docs/en/getting-started.md).

## Quick example

```python
from gcl_iam import drivers
from gcl_iam import middlewares as iam_middlewares
from restalchemy.api import middlewares

iam_driver = drivers.HttpDriver(
    iam_endpoint="https://iam.example.com/v1/iam/clients/my-service",
    audience="my-service",
    hs256_jwks_decryption_key="<32-byte A256GCM key>",
)

application = middlewares.attach_middlewares(
    application,
    [
        middlewares.configure_middleware(
            iam_middlewares.GenesisCoreAuthMiddleware,
            iam_engine_driver=iam_driver,
        ),
        iam_middlewares.ErrorsHandlerMiddleware,
    ],
)
```

Use real secret management for IAM credentials and encryption keys. Never put
them in source code.

## Development

Create the standard development environment and run the unit tests:

```bash
tox -e develop
tox -e py310
```

Additional checks are available as `tox -e ruff-check` and `tox -e mypy`.
