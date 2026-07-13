# Интеграция сервиса RESTAlchemy

## Создайте драйвер после разбора конфигурации

```python
from gcl_iam import drivers
from gcl_iam import opts as iam_opts
from oslo_config import cfg

CONF = cfg.CONF
iam_opts.register_iam_cli_opts(CONF)

# Разберите конфигурацию сервиса здесь.

iam_driver = drivers.HttpDriver(
    CONF.iam.iam_endpoint,
    CONF.iam.audience,
    CONF.iam.hs256_jwks_decryption_key,
    default_timeout=5,
    cache_maxsize=100,
    cache_ttl_seconds=300,
)
```

## Добавьте middleware в application factory

```python
from gcl_iam import middlewares as iam_middlewares
from restalchemy.api import middlewares


def build_wsgi_application(application, iam_driver):
    return middlewares.attach_middlewares(
        application,
        [
            middlewares.configure_middleware(
                iam_middlewares.GenesisCoreAuthMiddleware,
                iam_engine_driver=iam_driver,
                skip_auth_endpoints=[
                    iam_middlewares.EndpointComparator(
                        r"/health",
                        methods=["GET"],
                    ),
                ],
            ),
            iam_middlewares.ErrorsHandlerMiddleware,
        ],
    )
```

Если сервис уже расширяет error middleware RESTAlchemy, наследуйте его от
`gcl_iam.middlewares.ErrorsHandlerMiddleware`, чтобы сохранить HTTP status и
формат IAM-ошибок.

## Выберите контроллер

Project-scoped model:

```python
class ServersController(iam_controllers.PolicyBasedController):
    __policy_service_name__ = "compute"
    __policy_name__ = "server"
    __resource__ = resources.ResourceByRAModel(model_class=Server)
```

Глобальная model:

```python
class RegionsController(iam_controllers.PolicyBasedWithoutProjectController):
    __policy_service_name__ = "compute"
    __policy_name__ = "region"
    __resource__ = resources.ResourceByRAModel(model_class=Region)
```

Nested model:

```python
class ServerPortsController(iam_controllers.NestedPolicyBasedController):
    __policy_service_name__ = "compute"
    __policy_name__ = "port"
    __resource__ = resources.ResourceByRAModel(model_class=Port)
```

Если все изменения требуют OTP, используйте `PolicyBasedCheckOtpController`.

## Защитите custom action

CRUD защищены конкретными контроллерами. Custom action проверяет своё действие,
используя service и resource, настроенные в контроллере:

```python
def rotate_credentials(self, resource):
    self._enforce("rotate_credentials")
    # Выполните действие.
```

Если action принимает произвольный ресурс, проверьте и проект через
`_force_project_id` либо загрузите модель project-filtered методом контроллера.

## Настройте видимость полей

Передайте `FieldsIamPermissions` в ресурс RESTAlchemy с поддержкой
`fields_permissions`. Постоянно чувствительные значения оставляйте `HIDDEN`;
IAM-правила применяйте только к полям, безопасным для авторизованных клиентов.

## Протестируйте интеграцию

Для изолированных тестов используйте `DummyDriver`:

```python
from gcl_iam import drivers

driver = drivers.DummyDriver()
driver.permissions = ["compute.server.*"]
driver.project_id = "11111111-1111-1111-1111-111111111111"
driver.algorithm_keys["my-service"] = drivers.HS256AlgorithmKeys(
    key="test-only-signing-key"
)
```

`DummyDriver` предназначен для тестов. Не разворачивайте его default admin
identity или permission `*.*.*` в production.

Проверяйте отсутствие и повреждение token, неправильный audience, deny,
чужой проект, ротацию ключей, ошибки OTP и скрытие полей.
