from types import SimpleNamespace

from modules.rechnungsverarbeitung.src.invoices.services.payment_terms import checker as checker_module
from modules.rechnungsverarbeitung.src.invoices.services.payment_terms.checker import (
    PaymentTermsChecker,
)


class _ContractModel:
    tenant_id = "tenant_id"
    counterparty_name = "counterparty_name"

    class uploaded_at:
        @staticmethod
        def desc():
            return "uploaded_at_desc"


class _FakeQuery:
    def __init__(self, result):
        self.result = result

    def filter(self, *args, **kwargs):
        return self

    def order_by(self, *args, **kwargs):
        return self

    def first(self):
        return self.result


class _FakeSession:
    def __init__(self, contract):
        self._contract = contract

    def query(self, _model):
        return _FakeQuery(self._contract)


def test_payment_terms_mismatch_creates_alert(monkeypatch):
    contract = SimpleNamespace(
        payment_terms_days=30,
        document_id="ctr-xyz",
    )
    session = _FakeSession(contract)
    invoice = SimpleNamespace(document_id="inv-xyz", tenant_id="tenant-a")

    checker = PaymentTermsChecker()

    monkeypatch.setattr(checker_module, "Contract", _ContractModel)

    captured = {}

    def _fake_create_payment_terms_alert(_session, data):
        captured["data"] = data
        return "alert-created"

    monkeypatch.setattr(checker_module, "create_payment_terms_alert", _fake_create_payment_terms_alert)

    result = checker.check_and_alert(
        session=session,
        invoice=invoice,
        counterparty_name="Firma XYZ",
        invoice_terms_days=60,
    )

    assert result == "alert-created"
    assert captured["data"].counterparty_name == "Firma XYZ"
    assert captured["data"].contract_terms_days == 30
    assert captured["data"].invoice_terms_days == 60
    assert captured["data"].invoice_document_id == "inv-xyz"
    assert captured["data"].contract_document_id == "ctr-xyz"


def test_payment_terms_match_creates_no_alert(monkeypatch):
    contract = SimpleNamespace(payment_terms_days=30, document_id="ctr-xyz")
    session = _FakeSession(contract)
    invoice = SimpleNamespace(document_id="inv-xyz", tenant_id="tenant-a")

    checker = PaymentTermsChecker()

    monkeypatch.setattr(checker_module, "Contract", _ContractModel)

    def _unexpected(*_args, **_kwargs):
        raise AssertionError("create_payment_terms_alert should not be called")

    monkeypatch.setattr(checker_module, "create_payment_terms_alert", _unexpected)

    result = checker.check_and_alert(
        session=session,
        invoice=invoice,
        counterparty_name="Firma XYZ",
        invoice_terms_days=30,
    )

    assert result is None
