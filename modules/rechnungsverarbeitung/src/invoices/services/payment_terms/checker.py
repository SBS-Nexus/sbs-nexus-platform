from __future__ import annotations
from typing import Optional

from sqlalchemy.orm import Session

from shared.alerts.models import (
    PaymentTermsAlertData,
    create_payment_terms_alert,
)
from modules.contract_analyzer.src.contracts.db_models import Contract
from modules.rechnungsverarbeitung.src.invoices.db_models import Invoice


class PaymentTermsChecker:
    """
    Vergleicht Zahlungsziele zwischen Rechnungen und Verträgen pro Gegenpartei.
    """

    def check_and_alert(
        self,
        session: Session,
        invoice: Invoice,
        counterparty_name: str,
        invoice_terms_days: int,
    ):
        contract: Optional[Contract] = (
            session.query(Contract)
            .filter(
                Contract.tenant_id == invoice.tenant_id,
                Contract.counterparty_name == counterparty_name,
            )
            .order_by(Contract.uploaded_at.desc())
            .first()
        )
        if not contract or contract.payment_terms_days is None:
            return None

        if contract.payment_terms_days != invoice_terms_days:
            data = PaymentTermsAlertData(
                counterparty_name=counterparty_name,
                contract_terms_days=contract.payment_terms_days,
                invoice_terms_days=invoice_terms_days,
                invoice_document_id=invoice.document_id,
                contract_document_id=contract.document_id,
            )
            return create_payment_terms_alert(session, data)

        return None
