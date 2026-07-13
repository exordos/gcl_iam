# Аутентификация и контекст запроса

## Lifecycle запроса

`GenesisCoreAuthMiddleware` выполняет аутентификацию до вызова контроллера.

Для bearer token он:

1. читает `Authorization: Bearer ...`;
2. создаёт `UnverifiedToken`, чтобы получить недоверенный claim `aud`;
3. запрашивает у драйвера подходящий алгоритм проверки;
4. создаёт `AuthToken`, проверяя подпись и срок действия;
5. запрашивает introspection и передаёт `X-OTP`, если он указан;
6. создаёт `IamEngine` и `Enforcer`;
7. сохраняет engine в `GenesisCoreAuthContext.iam_context` на время запроса.

Некорректный token превращается в `InvalidAuthTokenError`. При отсутствии token
через `AnonDriver` создаётся `AnonymousToken`; middleware не пропускается.

## Контракт драйвера

Каждый драйвер реализует два метода:

```python
class AbstractAuthDriver:
    def get_algorithm(self, token_info): ...
    def get_introspection_info(self, token_info, otp_code=None): ...
```

`get_algorithm` возвращает объект с `encode` и `decode`; сервисы обычно
возвращают `HS256` или `RS256VerifyOnly`. `get_introspection_info` возвращает как
минимум:

```python
{
    "user_info": {
        "uuid": "...",
        "name": "...",
        "first_name": "...",
        "last_name": "...",
        "email": "...",
        "type": "...",
    },
    "project_id": "...",  # или None
    "otp_verified": True,
    "permissions": ["service.resource.action"],
}
```

`IamEngine` добавляет `otp_enabled` из auth token.

## HttpDriver

`HttpDriver` — стандартная удалённая реализация. Она проверяет audience до
сетевого запроса и поддерживает:

- HS256 JWKS с `kty="oct"`; секреты шифруются
  `encrypt_hs256_jwks_secret` через A256GCM;
- RS256 JWKS с `kty="RSA"`, `n` и `e`;
- второй подходящий JWKS-ключ как предыдущий ключ ротации;
- настраиваемые HTTP timeout, размер кэша и TTL.

Кэшируется только выбор алгоритма/JWKS. Introspection выполняется для каждого
запроса, поэтому изменения разрешений, проекта и OTP применяются сразу.

## Данные контекста

Внутри аутентифицированного запроса:

```python
from restalchemy.common import contexts

engine = contexts.get_context().iam_context
raw = engine.introspection_info()
typed = engine.get_introspection_info()
token = engine.token_info
enforcer = engine.enforcer
```

`typed.user_info` содержит `uuid`, `name`, `first_name`, `last_name`, `email` и
`type`. `typed.project_id` при наличии преобразуется в `uuid.UUID`.

Контекст локален для запроса. Доступ вне IAM-сессии вызывает исключение.
Вложенные IAM-сессии запрещены, чтобы identity нельзя было случайно заменить.

## Данные reverse proxy

`GenesisCoreAuthContext` также предоставляет:

- `get_real_url_with_prefix()` с учётом `X-Forwarded-Proto`,
  `X-Forwarded-Host`, `X-Forwarded-Port` и `X-Forwarded-Prefix`;
- `get_user_ip()`, который проверяет `X-Forwarded-For`, `X-Real-IP`, адрес в
  request и затем `REMOTE_ADDR`.

Принимайте forwarded headers только от доверенных reverse proxy. Библиотека не
настраивает эту границу доверия.
