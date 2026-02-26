from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from shared.alerts.models import Alert


def create_alert(
    db: Session,
    *,
    tenant_id: str,
    alert_type: str,
    severity: str,
    message: str,
    source_module: str,
    counterparty_name: Optional[str] = None,
    invoice_document_id: Optional[str] = None,
    contract_document_id: Optional[str] = None,
) -> Alert:
    alert = Alert(
        tenant_id=tenant_id,
        alert_type=alert_type,
        severity=severity,
        message=message,
        created_at=datetime.utcnow(),
        source_module=source_module,
        counterparty_name=counterparty_name,
        invoice_document_id=invoice_document_id,
        contract_document_id=contract_document_id,
    )
    db.add(alert)
    # Commit übernimmt get_session-Dependency; hier nur add/flush nötig
    db.flush()
    return alert
