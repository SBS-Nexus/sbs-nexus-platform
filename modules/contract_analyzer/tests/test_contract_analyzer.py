from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from modules.contract_analyzer.src.contracts.db_models import ContractAnalysis
from modules.contract_analyzer.src.contracts.schemas import ContractAnalysisRequest
from modules.contract_analyzer.src.contracts.services.analyzer import ContractAnalyzerService
from modules.contract_analyzer.src.contracts.services.contract_analysis import ContractAnalysisService
from modules.contract_analyzer.src.contracts.services.storage import ContractAnalysisRepository


def _make_session():
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    ContractAnalysis.__table__.create(bind=engine)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)()


def test_clause_detection_and_risk_scoring():
    service = ContractAnalyzerService()
    result = service.analyze_contract(
        tenant_id="tenant-a",
        contract_id="C-1",
        contract_text=(
            "Dieser Vertrag enthält eine automatische Verlängerung und eine unbeschränkte Haftung. "
            "Zusätzlich gilt ausschließlicher Gerichtsstand in Zürich."
        ),
    )

    assert result.risk_score == 75
    assert set(result.risk_tags) == {
        "automatic_renewal",
        "unlimited_liability",
        "exclusive_jurisdiction",
    }


def test_fingerprint_is_deterministic():
    text = "A" * 120
    assert ContractAnalyzerService.fingerprint_content(text) == ContractAnalyzerService.fingerprint_content(text)


def test_analyze_and_store_creates_pseudonymised_record(monkeypatch):
    db = _make_session()
    analyzer = ContractAnalysisService()
    monkeypatch.setattr("shared.tenant.context.TenantContext.get_current_tenant", lambda: "tenant-x")
    monkeypatch.setattr(
        "modules.contract_analyzer.src.contracts.services.contract_analysis.create_alert",
        lambda *args, **kwargs: None,
    )
    payload = ContractAnalysisRequest(
        contract_id="CTR-42",
        counterparty_name="Supplier GmbH",
        contract_text="automatic renewal " * 10,
    )

    analyzer.analyze_and_store(db, payload)
    db.commit()

    row = db.query(ContractAnalysis).one()
    assert row.contract_id == "CTR-42"
    assert len(row.content_fingerprint) == 64
    assert "automatic renewal" not in row.clause_hits_json.lower()


def test_high_risk_analysis_emits_alert(monkeypatch):
    db = _make_session()
    analyzer = ContractAnalysisService()
    monkeypatch.setattr("shared.tenant.context.TenantContext.get_current_tenant", lambda: "tenant-y")

    captured = {}

    def _capture_alert(*args, **kwargs):
        captured.update(kwargs)

    monkeypatch.setattr(
        "modules.contract_analyzer.src.contracts.services.contract_analysis.create_alert",
        _capture_alert,
    )

    payload = ContractAnalysisRequest(
        contract_id="CTR-99",
        contract_text=(
            "automatic renewal "
            "unlimited liability "
            "termination notice under 30 days "
        ) * 3,
    )
    analyzer.analyze_and_store(db, payload)

    assert captured["alert_type"] == "contract_high_risk"
    assert captured["tenant_id"] == "tenant-y"


def test_repository_roundtrip():
    db = _make_session()
    analyzer = ContractAnalyzerService()
    repo = ContractAnalysisRepository()
    result = analyzer.analyze_contract(
        tenant_id="tenant-z",
        contract_id="CTR-77",
        contract_text="automatic renewal " * 8,
    )

    repo.save(db, result=result, counterparty_name=None, content_fingerprint="abc")
    db.commit()

    row = repo.find_by_analysis_id(db, analysis_id=result.analysis_id, tenant_id="tenant-z")
    assert row is not None
    loaded = repo.to_result(row)
    assert loaded.analysis_id == result.analysis_id
