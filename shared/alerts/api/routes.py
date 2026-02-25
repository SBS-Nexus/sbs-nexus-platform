from __future__ import annotations
from typing import Optional, List

from fastapi import APIRouter, Header, HTTPException
from sqlalchemy.orm import Session

from shared.alerts.models import Alert, AlertType, AlertSeverity
from shared.db.session import get_session
from shared.tenant.context import TenantContext

router = APIRouter(prefix="/alerts", tags=["alerts"])


def _set_tenant(x_tenant_id: Optional[str]) -> None:
    if not x_tenant_id:
        raise HTTPException(status_code=400, detail="X-Tenant-ID header is required")
    TenantContext.set_current_tenant(x_tenant_id)


@router.get("/", response_model=list[dict])
def list_alerts(
    x_tenant_id: Optional[str] = Header(default=None, alias="X-Tenant-ID"),
    alert_type: Optional[str] = None,
    severity: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
):
    _set_tenant(x_tenant_id)
    tenant_id = TenantContext.get_current_tenant()

    with get_session() as session:
        query = (
            session.query(Alert)
            .filter(Alert.tenant_id == tenant_id)
            .order_by(Alert.created_at.desc())
        )

        if alert_type:
            query = query.filter(Alert.alert_type == alert_type)
        if severity:
            query = query.filter(Alert.severity == severity)

        alerts = query.limit(limit).offset(offset).all()

        return [
            {
                "id": a.id,
                "tenant_id": a.tenant_id,
                "alert_type": a.alert_type,
                "severity": a.severity,
                "message": a.message,
                "counterparty_name": a.counterparty_name,
                "invoice_document_id": a.invoice_document_id,
                "contract_document_id": a.contract_document_id,
                "created_at": a.created_at.isoformat() if a.created_at else None,
            }
            for a in alerts
        ]
