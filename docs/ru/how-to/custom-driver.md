# Пользовательский драйвер

Пользовательский драйвер нужен, если ключи или introspection доступны внутри
процесса, через другой протокол или несовместимый IAM API.

## Реализуйте интерфейс

```python
from gcl_iam import algorithms
from gcl_iam import drivers


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
                "uuid": str(session.user.uuid),
                "name": session.user.name,
                "first_name": session.user.first_name,
                "last_name": session.user.last_name,
                "email": session.user.email,
                "type": session.user.type,
            },
            "project_id": (
                str(session.project_id) if session.project_id else None
            ),
            "otp_verified": verify_otp(session.user, otp_code),
            "permissions": list(session.permissions),
        }
```

Вспомогательные функции примера относятся к приложению и не входят в
`gcl_iam`.

## Требования безопасности

- Выбирайте ключ по непроверенному audience, но не доверяйте другим claims.
- Отклоняйте неизвестный audience до дорогой или внешней работы.
- В сервисах без выдачи токенов возвращайте `RS256VerifyOnly`.
- Проверяйте активность сессии/token при introspection.
- Возвращайте актуальные permissions и project scope.
- Fail closed: отсутствие пользователя, ключа или permissions не должно давать admin.
- Не логируйте token, private key, symmetric secret и OTP.

## Ротация ключей

Передайте текущий и предыдущий ключи проверки:

```python
algorithm = algorithms.HS256(
    key=current_secret,
    previous_key=previous_secret,
)
```

или:

```python
algorithm = algorithms.RS256VerifyOnly(
    public_key=current_public_key,
    previous_public_key=previous_public_key,
)
```

Encode использует текущий ключ. Decode сначала пробует текущий, затем
предыдущий. Удалите предыдущий после истечения всех подписанных им токенов.

## Анонимный доступ

Без bearer token `GenesisCoreAuthMiddleware` использует собственный
`AnonDriver`; custom driver не вызывается. Анонимный introspection не содержит
permissions и project. Более богатое анонимное поведение реализуйте явно на
уровне route/controller либо осторожно расширьте middleware.
