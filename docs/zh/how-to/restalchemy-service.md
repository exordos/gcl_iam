# 集成 RESTAlchemy 服务

## 解析配置后创建驱动

```python
from gcl_iam import drivers
from gcl_iam import opts as iam_opts
from oslo_config import cfg
CONF = cfg.CONF
iam_opts.register_iam_cli_opts(CONF)
# 在此解析服务配置。
iam_driver = drivers.HttpDriver(
    CONF.iam.iam_endpoint, CONF.iam.audience,
    CONF.iam.hs256_jwks_decryption_key,
    default_timeout=5, cache_maxsize=100, cache_ttl_seconds=300,
)
```

## 在 application factory 中添加 middleware

```python
from gcl_iam import middlewares as iam_middlewares
from restalchemy.api import middlewares

def build_wsgi_application(application, iam_driver):
    return middlewares.attach_middlewares(application, [
        middlewares.configure_middleware(
            iam_middlewares.GenesisCoreAuthMiddleware,
            iam_engine_driver=iam_driver,
            skip_auth_endpoints=[
                iam_middlewares.EndpointComparator(r"/health", methods=["GET"]),
            ],
        ),
        iam_middlewares.ErrorsHandlerMiddleware,
    ])
```

自定义错误 middleware 应继承 `gcl_iam.middlewares.ErrorsHandlerMiddleware`。

## 选择控制器

```python
class ServersController(iam_controllers.PolicyBasedController):
    __policy_service_name__ = "compute"; __policy_name__ = "server"
    __resource__ = resources.ResourceByRAModel(model_class=Server)
```

全局资源使用 `PolicyBasedWithoutProjectController`，嵌套资源使用
`NestedPolicyBasedController`，变更必须 OTP 时使用 `PolicyBasedCheckOtpController`。

## 保护自定义 action

自定义 action 使用控制器中配置的 service 和 resource 名称：

```python
def rotate_credentials(self, resource):
    self._enforce("rotate_credentials")
```

若 action 可指定任意资源，还要通过 `_force_project_id` 或项目过滤查询检查 scope。

## 自定义字段可见性

向支持 `fields_permissions` 的资源传入 `FieldsIamPermissions`；永久敏感字段应始终
保持 `HIDDEN`。

## 测试集成

```python
from gcl_iam import drivers
driver = drivers.DummyDriver()
driver.permissions = ["compute.server.*"]
driver.project_id = "11111111-1111-1111-1111-111111111111"
driver.algorithm_keys["my-service"] = drivers.HS256AlgorithmKeys(
    key="test-only-signing-key"
)
```

`DummyDriver` 仅用于测试，不能部署其默认管理员。测试缺失/损坏 token、错误
audience、deny、错误项目、key 轮换、OTP 失败和字段隐藏。
