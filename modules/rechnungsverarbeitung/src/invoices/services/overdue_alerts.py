from datetime import datetime, date

from sqlalchemy.orm import Session

from shared.db.session import get_session_factory
from shared.alerts.services import create_alert
from modules.rechnungsverarbeitung.src.invoices.db_models import Invoice


def emit_overdue_invoice_alerts_for_tenant(tenant_id: str) -> int:
    """
    Erzeugt Alerts für alle Rechnungen eines Tenants, deren Fälligkeitsdatum
    überschritten ist und die nicht abgeschlossen sind (paid/cancelled).

    [TECH-DEBT] Customer-/Kreditor-Infos und SLA-Klassen (z.B. Net 30/45)
    später in die Nachricht und ggf. Severity einfließen lassen.
    """
    SessionLocal = get_session_factory()
    db: Session = SessionLocal()
    created = 0

    try:
        today = date.today()

        invoices = (
            db.query(Invoice)
            .filter(
                Invoice.tenant_id == tenant_id,
                Invoice.due_date.isnot(None),
                Invoice.due_date < datetime.combine(today, datetime.min.time()),
                Invoice.status.notin_(["paid", "cancelled"]),
            )
            .all()
        )

        for inv in invoices:
            due = inv.due_date.date() if isinstance(inv.due_date, datetime) else inv.due_date
            days_overdue = (today - due).days

            message = (
                f"Rechnung {inv.document_id} ist seit {due.isoformat()} überfällig "
                f"({days_overdue} Tage, aktueller Status: {inv.status})."
            )

            create_alert(
                db,
                tenant_id=tenant_id,
                alert_type="invoice_overdue",
                severity="high",  # [TECH-DEBT] später dynamisch nach days_overdue/SLA
                message=message,
                source_module="rechnungsverarbeitung",
                counterparty_name=None,  # [TECH-DEBT] noch kein Feld im Invoice-ORM
                invoice_document_id=str(inv.document_id),
            )
            created += 1

        db.commit()
        return created
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
