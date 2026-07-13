# Разрешения, проекты и OTP

## Правила разрешений

Правило состоит из трёх частей:

```text
service.resource.action
```

```python
from gcl_iam import rules

read_document = rules.Rule("documents", "document", "read")
same_rule = rules.Rule.from_raw("documents.document.read")
```

`Enforcer` поддерживает `*` на уровне service, resource или action:

- `documents.document.read` — одно действие;
- `documents.document.*` — все действия над документом;
- `documents.*.*` — все разрешения сервиса документов;
- `*.*.*` — полный доступ, только для доверенных администраторов.

```python
from gcl_iam.enforcers import Enforcer

enforcer = Enforcer(["documents.document.read"])
grant = enforcer.enforce_raw("documents.document.read")
enforcer.enforce(read_document, do_raise=True)
```

Результат — `Grant.ALLOW` или `Grant.DENY`; значения поддерживают boolean и
сравнение.

## Выбор контроллера

| Контроллер | Назначение |
| --- | --- |
| `PolicyBasedController` | Верхнеуровневые ресурсы с `project_id`. |
| `NestedPolicyBasedController` | Ресурсы через parent; копирует/проверяет проект, если nested model имеет `project_id`. |
| `PolicyBasedWithoutProjectController` | Глобальные ресурсы без проектной принадлежности. |
| `PolicyBasedCheckOtpController` | Проектные ресурсы, где create, update и delete всегда требуют OTP. |
| `PolicyBasedControllerMixin` | Пользовательские иерархии, явно вызывающие helpers авторизации. |

Задайте `__policy_service_name__` и при необходимости `__policy_name__`. При
`__policy_name__ = None` resource-часть равна `default`.

## Project scope

Проверки разрешения и проекта суммируются. Scoped user должен иметь правило и
может обращаться только к introspected `project_id`.

`PolicyBasedController`:

- добавляет проект в create и filter;
- отклоняет конфликтующий проект клиента;
- применяет project filter перед get, update и delete;
- разрешает identity без scope и с нужным permission работать со всеми проектами.

Модель проектного контроллера должна содержать совместимое поле `project_id`.

## OTP

`PolicyBasedCheckOtpController` всегда требует `otp_verified=True` для create,
update и delete. Если token сообщает, что OTP включён, проверка требуется также
для get и filter.

Клиент передаёт код в `X-OTP`. Middleware преобразует его в integer и передаёт
в introspection драйвера; валидацию выполняет драйвер.

## Разрешения полей

`FieldsIamPermissions` дополняет field permissions RESTAlchemy правилами IAM:

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

Разрешённое IAM-правило становится `RW`, запрещённое — `HIDDEN`. Их можно
смешивать с `RW`, `RO` и `HIDDEN` RESTAlchemy и задавать по API-методам.
