from __future__ import annotations
from typing import Optional
from shared.document_model import (
    UnifiedDocumentMetadata,
    DocumentType,
    DataClassification,
)
from shared.tenant.context import TenantContext


class AuftragsDocument(UnifiedDocumentMetadata):
    """
    Auftragsdokument: Serviceauftrag, Wartungsauftrag, Reparaturauftrag.
    Erbt DSGVO-Retention und Soft-Delete von UnifiedDocumentMetadata.
    """

    @staticmethod
    def for_new_upload(
        document_id: str,
        file_name: str,
        mime_type: str,
        uploaded_by: Optional[str] = None,
    ) -> "AuftragsDocument":
        base = UnifiedDocumentMetadata.create(
            document_id=document_id,
            tenant_id=TenantContext.get_current_tenant(),
            document_type=DocumentType.AUFTRAG,
            file_name=file_name,
            mime_type=mime_type,
            uploaded_by=uploaded_by or "system",
            source_system="sbs-auftragsai",
            classification=DataClassification.CONFIDENTIAL,
        )
        obj = AuftragsDocument.__new__(AuftragsDocument)
        obj.__dict__.update(base.__dict__)
        return obj
