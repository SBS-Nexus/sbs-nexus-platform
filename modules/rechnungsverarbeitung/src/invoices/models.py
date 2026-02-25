from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from shared.document_model import (
    UnifiedDocumentMetadata,
    DocumentType,
    DocumentStatus,
    DataClassification,
)
from shared.tenant.context import TenantContext


class InvoiceDocumentMetadata(UnifiedDocumentMetadata):
    """
    Rechnungs-spezifische Erweiterung von UnifiedDocumentMetadata.
    Fügt invoice-spezifische Felder hinzu ohne Basis-Logik zu duplizieren.
    """

    @staticmethod
    def for_new_upload(
        document_id: str,
        file_name: str,
        mime_type: str,
        uploaded_by: Optional[str] = None,
    ) -> "InvoiceDocumentMetadata":
        base = UnifiedDocumentMetadata.create(
            document_id=document_id,
            tenant_id=TenantContext.get_current_tenant(),
            document_type=DocumentType.INVOICE,
            file_name=file_name,
            mime_type=mime_type,
            uploaded_by=uploaded_by or "system",
            source_system="ki-rechnungsverarbeitung",
            classification=DataClassification.CONFIDENTIAL,
        )
        obj = InvoiceDocumentMetadata.__new__(InvoiceDocumentMetadata)
        obj.__dict__.update(base.__dict__)
        return obj
