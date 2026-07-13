# gcl_iam

`gcl_iam` ergänzt Python-RESTAlchemy-Dienste um Authentifizierung und
Autorisierung. Die Bibliothek prüft JWTs, bezieht Identitäts- und
Berechtigungsdaten über einen IAM-Treiber, speichert sie im Request-Kontext und
setzt sie in Controllern und bei der Feldserialisierung durch.

## Funktionen

- Prüfung von HS256- und RS256-JWTs.
- Vorheriger Schlüssel als Fallback während einer Rotation.
- JWKS und Introspection von einem entfernten IAM-Endpunkt.
- Eigene prozessinterne IAM-Treiber.
- Berechtigungen im Format `service.resource.action` mit `*` auf jeder Ebene.
- Einschränkung projektbezogener Ressourcen anhand der `project_id`.
- Schutz globaler und verschachtelter Ressourcen.
- Verifizierte OTPs für ausgewählte Operationen.
- IAM-gesteuerte Sichtbarkeit von RESTAlchemy-Feldern.
- Token-, Benutzer-, Projekt- und Berechtigungsdaten im aktuellen Kontext.
- Einheitliche HTTP-Antworten für IAM-Ausnahmen.

`gcl_iam` stellt keine Zugangsdaten aus, definiert keine Anwendungsrollen und
enthält keine IAM-Datenbank. Dafür ist der IAM-Dienst oder ein eigener Treiber
zuständig.

## Dokumentationsübersicht

1. [Installation](installation.md)
2. [Erste Schritte](getting-started.md)
3. Konzepte:
   - [Authentifizierung und Request-Kontext](concepts/authentication-and-context.md)
   - [Berechtigungen, Projekte und OTP](concepts/authorization.md)
4. Anleitungen:
   - [RESTAlchemy-Dienst integrieren](how-to/restalchemy-service.md)
   - [Eigenen Treiber implementieren](how-to/custom-driver.md)
5. [Referenz der öffentlichen API](reference/api.md)

## Sprachen

Die Dokumentation besitzt in allen vier Sprachen dieselbe Struktur:

- [English](../en/index.md)
- [Русский](../ru/index.md)
- [Deutsch](../de/index.md)
- [中文](../zh/index.md)

## Unterstützte Umgebung

- Python 3.10 oder neuer
- RESTAlchemy 15.x
- PyJWT 2.x
- HS256- oder RS256-JWT-Signaturen

Die aktuellen Abhängigkeitsbereiche in `pyproject.toml` sind maßgeblich.
