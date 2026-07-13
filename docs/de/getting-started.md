# Erste Schritte

Dieses Beispiel schützt eine RESTAlchemy-API mit einem entfernten IAM-Dienst
und einem projektbezogenen Controller.

## 1. IAM-Treiber erstellen

```python
from gcl_iam import drivers

iam_driver = drivers.HttpDriver(
    iam_endpoint="https://iam.example.com/v1/iam/clients/my-service",
    audience="my-service",
    hs256_jwks_decryption_key="<load from secret storage>",
)
```

Der Endpunkt erhält einen abschließenden Slash. Der Treiber lädt Schlüssel von
`actions/jwks`, cached den Algorithmus standardmäßig fünf Minuten und ruft für
jeden authentifizierten Request `actions/introspect` auf. `aud` muss `audience` entsprechen.

## 2. Middleware einbinden

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

`EndpointComparator` verwendet einen vollständigen Regex-Match. Patterns sind
passend zu maskieren und erlaubte HTTP-Methoden explizit anzugeben.

IAM-Controller dürfen nicht auf übersprungenen Endpunkten laufen: Dort wird
auch keine IAM-Session in den Kontext geschrieben.

## 3. Controller schützen

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

| Operation | Erforderliche Regel |
| --- | --- |
| Create | `documents.document.create` |
| Get oder Filter | `documents.document.read` |
| Update | `documents.document.update` |
| Delete | `documents.document.delete` |

Enthält die Introspection eine `project_id`, setzt der Controller sie bei
Erstellung und Abfragen und lehnt andere Projekte ab. Eine unscoped Identität
mit Berechtigung kann projektübergreifend arbeiten.

## 4. Request senden

```http
GET /v1/documents/ HTTP/1.1
Host: api.example.com
Authorization: Bearer <JWT>
```

Die Middleware:

1. dekodiert den ungeprüften Token nur zur Ermittlung der Audience;
2. bezieht vom Treiber einen HS256- oder RS256-Prüfer;
3. prüft Signatur und Ablaufzeit;
4. introspektiert den geprüften Token;
5. erstellt `IamEngine` und speichert ihn im Request-Kontext;
6. lässt `documents.document.read` und Projektscope prüfen.

Ohne `Authorization` entsteht ein anonymer Kontext ohne Berechtigungen.
Öffentliche Endpunkte müssen übersprungen oder bewusst anonym behandelt werden.

## 5. Identitätsdaten lesen

```python
from restalchemy.common import contexts

iam = contexts.get_context().iam_context
user = iam.get_introspection_info().user_info

print(user.uuid)
print(user.email)
print(iam.get_introspection_info().project_id)
```

Weitere Details stehen unter [Authentifizierung und Kontext](concepts/authentication-and-context.md)
und [Autorisierung](concepts/authorization.md).
