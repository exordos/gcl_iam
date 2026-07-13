# 权限、项目与 OTP

## 权限规则

规则格式为 `service.resource.action`：

```python
from gcl_iam import rules
read_document = rules.Rule("documents", "document", "read")
same_rule = rules.Rule.from_raw("documents.document.read")
```

`Enforcer` 各层支持 `*`。`documents.document.read` 只授予 read，
`documents.document.*` 授予所有文档操作，`documents.*.*` 授予整个服务，
`*.*.*` 仅应给可信管理员。

```python
from gcl_iam.enforcers import Enforcer
enforcer = Enforcer(["documents.document.read"])
grant = enforcer.enforce_raw("documents.document.read")
enforcer.enforce(read_document, do_raise=True)
```

结果为可作布尔值的 `Grant.ALLOW` 或 `Grant.DENY`。

## 控制器选择

| 控制器 | 用途 |
| --- | --- |
| `PolicyBasedController` | 含 `project_id` 的顶层资源。 |
| `NestedPolicyBasedController` | 通过 parent 访问的嵌套资源。 |
| `PolicyBasedWithoutProjectController` | 不属于项目的全局资源。 |
| `PolicyBasedCheckOtpController` | create/update/delete 必须验证 OTP 的项目资源。 |
| `PolicyBasedControllerMixin` | 显式调用授权 helper 的自定义层次。 |

设置 `__policy_service_name__` 和可选的 `__policy_name__`；后者为 `None` 时资源名
为 `default`。

## Project scope

权限与项目检查同时生效。scoped 用户既要有规则，又只能访问 introspection 的
`project_id`。控制器为 create/filter 注入项目，在 get/update/delete 前过滤项目，
并拒绝冲突值。模型必须有兼容的 `project_id`。

## OTP

`PolicyBasedCheckOtpController` 的 create/update/delete 总要求
`otp_verified=True`；若 token 表示启用 OTP，get/filter 也要求验证。客户端以
`X-OTP` 发送代码，由驱动验证。

## 字段权限

```python
from gcl_iam import rules
from gcl_iam.api import field_perms
from restalchemy.api import constants

permissions = field_perms.FieldsIamPermissions(
    default=field_perms.Permissions.RW,
    fields={
        "created_at": {constants.ALL: field_perms.Permissions.RO},
        "internal_note": {
            constants.ALL: rules.Rule("documents", "internal_note", "read")
        },
        "secret": {constants.ALL: field_perms.Permissions.HIDDEN},
    },
)
```

允许的 IAM 规则变为 `RW`，拒绝时变为 `HIDDEN`；可与 RESTAlchemy 的
`RW`/`RO`/`HIDDEN` 和按方法规则组合。
