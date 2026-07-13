# 实现自定义驱动

当 key/introspection 位于进程内、其他协议或不同 IAM API 时使用自定义驱动。

## 实现接口

```python
from gcl_iam import algorithms, drivers

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
                "uuid": str(session.user.uuid), "name": session.user.name,
                "first_name": session.user.first_name,
                "last_name": session.user.last_name,
                "email": session.user.email, "type": session.user.type,
            },
            "project_id": str(session.project_id) if session.project_id else None,
            "otp_verified": verify_otp(session.user, otp_code),
            "permissions": list(session.permissions),
        }
```

示例 helper 属于应用，不由 `gcl_iam` 提供。

## 安全要求

只按未验证 audience 选择 key，不信任其他未验证 claim；尽早拒绝未知 audience；
仅验证的服务返回 `RS256VerifyOnly`；introspection 检查活动 session/token 并返回
最新权限；fail closed；绝不记录 token、私钥、对称 secret 或 OTP。

## Key 轮换

```python
algorithm = algorithms.HS256(key=current_secret, previous_key=previous_secret)
```

或 `RS256VerifyOnly(public_key=current_public_key,
previous_public_key=previous_public_key)`。编码用当前 key，解码依次尝试当前/旧
key；旧 token 全部过期后再移除旧 key。

## 匿名访问

无 bearer token 时 middleware 使用自己的 `AnonDriver`，不会调用自定义驱动。
匿名上下文无权限、无项目。更丰富的匿名行为必须在 route/controller 或经审查的
middleware 子类中显式实现。
