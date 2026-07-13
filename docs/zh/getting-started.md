# 入门

本指南用远程 IAM 服务和项目范围控制器保护 RESTAlchemy API。

## 1. 创建 IAM 驱动

```python
from gcl_iam import drivers

iam_driver = drivers.HttpDriver(
    iam_endpoint="https://iam.example.com/v1/iam/clients/my-service",
    audience="my-service",
    hs256_jwks_decryption_key="<load from secret storage>",
)
```

驱动从 `actions/jwks` 获取 key，默认缓存算法五分钟，并为每个认证请求调用
`actions/introspect`。token 的 `aud` 必须等于 `audience`。

## 2. 挂载 middleware

```python
from gcl_iam import middlewares as iam_middlewares
from restalchemy.api import middlewares

application = middlewares.attach_middlewares(
    application,
    [
        middlewares.configure_middleware(
            iam_middlewares.GenesisCoreAuthMiddleware,
            iam_engine_driver=iam_driver,
            skip_auth_endpoints=[
                iam_middlewares.EndpointComparator(r"/health", methods=["GET"]),
            ],
        ),
        iam_middlewares.ErrorsHandlerMiddleware,
    ],
)
```

`EndpointComparator` 执行正则完整匹配。请正确转义 pattern，并明确列出 HTTP
方法。跳过认证也不会建立 IAM session，因此跳过的 endpoint 不能运行 IAM 控制器。

## 3. 保护控制器

```python
from gcl_iam.api import controllers as iam_controllers
from restalchemy.api import resources

class DocumentsController(iam_controllers.PolicyBasedController):
    __policy_service_name__ = "documents"
    __policy_name__ = "document"
    __resource__ = resources.ResourceByRAModel(
        model_class=Document, convert_underscore=False,
    )
```

| 操作 | 所需规则 |
| --- | --- |
| Create | `documents.document.create` |
| Get/Filter | `documents.document.read` |
| Update | `documents.document.update` |
| Delete | `documents.document.delete` |

若 introspection 含 `project_id`，控制器会注入该项目并拒绝其他项目；拥有权限且
没有 project scope 的身份可跨项目操作。

## 4. 发送请求

```http
GET /v1/documents/ HTTP/1.1
Host: api.example.com
Authorization: Bearer <JWT>
```

流程为：读取未验证 audience；获取 HS256/RS256 verifier；验证签名和过期时间；
introspect token；建立 `IamEngine` 上下文；检查规则和 project scope。

没有 `Authorization` 时会建立无权限的匿名上下文。公共 endpoint 应明确跳过或由
显式支持匿名身份的代码处理。

## 5. 读取身份数据

```python
from restalchemy.common import contexts

iam = contexts.get_context().iam_context
user = iam.get_introspection_info().user_info
print(user.uuid)
print(user.email)
print(iam.get_introspection_info().project_id)
```

详见[认证与上下文](concepts/authentication-and-context.md)和
[授权](concepts/authorization.md)。
