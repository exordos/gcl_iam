# gcl_iam

`gcl_iam` adds authentication and authorization to Python RESTAlchemy
services. It validates JWTs, obtains identity and permission data from an IAM
driver, stores that data in the request context, and enforces it in controllers
and field serializers.

## Capabilities

- Verify HS256 and RS256 JWTs.
- Accept a previous signing or verification key during key rotation.
- Fetch JWKS and introspection data from a remote IAM endpoint.
- Support custom in-process IAM drivers.
- Match permissions in `service.resource.action` form, with `*` at any level.
- Restrict project-scoped resources to the token's `project_id`.
- Protect projectless and nested resources.
- Require a verified OTP for selected operations.
- Show or hide RESTAlchemy fields according to IAM rules.
- Expose token, user, project and permission data through the current context.
- Convert IAM exceptions into consistent HTTP error responses.

`gcl_iam` does not issue user credentials, define application roles, or provide
an IAM database. Those responsibilities belong to the IAM service or a custom
driver.

## Documentation map

1. [Installation](installation.md)
2. [Getting started](getting-started.md)
3. Concepts:
   - [Authentication and request context](concepts/authentication-and-context.md)
   - [Permissions, projects and OTP](concepts/authorization.md)
4. How-to guides:
   - [Integrate a RESTAlchemy service](how-to/restalchemy-service.md)
   - [Implement a custom driver](how-to/custom-driver.md)
5. [Public API reference](reference/api.md)

## Languages

This documentation has identical structure in:

- [English](../en/index.md)
- [Русский](../ru/index.md)
- [Deutsch](../de/index.md)
- [中文](../zh/index.md)

## Supported environment

- Python 3.10 or newer
- RESTAlchemy 15.x
- PyJWT 2.x
- HS256 or RS256 JWT signatures

The current dependency ranges are authoritative in `pyproject.toml`.
