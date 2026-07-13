# Authentifizierung und Request-Kontext

## Request-Lebenszyklus

`GenesisCoreAuthMiddleware` authentifiziert vor dem Controller-Aufruf. Für einen Bearer-Token:

1. liest sie `Authorization: Bearer ...`;
2. ermittelt mit `UnverifiedToken` den noch nicht vertrauenswürdigen `aud`-Claim;
3. fragt den Treiber nach dem Prüfalgorithmus;
4. erstellt `AuthToken` und prüft Signatur und Ablaufzeit;
5. fragt Introspection ab und leitet gegebenenfalls `X-OTP` weiter;
6. erstellt `IamEngine` und `Enforcer`;
7. speichert die Engine während des Requests in `GenesisCoreAuthContext.iam_context`.

Ein ungültiger Token wird zu `InvalidAuthTokenError`. Ohne Token entsteht über
`AnonDriver` ein `AnonymousToken`; die Middleware wird dabei nicht übersprungen.

## Treibervertrag

```python
class AbstractAuthDriver:
    def get_algorithm(self, token_info): ...
    def get_introspection_info(self, token_info, otp_code=None): ...
```

`get_algorithm` liefert ein Objekt mit `encode` und `decode`, üblicherweise
`HS256` oder `RS256VerifyOnly`. Introspection liefert mindestens:

```python
{
    "user_info": {
        "uuid": "...", "name": "...", "first_name": "...",
        "last_name": "...", "email": "...", "type": "...",
    },
    "project_id": "...",  # oder None
    "otp_verified": True,
    "permissions": ["service.resource.action"],
}
```

`IamEngine` ergänzt `otp_enabled` aus dem Auth-Token.

## HttpDriver

`HttpDriver` prüft die Audience vor dem Netzwerkzugriff und unterstützt:

- HS256-JWKS mit `kty="oct"` und A256GCM-verschlüsselten Secrets;
- RS256-JWKS mit `kty="RSA"`, `n` und `e`;
- einen zweiten passenden JWKS-Schlüssel als Rotations-Fallback;
- konfigurierbares HTTP-Timeout, Cache-Größe und TTL.

Nur Algorithmus/JWKS werden gecached. Introspection erfolgt pro Request, sodass
Änderungen an Berechtigungen, Projekt und OTP sofort greifen.

## Kontextdaten

```python
from restalchemy.common import contexts

engine = contexts.get_context().iam_context
raw = engine.introspection_info()
typed = engine.get_introspection_info()
token = engine.token_info
enforcer = engine.enforcer
```

`typed.user_info` bietet `uuid`, `name`, `first_name`, `last_name`, `email` und
`type`; `project_id` wird gegebenenfalls zu `uuid.UUID`.

Der Kontext ist requestlokal. Zugriff außerhalb einer IAM-Session und
verschachtelte Sessions werden mit Kontextausnahmen abgelehnt.

## Proxy-Informationen

`get_real_url_with_prefix()` berücksichtigt `X-Forwarded-Proto`,
`X-Forwarded-Host`, `X-Forwarded-Port` und `X-Forwarded-Prefix`.
`get_user_ip()` prüft `X-Forwarded-For`, `X-Real-IP`, Request-Adressfelder und
`REMOTE_ADDR`. Forwarded Header dürfen nur von vertrauenswürdigen Proxys stammen.
