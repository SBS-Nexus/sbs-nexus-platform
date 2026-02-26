# Contract Analyzer – Datenschutz- und AI-Act-Notiz

## Zweck des Moduls
Der Contract Analyzer bewertet Vertragsklauseln regelbasiert auf Risikoindikatoren (z. B. automatische Verlängerung, unbeschränkte Haftung, kurze Kündigungsfrist) zur operativen Priorisierung für Fachanwender.

## Verarbeitete Datenarten
- `contract_id` (fachliche Referenz)
- optional `counterparty_name`
- Vertragsinhalt als **transiente Eingabe** für die Laufzeitanalyse
- Analyseergebnisse: Risk Score, Risk Tags, Clause Hits (Typ + knapper Evidence-Ausschnitt)
- SHA-256 Fingerprint des Eingabetextes zur Nachvollziehbarkeit ohne Volltextspeicherung

## Datensparsamkeit (DSGVO)
- Der vollständige Vertragstext wird nicht in der Datenbank persistiert.
- Persistiert werden nur Ergebnisdaten und ein Fingerprint.
- Logging/Alerts enthalten nur Metadaten (Tenant, contract_id, Risk Score), keine Volltexte.

## Logging und Alerts
- Bei hohem Risiko (`risk_score >= 60`) wird ein Alert über `shared.alerts.create_alert` erzeugt.
- Alert-Text enthält ausschließlich technische Referenzen und Risiko-Score.
- Damit bleibt die Nachvollziehbarkeit erhalten, ohne unnötige Inhaltsdaten zu speichern.

## Hinweis zum EU AI Act
- Aktueller Ansatz ist deterministisch/regelbasiert und dient als Entscheidungshilfe.
- Die finale juristische Bewertung verbleibt beim Menschen (Human-in-the-loop).
