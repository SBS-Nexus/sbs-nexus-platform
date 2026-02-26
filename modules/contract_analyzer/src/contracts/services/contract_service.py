from __future__ import annotations
import uuid
from typing import Optional

from sqlalchemy.orm import Session

from shared.document_model import DocumentStatus
from shared.tenant.context import TenantContext
from modules.contract_analyzer.src.contracts.models import ContractMetadata
from modules.contract_analyzer.src.contracts.db_models import Contract


class ContractService:
    """
    Service zum Registrieren von Vertragsdokumenten im System.
    """

    def register_contract(
        self,
        session: Session,
        file_name: str,
        mime_type: str,
        counterparty_name: str,
        payment_terms_days: int,
        uploaded_by: Optional[str] = None,
    ) -> Contract:
        document_id = str(uuid.uuid4())
        meta = ContractMetadata.create(
            document_id=document_id,
            file_name=file_name,
            mime_type=mime_type,
            counterparty_name=counterparty_name,
            payment_terms_days=payment_terms_days,
            uploaded_by=uploaded_by,
        )
        contract = Contract(
            document_id=meta.id,
            tenant_id=meta.tenant_id,
            document_type=meta.document_type.value if hasattr(meta.document_type, "value") else str(meta.document_type),
            status=DocumentStatus.PROCESSED.value if hasattr(DocumentStatus, "value") else "processed",
            file_name=meta.file_name,
            mime_type=meta.mime_type,
            uploaded_by=meta.uploaded_by,
            uploaded_at=meta.uploaded_at,
            source_system=meta.source_system,
            retention_until=meta.retention_until,
            counterparty_name=meta.counterparty_name,
            payment_terms_days=meta.payment_terms_days,
        )
        session.add(contract)
        session.flush()
        return contract
