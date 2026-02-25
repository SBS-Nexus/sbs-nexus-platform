from __future__ import annotations
from typing import Optional
from shared.document_model import (
    UnifiedDocumentMetadata,
    DocumentType,
    DataClassification,
)
from shared.tenant.context import TenantContext


class HydraulikDocument(UnifiedDocumentMetadata):
    """
    Hydraulik-Servicedokument: Wartungsprotokoll, Prüfbericht, Schaltplan.
    Erbt DSGVO-Retention (10 Jahre) und Soft-Delete von UnifiedDocumentMetadata.
    """

    @staticmethod
    def for_new_upload(
        document_id: str,
        file_name: str,
        mime_type: str,
        uploaded_by: Optional[str] = None,
    ) -> "HydraulikDocument":
        base = UnifiedDocumentMetadata.create(
            document_id=document_id,
            tenant_id=TenantContext.get_current_tenant(),
            document_type=DocumentType.HYDRAULIK_DOC,
            file_name=file_name,
            mime_type=mime_type,
            uploaded_by=uploaded_by or "system",
            source_system="sbs-hydraulikdoc",
            classification=DataClassification.INTERNAL,
        )
        obj = HydraulikDocument.__new__(HydraulikDocument)
        obj.__dict__.update(base.__dict__)
        return obj
