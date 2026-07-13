# Установка

## Установка пакета

`gcl_iam` требует Python 3.10 или новее.

```bash
python -m pip install gcl_iam
```

Для разработки из checkout используйте стандартное tox-окружение репозитория:

```bash
tox -e develop
```

Окружение создаётся в `.tox/develop`.

## Настройка runtime

Сервису со встроенным `HttpDriver` нужны три значения:

| Параметр | Назначение |
| --- | --- |
| `iam_endpoint` | Специфичный для клиента IAM endpoint. Драйвер вызывает вложенные `actions/jwks` и `actions/introspect`. |
| `audience` | Ожидаемое значение JWT claim `aud` для сервиса. |
| `hs256_jwks_decryption_key` | 32-байтный ключ A256GCM для расшифровки секретов HS256 из JWKS; raw UTF-8 или URL-safe base64. |

Приложения с `oslo.config` могут зарегистрировать параметры в группе `iam`:

```python
from gcl_iam import opts as iam_opts
from oslo_config import cfg

iam_opts.register_iam_cli_opts(cfg.CONF)
```

После разбора конфигурации создайте драйвер:

```python
from gcl_iam import drivers

iam_driver = drivers.HttpDriver(
    cfg.CONF.iam.iam_endpoint,
    cfg.CONF.iam.audience,
    cfg.CONF.iam.hs256_jwks_decryption_key,
)
```

## Работа с секретами

Ключ расшифровки HS256 JWKS и ключи подписи являются секретами:

- загружайте их из secret manager или защищённой runtime-конфигурации;
- не сохраняйте их в репозитории;
- не включайте их в логи и отчёты об ошибках;
- при ротации используйте текущий и предыдущий ключи, как описано в справочнике.

Потребители RS256 получают публичные ключи из JWKS и не нуждаются в приватном
ключе. Создавать `RS256` с приватным ключом должны только издатели токенов.

## Проверка установки

```bash
python -c "from gcl_iam.enforcers import Enforcer; assert Enforcer(['demo.item.read']).enforce_raw('demo.item.read')"
```

Если импорт и механизм разрешений работают, команда завершится без вывода.
