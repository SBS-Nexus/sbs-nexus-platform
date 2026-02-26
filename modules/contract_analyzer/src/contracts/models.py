from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from shared.document_model import (
    UnifiedDocumentMetadata,
    DocumentType,
    DataClassification,
)
from shared.tenant.context import TenantContext


@dataclass
class ContractMetadata(UnifiedDocumentMetadata):
    """
    Vertragsdokument-Metadaten.
    Enthält u.a. Zahlungsziel in Tagen und Gegenpartei (Lieferant/Kunde).
    """

    counterparty_name: Optional[str] = None
    payment_terms_days: Optional[int] = None  # z.B. 30 oder 60

    @staticmethod
    def create(
        document_id: str,
        file_name: str,
        mime_type: str,
        counterparty_name: str,
        payment_terms_days: int,
        uploaded_by: str | None = None,
    ) -> "ContractMetadata":
        base = UnifiedDocumentMetadata.create(
            document_id=document_id,
            tenant_id=TenantContext.get_current_tenant(),
            document_type=DocumentType.CONTRACT,
            file_name=file_name,
            mime_type=mime_type,
            uploaded_by=uploaded_by or "system",
            source_system="sbs-contract-analyzer",
            classification=DataClassification.CONFIDENTIAL,
        )
        obj = ContractMetadata.__new__(ContractMetadata)
        obj.__dict__.update(base.__dict__)
        obj.counterparty_name = counterparty_name
        obj.payment_terms_days = payment_terms_days
        return obj
