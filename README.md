# SBS Nexus Platform – Document-Intelligent AI for Industrial SMEs

Dokumenten-intelligente KI-Plattform für Industrie-KMU – als Enterprise SaaS, mandantenfähig (Multi-Tenant) und von Grund auf DSGVO-orientiert konzipiert.

Die Plattform bündelt mehrere spezialisierte KI-Module (z. B. Rechnungsverarbeitung, HydraulikDoc, AuftragsKI) auf einem gemeinsamen Enterprise-Core für Mandantenkontext, Datenbankzugriff, Governance und Observability.

---

## Architekturprinzipien

Die SBS Nexus Platform folgt Architekturprinzipien, wie sie in Enterprise-Stacks von Unternehmen wie Apple, NVIDIA oder SAP etabliert sind – übersetzt auf den Bedarf des produzierenden Mittelstands.

- **Multi-Tenant by Design**  
  Strikte Mandantentrennung auf allen Ebenen: HTTP-Layer, Domain-Layer, Datenbank. Jeder Datensatz trägt eine klare `tenant_id`, Tenant-Context wird zentral verwaltet.

- **Document-Intelligent Core**  
  Dokumente (Rechnungen, Serviceprotokolle, Auftragsdaten, Hydraulik-Dokumentation) werden als einheitliche, modulübergreifende Dokument-Metadaten-Objekte modelliert. Inhalte bleiben außerhalb des Plattform-Kerns – die Plattform orchestriert, extrahiert, klassifiziert und verteilt.

- **DSGVO-orientierte Verarbeitung**  
  Architektur, Logging und Datenhaltung sind von Beginn an auf Datenschutz und Auditierbarkeit ausgelegt: Minimierung von personenbezogenen Daten, saubere Trennung von IDs vs. Inhalten, klare Event- und Zugriffspfade.

- **Shared Enterprise Core**  
  Cross-Modul-Funktionalität (TenantContext, DB-Session, Logging-Patterns, Security-Standards) liegt in einem dedizierten `shared/`-Layer und wird von allen Modulen wiederverwendet. So entstehen konsistente Implementierungen statt „Per-Modul-Copy-Paste“.

- **API-first & Module-isoliert**  
  Jedes Modul stellt klar definierte, mandantenfähige APIs bereit. Module können unabhängig deployt werden, teilen sich aber dieselben Enterprise-Patterns.

---

## Repository-Struktur (Monorepo)

Die Plattform wird als Monorepo geführt, um Cross-Modul-Patterns, gemeinsame Governance und konsistentes Deployment zu gewährleisten [web:118][web:125].

