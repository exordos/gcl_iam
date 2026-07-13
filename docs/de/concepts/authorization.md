# Berechtigungen, Projekte und OTP

## Berechtigungsregeln

Eine Regel hat drei Teile: `service.resource.action`.

```python
from gcl_iam import rules

read_document = rules.Rule("documents", "document", "read")
same_rule = rules.Rule.from_raw("documents.document.read")
```

`Enforcer` unterstützt `*` auf jeder Ebene: `documents.document.read` gewährt
eine Aktion, `documents.document.*` alle Dokumentaktionen, `documents.*.*` den
gesamten Dienst und `*.*.*` alles. Letzteres ist nur für vertrauenswürdige
Administratoren geeignet.

```python
from gcl_iam.enforcers import Enforcer

enforcer = Enforcer(["documents.document.read"])
grant = enforcer.enforce_raw("documents.document.read")
enforcer.enforce(read_document, do_raise=True)
```

Das Ergebnis ist `Grant.ALLOW` oder `Grant.DENY` und boolesch nutzbar.

## Controller-Auswahl

| Controller | Verwendung |
| --- | --- |
| `PolicyBasedController` | Top-Level-Ressourcen mit `project_id`. |
| `NestedPolicyBasedController` | Ressourcen über Parent; prüft/kopiert den Scope bei `project_id`. |
| `PolicyBasedWithoutProjectController` | Globale Ressourcen ohne Projekt. |
| `PolicyBasedCheckOtpController` | Projektressourcen, deren Mutationen immer OTP erfordern. |
| `PolicyBasedControllerMixin` | Eigene Hierarchien, die Enforcement-Helfer explizit aufrufen. |

Setzen Sie `__policy_service_name__` und optional `__policy_name__`; bei `None`
lautet der Ressourcenteil `default`.

## Projektscope

Berechtigung und Projektprüfung gelten gemeinsam. Ein scoped Benutzer braucht
die Regel und darf nur auf die introspektierte `project_id` zugreifen.

`PolicyBasedController` setzt das Projekt bei Create/Filter, lehnt Konflikte
ab, filtert Get/Update/Delete und lässt unscoped Identitäten mit Berechtigung
projektübergreifend arbeiten. Das Modell muss ein kompatibles `project_id` besitzen.

## OTP

`PolicyBasedCheckOtpController` verlangt `otp_verified=True` immer für Create,
Update und Delete. Meldet der Token aktiviertes OTP, gilt dies auch für Get und
Filter. Clients senden `X-OTP`; der Treiber validiert den als Integer übergebenen Code.

## Feldberechtigungen

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

Eine gewährte IAM-Regel wird `RW`, eine verweigerte `HIDDEN`. Sie kann mit den
RESTAlchemy-Werten `RW`, `RO`, `HIDDEN` und methodenspezifischen Regeln kombiniert werden.
