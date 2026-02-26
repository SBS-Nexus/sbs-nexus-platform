from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
import uuid

from shared.db.session import Base  # an deine Base anpassen
from shared.tenant.context import TenantContext


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(String, index=True, nullable=False)
    alert_type = Column(String, index=True, nullable=False)
    severity = Column(String, nullable=False)
    message = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    source_module = Column(String, nullable=True)
    counterparty_name = Column(String, nullable=True)
    invoice_document_id = Column(String, nullable=True)
    contract_document_id = Column(String, nullable=True)


@dataclass
class PaymentTermsAlertData:
    counterparty_name: str
    contract_terms_days: int
    invoice_terms_days: int
    invoice_document_id: str
    contract_document_id: Optional[str] = None


def create_payment_terms_alert(session, data: PaymentTermsAlertData) -> Alert:
    tenant_id = TenantContext.get_current_tenant()
    message = (
        f"Diskrepanz bei Zahlungszielen für {data.counterparty_name}: "
        f"Vertrag {data.contract_terms_days} Tage, Rechnung {data.invoice_terms_days} Tage."
    )

    alert = Alert(
        tenant_id=tenant_id,
        alert_type="payment_terms_mismatch",
        severity="medium",
        message=message,
        created_at=datetime.utcnow(),
        source_module="rechnungsverarbeitung",
        counterparty_name=data.counterparty_name,
        invoice_document_id=data.invoice_document_id,
        contract_document_id=data.contract_document_id,
    )
    session.add(alert)
    session.flush()
    return alert
