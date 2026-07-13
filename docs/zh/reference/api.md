# 公共 API 参考

精确签名以安装版本为准；minor release 可能增加可选参数。

## `gcl_iam.algorithms`

`HS256`、`RS256`、`RS256VerifyOnly` 支持当前/旧 key；RSA helper 生成
2048/3072/4096 位 PKCS#8 key、导出公钥/位数/JWK；HS256 JWKS helper 以 32
字节 A256GCM key 加解密 `aesgcm:` 格式。`decode` 可设置 audience、过期与验证
选项，但关闭验证绝不能用于授权。

## `gcl_iam.tokens`

包括 `UnverifiedToken`、`VerifiedToken`、`AuthToken`、`IdToken`、
`RefreshToken`、`AnonymousToken`。为兼容现有 API，属性名必须使用历史拼写
`autenticated_at`。

## `gcl_iam.drivers`

包括 `AbstractAuthDriver`、`HttpDriver`、`DummyDriver`、`AnonDriver`、
`HS256AlgorithmKeys`、`RS256AlgorithmKeys`。`HttpDriver` 可选参数默认值为
`default_timeout=5`、`cache_maxsize=100`、`cache_ttl_seconds=300`。

## `gcl_iam.engines` 与 `gcl_iam.contexts`

`IamEngine` 组合 token、introspection 和 `Enforcer`；`IntrospectionInfo`/
`UserInfo` 提供 typed accessor；`GenesisCoreAuthContext` 管理 IAM session、proxy
URL 和客户端 IP。

## `gcl_iam.enforcers` 与 `gcl_iam.rules`

提供 `Rule`/`Rule.from_raw`、`Enforcer.enforce`/`enforce_raw`、
`Grant.DENY`/`ALLOW`。第三段规则允许包含点。

## `gcl_iam.middlewares`

包括 `GenesisCoreAuthMiddleware`、执行 regex full match（默认 GET）的
`EndpointComparator`，以及将异常映射为 HTTP 400/401/403 的
`ErrorsHandlerMiddleware`。

## `gcl_iam.api.controllers`

包括 `PolicyBasedControllerMixin`、`PolicyBasedController`、
`NestedPolicyBasedController`、`PolicyBasedWithoutProjectController`、
`PolicyBasedCheckOtpController`。CRUD 映射为 create/read/update/delete，filter
映射为 read。

## `gcl_iam.api.field_perms`

`FieldsIamPermissions(fields, default=Permissions.RW)` 与 RESTAlchemy
`Permissions` alias。

## `gcl_iam.opts`

`register_iam_cli_opts(conf)` 在 `iam` 组注册 `iam_endpoint`、`audience` 和 secret
`hs256_jwks_decryption_key`。

## 异常

主要包括 credentials/token/OTP、`ClientAuthenticationError`、Forbidden/Policy
和 context session 异常。应用应捕获最具体的类；HTTP 服务优先使用错误 middleware。
