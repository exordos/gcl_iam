# Implement a custom driver

Use a custom driver when keys or introspection data are available in-process,
through a non-HTTP protocol, or from a different IAM API.

## Implement the interface

```python
from gcl_iam import algorithms
from gcl_iam import drivers


class DatabaseDriver(drivers.AbstractAuthDriver):
    def get_algorithm(self, token_info):
        client = load_client_by_audience(token_info.audience_name)
        return algorithms.RS256VerifyOnly(
            public_key=client.public_key,
            previous_public_key=client.previous_public_key,
        )

    def get_introspection_info(self, token_info, otp_code=None):
        session = load_active_session(token_info.uuid)
        return {
            "user_info": {
                "uuid": str(session.user.uuid),
                "name": session.user.name,
                "first_name": session.user.first_name,
                "last_name": session.user.last_name,
                "email": session.user.email,
                "type": session.user.type,
            },
            "project_id": (
                str(session.project_id) if session.project_id else None
            ),
            "otp_verified": verify_otp(session.user, otp_code),
            "permissions": list(session.permissions),
        }
```

The example helper functions belong to the application; they are not provided
by `gcl_iam`.

## Security requirements

- Select keys from the unverified audience, but treat no other unverified claim
  as trusted.
- Reject unknown audiences before expensive or external work.
- Return verification-only `RS256VerifyOnly` in services that never issue
  tokens.
- Validate that the session/token is active during introspection.
- Return current permissions and project scope rather than stale embedded
  authorization data.
- Fail closed: missing users, keys or permissions must not create an
  administrator identity.
- Never log tokens, private keys, symmetric secrets or OTP values.

## Key rotation

Pass both the current and immediately previous verification key:

```python
algorithm = algorithms.HS256(
    key=current_secret,
    previous_key=previous_secret,
)
```

or:

```python
algorithm = algorithms.RS256VerifyOnly(
    public_key=current_public_key,
    previous_public_key=previous_public_key,
)
```

Encoding always uses the current key. Decoding tries the current key first and
then the previous key. Remove the previous key after all tokens signed by it
have expired.

## Anonymous access

`GenesisCoreAuthMiddleware` uses its own `AnonDriver` when no bearer token is
present; the configured custom driver is not called. Anonymous introspection
has no permissions and no project. If the application needs richer anonymous
behavior, implement it explicitly at the route/controller layer or subclass the
middleware with a carefully reviewed trust model.
