# Authentication and request context

## Request lifecycle

`GenesisCoreAuthMiddleware` handles authentication before the RESTAlchemy
controller is called.

For a bearer token it:

1. reads `Authorization: Bearer ...`;
2. creates `UnverifiedToken` to obtain the `aud` claim without trusting it;
3. asks the configured driver for the matching verification algorithm;
4. creates `AuthToken`, verifying signature and expiration;
5. asks the driver for introspection data, forwarding `X-OTP` when present;
6. creates an `IamEngine` and `Enforcer`; and
7. stores the engine in `GenesisCoreAuthContext.iam_context` for the duration of
   the request.

An invalid bearer token becomes `InvalidAuthTokenError`. A missing bearer token
creates `AnonymousToken` through `AnonDriver`; it does not skip the middleware.

## Driver contract

Every driver implements two methods:

```python
class AbstractAuthDriver:
    def get_algorithm(self, token_info): ...
    def get_introspection_info(self, token_info, otp_code=None): ...
```

`get_algorithm` returns an object with `encode` and `decode`; service-side
drivers normally return `HS256` or `RS256VerifyOnly`. `get_introspection_info`
returns a mapping with at least:

```python
{
    "user_info": {
        "uuid": "...",
        "name": "...",
        "first_name": "...",
        "last_name": "...",
        "email": "...",
        "type": "...",
    },
    "project_id": "...",  # or None
    "otp_verified": True,
    "permissions": ["service.resource.action"],
}
```

`IamEngine` adds `otp_enabled` from the auth token.

## HttpDriver

`HttpDriver` is the standard remote implementation. It validates the audience
before making a request. It supports:

- HS256 JWKS entries with `kty="oct"`; secrets must be encrypted by
  `encrypt_hs256_jwks_secret` using A256GCM;
- RS256 JWKS entries with `kty="RSA"`, `n` and `e`;
- a second matching JWKS key as the previous key during rotation; and
- configurable HTTP timeout, cache size and cache TTL.

Only algorithm/JWKS resolution is cached. Introspection remains per request so
permission, project and OTP changes take effect immediately.

## Context data

Inside an authenticated request:

```python
from restalchemy.common import contexts

engine = contexts.get_context().iam_context
raw = engine.introspection_info()
typed = engine.get_introspection_info()
token = engine.token_info
enforcer = engine.enforcer
```

`typed.user_info` exposes `uuid`, `name`, `first_name`, `last_name`, `email` and
`type`. `typed.project_id` is converted to `uuid.UUID` when present.

The context is request-local. Accessing it outside an IAM session raises a
context exception. Nested IAM sessions are rejected to prevent accidental
identity replacement.

## Proxy information

`GenesisCoreAuthContext` also provides:

- `get_real_url_with_prefix()`, which considers `X-Forwarded-Proto`,
  `X-Forwarded-Host`, `X-Forwarded-Port` and `X-Forwarded-Prefix`; and
- `get_user_ip()`, which checks `X-Forwarded-For`, `X-Real-IP`, request address
  attributes and finally `REMOTE_ADDR`.

Accept forwarded headers only from trusted reverse proxies. The library does
not establish that trust boundary for the application.
