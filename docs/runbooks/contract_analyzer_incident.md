# Contract Analyzer Incident Runbook

## Zweck

Dieses Runbook beschreibt die Schritte zur Fehleranalyse und Behebung von Störungen im Contract Analyzer (Analyse-Endpunkte und Ergebnisse).

## Typische Symptome

- API-Aufrufe auf `/api/v1/contracts/...` liefern 5xx-Fehler.
- Deutlich erhöhte Latenzen bei Vertragsanalysen.
- Kunden melden fehlende oder offensichtlich falsche Analyseergebnisse.

## Sofortmaßnahmen (First Response)

1. Incident/Ticket anlegen mit:
   - Tenant-ID,
   - Zeitpunkt (UTC),
   - betroffenen API-Routen,
   - sofern vorhanden: X-Correlation-ID aus der Anfrage/Response.
2. Logs nach `module=contract_analyzer` und der betroffenen Correlation-ID bzw. analysis_id durchsuchen.
3. Health-Status abhängiger Systeme prüfen (Datenbank, Modell-/Embedding-Backend, externe APIs).

## Diagnoseschritte

1. Logs nach `event=analysis_failed` filtern und Fehlermuster identifizieren.
2. Prüfen, ob ein einzelner Tenant oder mehrere Tenants betroffen sind.
3. Datenbankzustand prüfen:
   - Analysen-/Ergebnistabellen (z.B. fehlerhafte oder unvollständige Einträge),
   - Warteschlangen/Jobs (falls asynchron verarbeitet wird).
4. Bei Performanceproblemen: gleichzeitige Requests und Ressourcenauslastung (CPU, RAM, DB) prüfen.

## Eskalation

- Eskalation an die zuständige technische Rolle (z.B. Backend/ML-Engineering), wenn:
  - mehr als ein Tenant betroffen ist,
  - die Störung länger als 15 Minuten anhält,
  - Datenintegrität betroffen sein könnte (z.B. widersprüchliche Ergebnisse).
- Bei sicherheitsrelevanten Auffälligkeiten (z.B. Datenlecks, Cross-Tenant-Zugriff) sofort an Security/Compliance eskalieren.

## Nachbereitung

1. Incident-Report mit Ursache, Auswirkungen und Zeitverlauf dokumentieren.
2. Korrekturmaßnahmen ableiten:
   - zusätzliche Tests (Unit/E2E),
   - verbesserte Logging-/Monitoring-Signale,
   - Anpassungen an Ressourcenlimits oder Timeouts.
3. Runbook bei Bedarf aktualisieren (neue Symptome, Diagnoseschritte, Eskalationspfade).
