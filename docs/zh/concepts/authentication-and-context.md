# 认证与请求上下文

## 请求生命周期

`GenesisCoreAuthMiddleware` 在控制器前执行：读取 bearer token；以
`UnverifiedToken` 取得未受信的 `aud`；向驱动获取算法；以 `AuthToken` 验证签名
和过期时间；执行 introspection 并转发 `X-OTP`；创建 `IamEngine`/`Enforcer`；在
请求期间保存到 `GenesisCoreAuthContext.iam_context`。

无效 token 变为 `InvalidAuthTokenError`。没有 token 时通过 `AnonDriver` 创建
`AnonymousToken`，而不是跳过 middleware。

## 驱动契约

```python
class AbstractAuthDriver:
    def get_algorithm(self, token_info): ...
    def get_introspection_info(self, token_info, otp_code=None): ...
```

算法对象提供 `encode`/`decode`，服务通常返回 `HS256` 或 `RS256VerifyOnly`。
introspection 至少返回：

```python
{
    "user_info": {
        "uuid": "...", "name": "...", "first_name": "...",
        "last_name": "...", "email": "...", "type": "...",
    },
    "project_id": "...",  # 或 None
    "otp_verified": True,
    "permissions": ["service.resource.action"],
}
```

`IamEngine` 从 auth token 添加 `otp_enabled`。

## HttpDriver

`HttpDriver` 在网络请求前验证 audience，支持 `kty="oct"` 且以 A256GCM 加密
secret 的 HS256 JWKS、含 `kty="RSA"`/`n`/`e` 的 RS256 JWKS、第二把旧 key，
以及可配置 timeout/cache/TTL。仅缓存算法/JWKS；每个请求都执行 introspection。

## 上下文数据

```python
from restalchemy.common import contexts

engine = contexts.get_context().iam_context
raw = engine.introspection_info()
typed = engine.get_introspection_info()
token = engine.token_info
enforcer = engine.enforcer
```

`typed.user_info` 提供用户字段，`project_id` 会转换为 `uuid.UUID`。上下文仅在当前
请求有效；session 外访问或嵌套 IAM session 会抛出异常。

## Proxy 信息

`get_real_url_with_prefix()` 处理 `X-Forwarded-*` URL header；`get_user_ip()`
依次检查 `X-Forwarded-For`、`X-Real-IP`、request 地址和 `REMOTE_ADDR`。只应信任
来自可信 reverse proxy 的 forwarded header。
