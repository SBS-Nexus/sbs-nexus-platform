from datetime import date, datetime, timedelta
from types import SimpleNamespace

from modules.rechnungsverarbeitung.src.invoices.services import overdue_alerts


class _FakeQuery:
    def __init__(self, invoices):
        self._invoices = invoices

    def filter(self, *_args, **_kwargs):
        return self

    def all(self):
        return self._invoices


class _FakeSession:
    def __init__(self, invoices):
        self._invoices = invoices
        self.committed = False
        self.rolled_back = False
        self.closed = False

    def query(self, _model):
        return _FakeQuery(self._invoices)

    def commit(self):
        self.committed = True

    def rollback(self):
        self.rolled_back = True

    def close(self):
        self.closed = True



def test_emit_overdue_invoice_alerts_creates_alerts_for_all_matching_invoices(monkeypatch):
    today = date.today()
    invoices = [
        SimpleNamespace(document_id="inv-001", due_date=today - timedelta(days=3), status="processed"),
        SimpleNamespace(document_id="inv-002", due_date=datetime.combine(today - timedelta(days=1), datetime.min.time()), status="uploaded"),
    ]
    session = _FakeSession(invoices)

    monkeypatch.setattr(overdue_alerts, "get_session_factory", lambda: lambda: session)

    created_payloads = []

    def _fake_create_alert(_db, **kwargs):
        created_payloads.append(kwargs)

    monkeypatch.setattr(overdue_alerts, "create_alert", _fake_create_alert)

    created = overdue_alerts.emit_overdue_invoice_alerts_for_tenant("tenant-a")

    assert created == 2
    assert session.committed is True
    assert session.closed is True
    assert len(created_payloads) == 2
    assert all(p["alert_type"] == "invoice_overdue" for p in created_payloads)
    assert created_payloads[0]["tenant_id"] == "tenant-a"
    assert "inv-001" in created_payloads[0]["message"]


def test_emit_overdue_invoice_alerts_rolls_back_on_error(monkeypatch):
    session = _FakeSession([
        SimpleNamespace(document_id="inv-001", due_date=date.today() - timedelta(days=2), status="processed")
    ])
    monkeypatch.setattr(overdue_alerts, "get_session_factory", lambda: lambda: session)

    def _failing_create_alert(*_args, **_kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(overdue_alerts, "create_alert", _failing_create_alert)

    try:
        overdue_alerts.emit_overdue_invoice_alerts_for_tenant("tenant-a")
        raise AssertionError("Expected RuntimeError")
    except RuntimeError as exc:
        assert "boom" in str(exc)

    assert session.rolled_back is True
    assert session.closed is True
