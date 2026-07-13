# Быстрый старт

В этом руководстве RESTAlchemy API защищается удалённым IAM-сервисом и
контроллером с проектной областью.

## 1. Создайте IAM-драйвер

```python
from gcl_iam import drivers

iam_driver = drivers.HttpDriver(
    iam_endpoint="https://iam.example.com/v1/iam/clients/my-service",
    audience="my-service",
    hs256_jwks_decryption_key="<load from secret storage>",
)
```

Endpoint нормализуется завершающим `/`. Драйвер получает ключи из
`actions/jwks`, по умолчанию кэширует алгоритм на пять минут и вызывает
`actions/introspect` для каждого аутентифицированного запроса. Claim `aud`
должен совпадать с `audience`.

## 2. Подключите middleware

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

`EndpointComparator` выполняет полное совпадение регулярного выражения. При
необходимости экранируйте pattern и явно перечисляйте HTTP-методы.

Не используйте IAM-контроллеры на пропущенном endpoint: при пропуске
аутентификации IAM-сессия также не сохраняется в контексте.

## 3. Защитите контроллер

```python
from gcl_iam.api import controllers as iam_controllers
from restalchemy.api import resources


class DocumentsController(iam_controllers.PolicyBasedController):
    __policy_service_name__ = "documents"
    __policy_name__ = "document"

    __resource__ = resources.ResourceByRAModel(
        model_class=Document,
        convert_underscore=False,
    )
```

CRUD-методам нужны следующие разрешения:

| Операция | Правило |
| --- | --- |
| Create | `documents.document.create` |
| Get или filter | `documents.document.read` |
| Update | `documents.document.update` |
| Delete | `documents.document.delete` |

Если introspection содержит `project_id`, контроллер добавляет его к аргументам
создания и запросов и отклоняет другой проект. Identity без project scope, но с
нужным разрешением может работать со всеми проектами.

## 4. Отправьте запрос

```http
GET /v1/documents/ HTTP/1.1
Host: api.example.com
Authorization: Bearer <JWT>
```

Middleware выполняет следующие действия:

1. Декодирует непроверенный токен только для определения audience.
2. Запрашивает у драйвера verifier HS256 или RS256.
3. Проверяет подпись и срок действия.
4. Выполняет introspection проверенного токена.
5. Создаёт `IamEngine` и сохраняет его в контексте запроса.
6. Контроллер проверяет `documents.document.read` и project scope.

Без `Authorization` middleware создаёт анонимный контекст без разрешений.
Публичные endpoint следует явно пропускать или обрабатывать кодом, который
осознанно поддерживает анонимную identity.

## 5. Получите данные identity

```python
from restalchemy.common import contexts

iam = contexts.get_context().iam_context
user = iam.get_introspection_info().user_info

print(user.uuid)
print(user.email)
print(iam.get_introspection_info().project_id)
```

Полный lifecycle описан в разделе [аутентификация и контекст](concepts/authentication-and-context.md),
а выбор контроллера — в разделе [авторизация](concepts/authorization.md).