```text
sbs-nexus-platform/
├── modules/
│   └── rechnungsverarbeitung/        # KI-Rechnungsverarbeitung (Modul 1)
│       ├── src/
│       │   ├── api/                  # FastAPI Endpoints (REST-API)
│       │   ├── invoices/             # Domain-Modelle & Services
│       │   └── app/                  # (zukünftig UI/Next.js-Integration)
│       ├── scripts/                  # z. B. create_tables, DB-Migrationen
│       └── tests/                    # Pytest-Suite für dieses Modul
│
├── shared/
│   ├── tenant/
│   │   └── context.py                # TenantContext, Header-Resolution, Scoping
│   └── db/
│       └── session.py                # DB-Engine, Session-Factory, Base-ORM
│
├── scripts/                          # Plattformweite Hilfsskripte
├── _archive/                         # Historische Artefakte / Legacy-Webapp
├── email_templates/                  # Enterprise-E-Mail-Templates (Branding)
├── pptx_templates/                   # Präsentations-/Report-Templates
└── README.md


Modul 1: KI-Rechnungsverarbeitung (Invoice API)
Die KI-Rechnungsverarbeitung ist das erste Modul, das auf dem neuen Enterprise-Core aufsetzt. Ziel: Mandantenfähige, KI-gestützte Eingangsrechnungsverarbeitung für Industrie-KMU, mit klarer Trennung von Metadaten, Inhalten und Event-Historie [web:76][web:93].

Funktionsumfang – Slice 1 (API-Kern)
Mandantenfähiger Upload-Endpunkt
Upload von Eingangsrechnungen (z. B. PDF) pro Mandant inkl. User-Kontext, Verarbeitung als Dokument-Metadatenobjekt.

Persistente Metadatenhaltung in PostgreSQL
Speicherung von Rechnungen als Invoice-Entitäten mit tenant_id, Status, Dateinamen, Timestamps und Source-System.

Streng tenant-gefiltertes Lesen
Zugriff auf einzelne Rechnungen oder Listen ausschließlich im Kontext des gesetzten Tenants (X-Tenant-ID).

DSGVO-nahe Architektur
Plattform-Core arbeitet mit IDs und Metadaten – Inhalte können je nach Use Case in nachgelagerte, spezialisierte Komponenten ausgelagert werden.

API – Technische Spezifikation (Slice 1)
Authentifizierungs- und Mandantenkontext
Der Mandant wird über einen expliziten Header gesetzt und im TenantContext hinterlegt:

Header: X-Tenant-ID (obligatorisch)

Header: X-User-ID (optional, für Audit-Funktionen)

TenantContext wird im shared/tenant/context.py verwaltet und von allen API-Endpunkten verwendet.

Endpunkte
1. Upload einer Rechnung
text
POST /invoices/upload
Headers

X-Tenant-ID: Mandantenkennung (z. B. demo-tenant)

X-User-ID: User-ID oder Systemkennung (z. B. demo-user)

Body (multipart/form-data)

file: Rechnungsdokument (z. B. PDF)

Response (JSON)

json
{
  "document_id": "f271bb98-24ab-46a5-80df-148a5d21c5dc",
  "tenant_id": "demo-tenant",
  "status": "uploaded",
  "file_name": "invoice-3659444-2025-02-01.pdf",
  "document_type": "invoice"
}
2. Einzelabruf einer Rechnung
text
GET /invoices/{document_id}
Headers

X-Tenant-ID: Mandantenkennung

Response (JSON, Beispiel)

json
{
  "document_id": "f271bb98-24ab-46a5-80df-148a5d21c5dc",
  "tenant_id": "demo-tenant",
  "status": "uploaded",
  "file_name": "invoice-3659444-2025-02-01.pdf",
  "document_type": "invoice",
  "uploaded_by": "demo-user",
  "uploaded_at": "2026-02-19T23:39:26.528974",
  "processed_at": null,
  "source_system": "ki-rechnungsverarbeitung"
}
Nur Rechnungen, bei denen tenant_id == X-Tenant-ID, werden zurückgegeben. Andernfalls erfolgt eine 404 Invoice not found.

3. Listing von Rechnungen eines Tenants
text
GET /invoices?limit={limit}&offset={offset}
Headers

X-Tenant-ID: Mandantenkennung

Query-Parameter

limit (optional, Default: 50)

offset (optional, Default: 0)

Response (JSON, Beispiel)

json
{
  "items": [
    {
      "document_id": "f271bb98-24ab-46a5-80df-148a5d21c5dc",
      "tenant_id": "demo-tenant",
      "status": "uploaded",
      "file_name": "invoice-3659444-2025-02-01.pdf",
      "uploaded_at": "2026-02-19T23:39:26.528974"
    },
    {
      "document_id": "1c2dc7a2-4f6e-4aa5-bc74-1fba88f678bc",
      "tenant_id": "demo-tenant",
      "status": "uploaded",
      "file_name": "invoice-3659444-2025-02-01.pdf",
      "uploaded_at": "2026-02-19T22:29:17.655222"
    }
  ],
  "limit": 10,
  "offset": 0
}
Shared Enterprise Core
Der shared/-Bereich definiert plattformweite Standards, die von allen Modulen wiederverwendet werden.

TenantContext (shared/tenant/context.py)
Zentraler Mechanismus zur Verwaltung des aktuellen Tenants pro Request.

API-Endpunkte setzen den Tenant via X-Tenant-ID-Header.

Domain-Services lesen den Tenant ausschließlich über den TenantContext – keine direkten Header-Zugriffe im Domain-Layer.

DB-Session & ORM (shared/db/session.py)
Erstellung der SQLAlchemy-Engine (z. B. PostgreSQL).

Bereitstellung von Session-Factories und Base für ORM-Modelle.

Zentralisierte Stelle für:

Connection-Konfiguration

Pooling

spätere Erweiterungen wie Read/Write-Splitting oder Tenancy-Strategien.

Alle Module (z. B. modules/rechnungsverarbeitung) bauen ihre ORM-Modelle auf dieser Base auf und nutzen get_session() aus dem Shared-DB-Layer.

Roadmap (High-Level)
Die Roadmap ist bewusst modul- und plattformorientiert aufgebaut, mit klaren Enterprise-Slices.

Modul KI-Rechnungsverarbeitung

Event-Log & Status-Maschine (uploaded → extracted → validated → exported)

KI-Extraktion (Multi-Model, u. a. GPT/Claude)

DATEV-/ERP-Exports für unterschiedliche Systeme

Modul HydraulikDoc

Mandantenfähige Verwaltung von Hydraulik-Dokumentation und Service-Historie

Integration mit bestehenden SBS-Systemen (z. B. smartmaintenance, SBSnexus.de)

Modul AuftragsKI

KI-gestützte Unterstützung für Angebots- und Auftragsabwicklung

Verbindung mit bestehenden GTM- und Automatisierungssystemen (z. B. sbs-gtm-automation)

Platform Foundation

Erweiterte Observability (structured logging, Trace-IDs, Request-IDs)

Security-Policies (Rate Limiting, API Keys/OAuth, Rollen-/Rechte-Modell)

Mandantenweites Event-Log und Audit-Trail

Kontakt & Compliance
SBS Deutschland GmbH & Co. KG
In der Dell 19
69469 Weinheim, Deutschland

📧 info@sbsdeutschland.com

🌐 https://www.sbsdeutschland.com

Die Plattform wird in Deutschland / EU gehostet und ist auf langfristige DSGVO-Konformität, Nachvollziehbarkeit von Geschäftsprozessen und Auditierbarkeit von KI-Entscheidungen ausgelegt [web:76][web:87].

© 2026 SBS Deutschland GmbH & Co. KG – Proprietary.
Alle Rechte vorbehalten.
