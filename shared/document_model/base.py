from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from typing import Optional

from shared.document_model.enums import DocumentType, DocumentStatus, DataClassification


# DSGVO: Standard-Aufbewahrungsfrist 10 Jahre (§ 147 AO)
_DEFAULT_RETENTION_YEARS = 10


@dataclass
class UnifiedDocumentMetadata:
    """
    Basis-Metadaten für alle SBS NEXUS Dokument-Typen.
    Verwendet von: Rechnungsverarbeitung, HydraulikDoc, AuftragsKI.
    DSGVO-konform: retention_until, classification, deleted_at.
    """
    id: str
    tenant_id: str
    document_type: DocumentType
    status: DocumentStatus = DocumentStatus.UPLOADED

    # Datei-Metadaten
    file_name: Optional[str] = None
    mime_type: Optional[str] = None
    file_size_bytes: Optional[int] = None

    # Lifecycle
    uploaded_by: str = "system"
    uploaded_at: Optional[datetime] = None
    processed_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None  # Soft-Delete für DSGVO

    # Herkunft
    source_system: str = "sbs-nexus-platform"
    external_reference: Optional[str] = None  # z.B. DATEV-Belegnummer

    # DSGVO
    classification: DataClassification = DataClassification.INTERNAL
    retention_until: Optional[datetime] = None

    @staticmethod
    def create(
        document_id: str,
        tenant_id: str,
        document_type: DocumentType,
        file_name: str,
        mime_type: str,
        uploaded_by: str = "system",
        source_system: str = "sbs-nexus-platform",
        classification: DataClassification = DataClassification.INTERNAL,
        retention_years: int = _DEFAULT_RETENTION_YEARS,
    ) -> "UnifiedDocumentMetadata":
        now = datetime.now(timezone.utc)
        return UnifiedDocumentMetadata(
            id=document_id,
            tenant_id=tenant_id,
            document_type=document_type,
            file_name=file_name,
            mime_type=mime_type,
            uploaded_by=uploaded_by,
            uploaded_at=now,
            source_system=source_system,
            classification=classification,
            retention_until=now + timedelta(days=365 * retention_years),
        )

    def is_retention_expired(self) -> bool:
        if self.retention_until is None:
            return False
        return datetime.now(timezone.utc) > self.retention_until

    def soft_delete(self) -> None:
        """DSGVO-konformes Löschen: Status + Zeitstempel, kein Hard-Delete."""
        self.status = DocumentStatus.DELETED
        self.deleted_at = datetime.now(timezone.utc)
