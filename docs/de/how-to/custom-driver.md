# Eigenen Treiber implementieren

Ein eigener Treiber eignet sich für prozessinterne Daten, andere Protokolle
oder eine abweichende IAM-API.

## Schnittstelle implementieren

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
                "uuid": str(session.user.uuid), "name": session.user.name,
                "first_name": session.user.first_name,
                "last_name": session.user.last_name,
                "email": session.user.email, "type": session.user.type,
            },
            "project_id": str(session.project_id) if session.project_id else None,
            "otp_verified": verify_otp(session.user, otp_code),
            "permissions": list(session.permissions),
        }
```

Die Hilfsfunktionen gehören zur Anwendung, nicht zu `gcl_iam`.

## Sicherheitsanforderungen

- Den Schlüssel anhand der ungeprüften Audience wählen, anderen Claims nicht vertrauen.
- Unbekannte Audiences früh ablehnen.
- Für reine Dienste `RS256VerifyOnly` zurückgeben.
- Aktive Session/Token bei Introspection prüfen und aktuelle Scopes liefern.
- Fail closed: fehlende Daten dürfen keinen Administrator erzeugen.
- Tokens, private/symmetrische Schlüssel und OTPs nie protokollieren.

## Schlüsselrotation

```python
algorithm = algorithms.HS256(key=current_secret, previous_key=previous_secret)
```

oder:

```python
algorithm = algorithms.RS256VerifyOnly(
    public_key=current_public_key,
    previous_public_key=previous_public_key,
)
```

Encoding nutzt den aktuellen Schlüssel; Decoding probiert aktuellen und
vorherigen. Letzteren erst nach Ablauf aller damit signierten Tokens entfernen.

## Anonymer Zugriff

Ohne Bearer-Token nutzt die Middleware ihren `AnonDriver`; der eigene Treiber
wird nicht aufgerufen. Der anonyme Kontext hat keine Berechtigungen und kein
Projekt. Abweichendes Verhalten muss explizit und mit geprüftem Trust-Modell
auf Route-/Controller- oder Middleware-Ebene implementiert werden.
