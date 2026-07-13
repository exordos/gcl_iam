# Permissions, projects and OTP

## Permission rules

A rule has three dot-separated parts:

```text
service.resource.action
```

Create rules directly or parse them:

```python
from gcl_iam import rules

read_document = rules.Rule("documents", "document", "read")
same_rule = rules.Rule.from_raw("documents.document.read")
```

`Enforcer` supports `*` at the service, resource or action level. For example:

- `documents.document.read` grants one action;
- `documents.document.*` grants every action on documents;
- `documents.*.*` grants every documents-service permission;
- `*.*.*` grants everything and should be reserved for trusted administrators.

```python
from gcl_iam.enforcers import Enforcer

enforcer = Enforcer(["documents.document.read"])
grant = enforcer.enforce_raw("documents.document.read")

# Raise PolicyNotAuthorized when denied.
enforcer.enforce(read_document, do_raise=True)
```

The return value is `Grant.ALLOW` or `Grant.DENY`; both are boolean-compatible
and ordered.

## Controller choices

| Controller | Use it for |
| --- | --- |
| `PolicyBasedController` | Top-level resources with a `project_id`. |
| `NestedPolicyBasedController` | Resources reached through a parent; it copies/enforces project scope when the nested model has `project_id`. |
| `PolicyBasedWithoutProjectController` | Global resources that do not have project ownership. |
| `PolicyBasedCheckOtpController` | Project resources where create, update and delete always require verified OTP. |
| `PolicyBasedControllerMixin` | Custom controller hierarchies that call its enforcement helpers explicitly. |

Set `__policy_service_name__` and optionally `__policy_name__`. If
`__policy_name__` is `None`, the resource part is `default`.

## Project scope

Permission and project checks are cumulative. A scoped user must have the
required rule and may access only the introspected `project_id`.

`PolicyBasedController`:

- injects the scoped project into create and filter arguments;
- rejects a conflicting project passed by the client;
- applies the project filter before get, update or delete; and
- allows a permission-bearing unscoped identity to work across projects.

The model used by a project-aware controller must expose a compatible
`project_id` property.

## OTP

`PolicyBasedCheckOtpController` always requires `otp_verified=True` for create,
update and delete. If the auth token says OTP is enabled, it also requires a
verified OTP for get and filter.

Clients pass the one-time code in `X-OTP`. The middleware converts it to an
integer and forwards it to driver introspection. Drivers decide how to validate
the code.

## Field permissions

`FieldsIamPermissions` extends RESTAlchemy field permissions with IAM rules:

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

A granted IAM rule becomes `RW`; a denied rule becomes `HIDDEN`. Ordinary
RESTAlchemy `RW`, `RO` and `HIDDEN` permissions can be mixed with rules and can
vary by API method.
