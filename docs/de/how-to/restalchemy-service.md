# RESTAlchemy-Dienst integrieren

## Treiber nach dem Konfigurationsparsing erstellen

```python
from gcl_iam import drivers
from gcl_iam import opts as iam_opts
from oslo_config import cfg

CONF = cfg.CONF
iam_opts.register_iam_cli_opts(CONF)
# Dienstkonfiguration hier einlesen.
iam_driver = drivers.HttpDriver(
    CONF.iam.iam_endpoint, CONF.iam.audience,
    CONF.iam.hs256_jwks_decryption_key,
    default_timeout=5, cache_maxsize=100, cache_ttl_seconds=300,
)
```

## Middleware in der Application Factory ergänzen

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

Eigene Error-Middleware sollte von `gcl_iam.middlewares.ErrorsHandlerMiddleware`
erben, damit IAM-Status und Antwortformat erhalten bleiben.

## Controller auswählen

```python
class ServersController(iam_controllers.PolicyBasedController):
    __policy_service_name__ = "compute"
    __policy_name__ = "server"
    __resource__ = resources.ResourceByRAModel(model_class=Server)
```

```python
class RegionsController(iam_controllers.PolicyBasedWithoutProjectController):
    __policy_service_name__ = "compute"
    __policy_name__ = "region"
    __resource__ = resources.ResourceByRAModel(model_class=Region)
```

```python
class ServerPortsController(iam_controllers.NestedPolicyBasedController):
    __policy_service_name__ = "compute"
    __policy_name__ = "port"
    __resource__ = resources.ResourceByRAModel(model_class=Port)
```

Für OTP-pflichtige Mutationen dient `PolicyBasedCheckOtpController`.

## Eigene Aktion schützen

Eine eigene Aktion verwendet die im Controller konfigurierten Dienst- und
Ressourcennamen:

```python
def rotate_credentials(self, resource):
    self._enforce("rotate_credentials")
    # Aktion ausführen.
```

Bei frei adressierbaren Ressourcen zusätzlich den Projektscope über
`_force_project_id` oder einen projektgefilterten Load prüfen.

## Feldsichtbarkeit anpassen

`FieldsIamPermissions` an eine RESTAlchemy-Ressource mit `fields_permissions`
übergeben. Dauerhaft sensible Werte bleiben `HIDDEN`.

## Integration testen

```python
from gcl_iam import drivers

driver = drivers.DummyDriver()
driver.permissions = ["compute.server.*"]
driver.project_id = "11111111-1111-1111-1111-111111111111"
driver.algorithm_keys["my-service"] = drivers.HS256AlgorithmKeys(
    key="test-only-signing-key"
)
```

`DummyDriver` ist nur für Tests; seine Admin-Identität darf nicht produktiv
laufen. Zu testen sind fehlende/defekte Tokens, falsche Audience, Deny,
falsches Projekt, Rotation, OTP-Fehler und versteckte Felder.
