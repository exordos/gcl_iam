# Installation

## Paket installieren

`gcl_iam` benötigt Python 3.10 oder neuer.

```bash
python -m pip install gcl_iam
```

Für die Entwicklung aus einem Checkout dient die tox-Standardumgebung:

```bash
tox -e develop
```

Sie wird in `.tox/develop` angelegt.

## Laufzeitkonfiguration

Ein Dienst mit `HttpDriver` benötigt drei Werte:

| Einstellung | Zweck |
| --- | --- |
| `iam_endpoint` | Clientspezifischer IAM-Endpunkt; darunter werden `actions/jwks` und `actions/introspect` aufgerufen. |
| `audience` | Erwarteter JWT-Claim `aud` des Dienstes. |
| `hs256_jwks_decryption_key` | 32-Byte-A256GCM-Schlüssel zum Entschlüsseln der HS256-Secrets aus JWKS; UTF-8 oder URL-sicheres Base64. |

Anwendungen mit `oslo.config` können die Optionen in der Gruppe `iam` registrieren:

```python
from gcl_iam import opts as iam_opts
from oslo_config import cfg

iam_opts.register_iam_cli_opts(cfg.CONF)
```

Nach dem Einlesen der Konfiguration wird der Treiber erstellt:

```python
from gcl_iam import drivers

iam_driver = drivers.HttpDriver(
    cfg.CONF.iam.iam_endpoint,
    cfg.CONF.iam.audience,
    cfg.CONF.iam.hs256_jwks_decryption_key,
)
```

## Umgang mit Secrets

Der HS256-JWKS-Entschlüsselungsschlüssel und Signaturschlüssel sind geheim:

- aus einem Secret Manager oder geschützter Laufzeitkonfiguration laden;
- nie in ein Repository committen;
- nicht in Logs oder Fehlerberichte aufnehmen;
- bei Rotation aktuellen und vorherigen Schlüssel laut API-Referenz verwenden.

RS256-Konsumenten beziehen öffentliche Schlüssel aus JWKS und benötigen keinen
privaten Schlüssel. Nur Token-Aussteller sollten `RS256` damit erzeugen.

## Installation prüfen

```bash
python -c "from gcl_iam.enforcers import Enforcer; assert Enforcer(['demo.item.read']).enforce_raw('demo.item.read')"
```

Bei erfolgreichem Import und funktionierender Berechtigungsprüfung gibt es keine Ausgabe.
