# Referenz der öffentlichen API

Die installierte Version ist für exakte Signaturen maßgeblich; Minor Releases
können optionale Parameter ergänzen.

## `gcl_iam.algorithms`

- `HS256(key, previous_key=None)` — HS256 signieren und prüfen.
- `RS256(private_key, public_key, previous_public_key=None)` — RS256 signieren/prüfen.
- `RS256VerifyOnly(public_key, previous_public_key=None)` — nur RS256-Prüfung.
- RSA-Helfer erzeugen PKCS#8-Schlüssel (2048/3072/4096), leiten Public PEM ab,
  lesen die Bitgröße und konvertieren Public PEM zu JWK.
- `encrypt_hs256_jwks_secret`/`decrypt_hs256_jwks_secret` schützen Secrets mit
  einem 32-Byte-A256GCM-Schlüssel; das Format beginnt mit `aesgcm:`.

`decode` bietet `audience`, `ignore_audience`, `ignore_expiration`, `verify`.
Deaktivierte Prüfung darf nie Requests autorisieren.

## `gcl_iam.tokens`

`UnverifiedToken`, `VerifiedToken`, `AuthToken`, `IdToken`, `RefreshToken` und
`AnonymousToken` bilden die Tokenarten ab. Der historische Property-Name
`autenticated_at` ist aus Kompatibilitätsgründen genau so zu verwenden.

## `gcl_iam.drivers`

`AbstractAuthDriver`, `HttpDriver`, `DummyDriver`, `AnonDriver` sowie
`HS256AlgorithmKeys` und `RS256AlgorithmKeys`. `HttpDriver` bietet zusätzlich
`default_timeout=5`, `cache_maxsize=100`, `cache_ttl_seconds=300`.

## `gcl_iam.engines` und `gcl_iam.contexts`

`IamEngine` kombiniert Token, Introspection und `Enforcer`;
`IntrospectionInfo`/`UserInfo` sind typisierte Zugriffe;
`GenesisCoreAuthContext` verwaltet IAM-Session, Proxy-URL und Client-IP.

## `gcl_iam.enforcers` und `gcl_iam.rules`

`Rule`, `Rule.from_raw`, `Enforcer.enforce`, `enforce_raw` sowie
`Grant.DENY`/`ALLOW`. Die dritte Regelkomponente darf Punkte enthalten.

## `gcl_iam.middlewares`

`GenesisCoreAuthMiddleware`, `EndpointComparator` (Regex-Full-Match, Standard
GET) und `ErrorsHandlerMiddleware` (HTTP 400/401/403 mit `invalid_client`,
`invalid_token`, `invalid_grant`).

## `gcl_iam.api.controllers`

`PolicyBasedControllerMixin`, `PolicyBasedController`,
`NestedPolicyBasedController`, `PolicyBasedWithoutProjectController` und
`PolicyBasedCheckOtpController`. CRUD mappt auf `create/read/update/delete`,
Filter auf `read`.

## `gcl_iam.api.field_perms`

`FieldsIamPermissions(fields, default=Permissions.RW)` und der RESTAlchemy-Alias
`Permissions`.

## `gcl_iam.opts`

`register_iam_cli_opts(conf)` registriert `iam_endpoint`, `audience` und das
geheime `hs256_jwks_decryption_key` in der Gruppe `iam`.

## Ausnahmen

Wichtige Familien sind Credentials-/Token-/OTP-Fehler,
`ClientAuthenticationError`, Forbidden-/Policy-Fehler und Kontextfehler.
Im Code möglichst spezifisch fangen; in HTTP-Diensten die Error-Middleware nutzen.
