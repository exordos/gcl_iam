# Integrate a RESTAlchemy service

## Build the driver after configuration parsing

```python
from gcl_iam import drivers
from gcl_iam import opts as iam_opts
from oslo_config import cfg

CONF = cfg.CONF
iam_opts.register_iam_cli_opts(CONF)

# Parse your service configuration here.

iam_driver = drivers.HttpDriver(
    CONF.iam.iam_endpoint,
    CONF.iam.audience,
    CONF.iam.hs256_jwks_decryption_key,
    default_timeout=5,
    cache_maxsize=100,
    cache_ttl_seconds=300,
)
```

## Add middleware in the application factory

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

If the service already subclasses its RESTAlchemy error middleware, inherit
from `gcl_iam.middlewares.ErrorsHandlerMiddleware` so IAM exceptions retain
their status and response shape.

## Select a controller

Project-scoped model:

```python
class ServersController(iam_controllers.PolicyBasedController):
    __policy_service_name__ = "compute"
    __policy_name__ = "server"
    __resource__ = resources.ResourceByRAModel(model_class=Server)
```

Global model:

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

Use `PolicyBasedCheckOtpController` instead of `PolicyBasedController` when all
mutations must be protected by OTP.

## Protect a custom action

CRUD methods are protected by the concrete controllers. A custom action should
enforce its own explicit action using the controller's configured service and
resource names:

```python
def rotate_credentials(self, resource):
    self._enforce("rotate_credentials")
    # Perform the action.
```

Apply a project check as well when the custom action can address an arbitrary
resource. Reuse `_force_project_id` or load the model through a project-filtered
controller method.

## Customize field visibility

Pass `FieldsIamPermissions` to a RESTAlchemy resource that supports
`fields_permissions`. Keep permanently sensitive values `HIDDEN`; use IAM rules
only for fields that are safe to reveal to authorized callers.

## Test the integration

For isolated tests use `DummyDriver` and configure the audience keys:

```python
from gcl_iam import drivers

driver = drivers.DummyDriver()
driver.permissions = ["compute.server.*"]
driver.project_id = "11111111-1111-1111-1111-111111111111"
driver.algorithm_keys["my-service"] = drivers.HS256AlgorithmKeys(
    key="test-only-signing-key"
)
```

`DummyDriver` is intended for tests. Do not deploy its default administrator
identity or `*.*.*` permission in production.

Test at least missing tokens, malformed tokens, wrong audiences, denied rules,
wrong project IDs, key rotation, OTP failures and field hiding.
