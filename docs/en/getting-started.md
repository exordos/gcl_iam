# Getting started

This guide protects a RESTAlchemy API with a remote IAM service and a
project-scoped controller.

## 1. Create the IAM driver

```python
from gcl_iam import drivers

iam_driver = drivers.HttpDriver(
    iam_endpoint="https://iam.example.com/v1/iam/clients/my-service",
    audience="my-service",
    hs256_jwks_decryption_key="<load from secret storage>",
)
```

The endpoint is normalized with a trailing slash. The driver obtains keys from
`actions/jwks`, caches the selected algorithm for five minutes by default, and
calls `actions/introspect` for every authenticated request. The token's `aud`
claim must equal `audience`.

## 2. Attach middleware

```python
from gcl_iam import middlewares as iam_middlewares
from restalchemy.api import middlewares

application = middlewares.attach_middlewares(
    application,
    [
        middlewares.configure_middleware(
            iam_middlewares.GenesisCoreAuthMiddleware,
            iam_engine_driver=iam_driver,
            skip_auth_endpoints=[
                iam_middlewares.EndpointComparator(r"/health", methods=["GET"]),
            ],
        ),
        iam_middlewares.ErrorsHandlerMiddleware,
    ],
)
```

`EndpointComparator` uses a regular-expression full match. Escape or anchor
patterns as needed and list every allowed HTTP method explicitly.

Do not run IAM-aware controllers on a skipped endpoint: skipping authentication
also means no IAM session is stored in the request context.

## 3. Protect a controller

```python
from gcl_iam.api import controllers as iam_controllers
from restalchemy.api import resources


class DocumentsController(iam_controllers.PolicyBasedController):
    __policy_service_name__ = "documents"
    __policy_name__ = "document"

    __resource__ = resources.ResourceByRAModel(
        model_class=Document,
        convert_underscore=False,
    )
```

CRUD methods require these permissions:

| Operation | Required rule |
| --- | --- |
| Create | `documents.document.create` |
| Get or filter | `documents.document.read` |
| Update | `documents.document.update` |
| Delete | `documents.document.delete` |

If introspection contains a `project_id`, the controller injects it into create
and query arguments and rejects a different project. An unscoped identity with
the required permission can operate across projects.

## 4. Send a request

```http
GET /v1/documents/ HTTP/1.1
Host: api.example.com
Authorization: Bearer <JWT>
```

The middleware performs the following steps:

1. Decode the unverified token only to discover its audience.
2. Ask the driver for an HS256 or RS256 verifier.
3. Verify the signature and expiration.
4. Introspect the verified token.
5. Build an `IamEngine` and store it in the request context.
6. Let the controller enforce `documents.document.read` and project scope.

Without an `Authorization` header, the middleware creates an anonymous context
with no permissions. Public endpoints should either be explicitly skipped or
handled by code that intentionally supports the anonymous identity.

## 5. Read identity data

```python
from restalchemy.common import contexts

iam = contexts.get_context().iam_context
user = iam.get_introspection_info().user_info

print(user.uuid)
print(user.email)
print(iam.get_introspection_info().project_id)
```

See [authentication and request context](concepts/authentication-and-context.md)
for the complete lifecycle and [authorization](concepts/authorization.md) for
controller selection.
