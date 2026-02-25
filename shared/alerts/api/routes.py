from __future__ import annotations

from typing import Annotated, Optional, List

from fastapi import APIRouter, Depends, Header, Query
from sqlalchemy.orm import Session

from shared.db.session import get_session
from shared.alerts.models import Alert


router = APIRouter(tags=["alerts"])

TenantHeader = Annotated[str, Header(alias="X-Tenant-ID")]


@router.get(
    "/alerts/",
    summary="List alerts for tenant",
)
def list_alerts(
    tenant_id: TenantHeader,
    alert_type: Optional[str] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_session),
):
    """
    Liefert Alerts für einen Tenant, optional gefiltert nach Alert-Typ.

    - Multi-Tenant: Filterung über X-Tenant-ID Header.
    - Pagination: limit/offset.
    """
    query = db.query(Alert).filter(Alert.tenant_id == tenant_id)

    if alert_type:
        query = query.filter(Alert.alert_type == alert_type)

    alerts: List[Alert] = (
        query.order_by(Alert.created_at.desc())
        .limit(limit)
        .offset(offset)
        .all()
    )

    return {
        "tenant_id": tenant_id,
        "alert_type": alert_type,
        "limit": limit,
        "offset": offset,
        "alerts": [
            {
                "id": str(a.id),
                "tenant_id": a.tenant_id,
                "alert_type": a.alert_type,
                "severity": a.severity,
                "message": a.message,
                "created_at": a.created_at.isoformat(),
                "source_module": a.source_module,
                "counterparty_name": a.counterparty_name,
                "invoice_document_id": a.invoice_document_id,
                "contract_document_id": a.contract_document_id,
            }
            for a in alerts
        ],
    }
