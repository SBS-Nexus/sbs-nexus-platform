from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from shared.db.session import Base
from shared.tenant.context import _tenant_id_ctx
from shared.alerts.models import (
    PaymentTermsAlertData,
    create_payment_terms_alert,
    Alert,
)


def test_create_payment_terms_alert_inserts_row():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    _tenant_id_ctx.set("test-tenant-alerts")

    data = PaymentTermsAlertData(
        counterparty_name="Firma XYZ",
        contract_terms_days=30,
        invoice_terms_days=60,
        invoice_document_id="inv-123",
        contract_document_id="ctr-456",
    )
    alert = create_payment_terms_alert(session, data)
    session.commit()

    db_alert = session.query(Alert).filter_by(id=alert.id).first()
    assert db_alert is not None
    assert db_alert.tenant_id == "test-tenant-alerts"
    assert "Diskrepanz" in db_alert.message
