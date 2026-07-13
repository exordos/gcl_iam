# Справочник публичного API

Здесь перечислены публичные блоки исходного дерева. Точные сигнатуры смотрите в
установленной версии: minor release может добавлять необязательные параметры.

## `gcl_iam.algorithms`

- `HS256(key, previous_key=None)` — подпись и проверка HS256 JWT.
- `RS256(private_key, public_key, previous_public_key=None)` — подпись и проверка RS256.
- `RS256VerifyOnly(public_key, previous_public_key=None)` — только проверка RS256.
- `generate_rsa_private_key_pem(bitness=2048, public_exponent=65537)` — PKCS#8
  RSA key без шифрования; размеры 2048, 3072 и 4096.
- `generate_rsa_public_key_pem(private_key_pem)` — получить public PEM.
- `get_rsa_bitness_from_private_key_pem(private_key_pem)` — размер ключа.
- `public_pem_to_jwk(public_key_pem)` — RSA public key в JWK.
- `encrypt_hs256_jwks_secret` и `decrypt_hs256_jwks_secret` — A256GCM с
  32-байтным ключом; сериализация начинается с `aesgcm:`.

`BaseJwtAlgorithm.decode` принимает `audience`, `ignore_audience`,
`ignore_expiration` и `verify`. Отключение проверки допустимо только для
контролируемой диагностики и не должно авторизовывать запрос.

## `gcl_iam.tokens`

- `UnverifiedToken` — непроверенные claims только для выбора драйвера/ключа.
- `VerifiedToken` — общие проверенные claims и UTC timestamps.
- `AuthToken` — `token_type`, `otp_enabled` и время аутентификации.
- `IdToken` — имя и email пользователя.
- `RefreshToken` — представление проверенного refresh token.
- `AnonymousToken` — фиксированная анонимная identity.

Историческое public property `autenticated_at` написано именно так; для
совместимости используйте это имя.

## `gcl_iam.drivers`

- `AbstractAuthDriver` — контракт custom driver.
- `HttpDriver` — remote JWKS и introspection.
- `DummyDriver` — настраиваемый test driver.
- `AnonDriver` — встроенный anonymous introspection.
- `HS256AlgorithmKeys` и `RS256AlgorithmKeys` — immutable key containers для тестов.

После трёх обязательных значений `HttpDriver` принимает `default_timeout=5`,
`cache_maxsize=100`, `cache_ttl_seconds=300`.

## `gcl_iam.engines` и `gcl_iam.contexts`

- `IamEngine` — token, introspection и `Enforcer`.
- `IntrospectionInfo` и `UserInfo` — typed accessors.
- `GenesisCoreAuthContext` — IAM session, proxy URL и client IP.

## `gcl_iam.enforcers` и `gcl_iam.rules`

- `Rule(service, res, perm)` и `Rule.from_raw(value)`.
- `Enforcer(perms)` с `enforce(...)` и `enforce_raw(...)`.
- `Grant.DENY` и `Grant.ALLOW`.

Правило содержит три логические части; третья может включать точки, так как
parser делает не больше двух splits.

## `gcl_iam.middlewares`

- `GenesisCoreAuthMiddleware(application, iam_engine_driver, ...)` — IAM context;
  опции: `context_class`, `context_kwargs`, `readonly_whitelist`, `skip_auth_endpoints`.
- `EndpointComparator(path, methods=None)` — regex full match; default `GET`.
- `ErrorsHandlerMiddleware` — IAM exceptions в HTTP 400, 401 или 403.

Ответы используют `invalid_client`, `invalid_token`, `invalid_grant`; policy deny
возвращает HTTP 403.

## `gcl_iam.api.controllers`

- `PolicyBasedControllerMixin`
- `PolicyBasedController`
- `NestedPolicyBasedController`
- `PolicyBasedWithoutProjectController`
- `PolicyBasedCheckOtpController`

CRUD mapping: `create`, `read`, `update`, `delete`; filter соответствует `read`.

## `gcl_iam.api.field_perms`

- `FieldsIamPermissions(fields, default=Permissions.RW)` — field permissions с `Rule`.
- `Permissions` — alias permissions RESTAlchemy.

## `gcl_iam.opts`

- `register_iam_cli_opts(conf)` — регистрирует `iam_endpoint`, `audience` и
  secret `hs256_jwks_decryption_key` в группе `iam`.

## Исключения

Основные семейства:

- `CredentialsAreInvalidError` и token/OTP subclasses;
- `ClientAuthenticationError`, `Unauthorized`, `TokenAudienceMismatchError`;
- `CommonForbiddenError`, `PolicyNotAuthorized`, `Forbidden`;
- ошибки context session.

В коде ловите наиболее узкий класс. В HTTP-приложении предпочитайте
`ErrorsHandlerMiddleware` ручному преобразованию исключений.
