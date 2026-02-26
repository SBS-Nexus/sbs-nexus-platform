from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from shared.db.session import Base
from shared.tenant.context import _tenant_id_ctx
from modules.contract_analyzer.src.contracts.db_models import Contract
from modules.rechnungsverarbeitung.src.invoices.db_models import Invoice
from modules.rechnungsverarbeitung.src.invoices.services.payment_terms.checker import (
    PaymentTermsChecker,
)
from shared.alerts.models import Alert


def test_payment_terms_mismatch_creates_alert():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    _tenant_id_ctx.set("mueller-hydraulik")

    # Vertrag mit 30 Tagen Zahlungsziel
    contract = Contract(
        document_id="ctr-xyz",
        tenant_id="mueller-hydraulik",
        counterparty_name="Firma XYZ",
        payment_terms_days=30,
    )
    session.add(contract)

    # Rechnung mit 60 Tagen Zahlungsziel
    invoice = Invoice(
        document_id="inv-xyz",
        tenant_id="mueller-hydraulik",
        document_type="invoice",
        file_name="rechnung_xyz.pdf",
        mime_type="application/pdf",
        uploaded_by="buchhaltung",
        uploaded_at=datetime.now(timezone.utc),
        status="processed",
        source_system="ki-rechnungsverarbeitung",
    )
    session.add(invoice)
    session.flush()

    checker = PaymentTermsChecker()
    alert = checker.check_and_alert(
        session=session,
        invoice=invoice,
        counterparty_name="Firma XYZ",
        invoice_terms_days=60,
    )
    session.commit()

    db_alert = session.query(Alert).first()
    assert alert is not None
    assert db_alert is not None
    assert db_alert.tenant_id == "mueller-hydraulik"
    assert "30" in db_alert.message
    assert "60" in db_alert.message
    assert db_alert.counterparty_name == "Firma XYZ"
