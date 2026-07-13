# Public API reference

This page lists the supported building blocks visible in the source tree. For
exact call signatures, consult the installed version because minor releases may
add optional parameters.

## `gcl_iam.algorithms`

- `HS256(key, previous_key=None)` — sign and verify HS256 JWTs.
- `RS256(private_key, public_key, previous_public_key=None)` — sign and verify
  RS256 JWTs.
- `RS256VerifyOnly(public_key, previous_public_key=None)` — verify RS256 JWTs;
  `encode` is unsupported.
- `generate_rsa_private_key_pem(bitness=2048, public_exponent=65537)` — generate
  an unencrypted PKCS#8 RSA private key. Supported sizes: 2048, 3072 and 4096.
- `generate_rsa_public_key_pem(private_key_pem)` — derive a PEM public key.
- `get_rsa_bitness_from_private_key_pem(private_key_pem)` — return key size.
- `public_pem_to_jwk(public_key_pem)` — convert an RSA public key to JWK fields.
- `encrypt_hs256_jwks_secret(secret, encryption_key)` and
  `decrypt_hs256_jwks_secret(secret, decryption_key)` — protect HS256 JWKS
  secrets with a 32-byte A256GCM key. The serialized form starts with `aesgcm:`.

`BaseJwtAlgorithm.decode` supports `audience`, `ignore_audience`,
`ignore_expiration` and `verify`. Disabling verification is useful only for
controlled diagnostics and must not authorize requests.

## `gcl_iam.tokens`

- `UnverifiedToken` — parses claims without verification; use only to select a
  driver/key.
- `VerifiedToken` — verified common claims and UTC timestamps.
- `AuthToken` — adds `token_type`, `otp_enabled` and authentication time.
- `IdToken` — adds user name and email.
- `RefreshToken` — verified refresh-token representation.
- `AnonymousToken` — fixed anonymous identity used for missing bearer tokens.

The historical public property name `autenticated_at` is intentionally spelled
as implemented; callers must use that spelling for compatibility.

## `gcl_iam.drivers`

- `AbstractAuthDriver` — custom driver contract.
- `HttpDriver` — remote JWKS and introspection implementation.
- `DummyDriver` — configurable test driver.
- `AnonDriver` — built-in anonymous introspection.
- `HS256AlgorithmKeys` and `RS256AlgorithmKeys` — immutable key containers used
  by `DummyDriver`.

`HttpDriver` constructor options after the three required values are
`default_timeout=5`, `cache_maxsize=100`, and `cache_ttl_seconds=300`.

## `gcl_iam.engines` and `gcl_iam.contexts`

- `IamEngine` — combines verified token, introspection and `Enforcer`.
- `IntrospectionInfo` and `UserInfo` — typed accessors over introspection data.
- `GenesisCoreAuthContext` — RESTAlchemy context with an IAM session, proxy URL
  reconstruction and client IP discovery.

## `gcl_iam.enforcers` and `gcl_iam.rules`

- `Rule(service, res, perm)` and `Rule.from_raw(value)`.
- `Enforcer(perms)` with `enforce(rule, do_raise=False, exc=None)` and
  `enforce_raw(raw_rule, do_raise=False, exc=None)`.
- `Grant.DENY` and `Grant.ALLOW`.

Rules must contain exactly three logical components; the third component may
contain dots because parsing uses at most two splits.

## `gcl_iam.middlewares`

- `GenesisCoreAuthMiddleware(application, iam_engine_driver, ...)` — creates the
  request IAM context. Optional parameters include `context_class`,
  `context_kwargs`, `readonly_whitelist`, and `skip_auth_endpoints`.
- `EndpointComparator(path, methods=None)` — regex full-match comparator;
  methods default to `GET`.
- `ErrorsHandlerMiddleware` — maps IAM exceptions to HTTP 400, 401 or 403.

Error responses use OAuth-style identifiers such as `invalid_client`,
`invalid_token` and `invalid_grant`; forbidden policy errors return HTTP 403.

## `gcl_iam.api.controllers`

- `PolicyBasedControllerMixin`
- `PolicyBasedController`
- `NestedPolicyBasedController`
- `PolicyBasedWithoutProjectController`
- `PolicyBasedCheckOtpController`

The default CRUD action mapping is `create`, `read`, `update`, `delete`, with
filter mapped to `read`.

## `gcl_iam.api.field_perms`

- `FieldsIamPermissions(fields, default=Permissions.RW)` — per-method
  RESTAlchemy field permissions with `Rule` support.
- `Permissions` — alias of RESTAlchemy's permissions enum/container.

## `gcl_iam.opts`

- `register_iam_cli_opts(conf)` — registers `iam_endpoint`, `audience` and
  secret `hs256_jwks_decryption_key` options in the `iam` group.

## Exceptions

The main families are:

- `CredentialsAreInvalidError` and its token/OTP subclasses;
- `ClientAuthenticationError`, `Unauthorized` and
  `TokenAudienceMismatchError`;
- `CommonForbiddenError`, `PolicyNotAuthorized` and `Forbidden`; and
- context session errors.

Catch the narrowest useful class in application code. In HTTP applications,
prefer `ErrorsHandlerMiddleware` over manual exception-to-response conversion.
