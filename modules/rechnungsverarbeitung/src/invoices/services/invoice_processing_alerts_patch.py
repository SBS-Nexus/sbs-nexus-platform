from datetime import datetime

from sqlalchemy.orm import Session

from shared.db.session import get_session
from shared.alerts.services import create_alert

# Importiere deine bestehenden Invoice-Modelle/Funktionen:
# from modules.rechnungsverarbeitung.src.invoices.models import Invoice


def check_and_emit_overdue_invoice_alerts(tenant_id: str) -> int:
    """
    Scannt Rechnungen für einen Tenant und erzeugt Alerts für überfällige Rechnungen.
    Gibt die Anzahl neu erzeugter Alerts zurück.
    """
    created = 0
    with get_session() as db:  # synchroner Kontext für Backend-Job
        now = datetime.utcnow()

        # TODO: Hier deine echte Query einfügen:
        # Beispiel: alle offenen Rechnungen mit faelligkeit < heute
        # invoices = (
        #     db.query(Invoice)
        #     .filter(
        #         Invoice.tenant_id == tenant_id,
        #         Invoice.status == "open",
        #         Invoice.due_date < now,
        #     )
        #     .all()
        # )

        invoices = []  # Platzhalter, bis du deine Models verdrahtet hast

        for inv in invoices:
            message = f"Rechnung {inv.invoice_number} überfällig seit {inv.due_date.date().isoformat()}"
            create_alert(
                db,
                tenant_id=tenant_id,
                alert_type="invoice_overdue",
                severity="high",
                message=message,
                source_module="rechnungsverarbeitung",
                counterparty_name=getattr(inv, "customer_name", None),
                invoice_document_id=str(inv.id),
            )
            created += 1

    return created
