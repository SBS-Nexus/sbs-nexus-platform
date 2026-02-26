from __future__ import annotations

from sqlalchemy.orm import Session

from modules.contract_analyzer.src.contracts.schemas import ContractAnalysisRequest, ContractAnalysisResult
from modules.contract_analyzer.src.contracts.services.analyzer import ContractAnalyzerService
from modules.contract_analyzer.src.contracts.services.storage import ContractAnalysisRepository
from shared.alerts.services import create_alert
from shared.tenant.context import TenantContext


class ContractAnalysisService:
    def __init__(self) -> None:
        self.analyzer = ContractAnalyzerService()
        self.repository = ContractAnalysisRepository()

    def analyze_and_store(self, db: Session, payload: ContractAnalysisRequest) -> ContractAnalysisResult:
        tenant_id = TenantContext.get_current_tenant()
        result = self.analyzer.analyze_contract(
            tenant_id=tenant_id,
            contract_id=payload.contract_id,
            contract_text=payload.contract_text,
            counterparty_name=payload.counterparty_name,
        )
        fingerprint = self.analyzer.fingerprint_content(payload.contract_text)
        self.repository.save(
            db,
            result=result,
            counterparty_name=payload.counterparty_name,
            content_fingerprint=fingerprint,
        )

        if result.risk_score >= 60:
            create_alert(
                db,
                tenant_id=tenant_id,
                alert_type="contract_high_risk",
                severity="high",
                message=f"Contract {payload.contract_id} analysed with risk score {result.risk_score}",
                source_module="contract_analyzer",
                counterparty_name=payload.counterparty_name,
                contract_document_id=payload.contract_id,
            )

        return result

    def get_analysis(self, db: Session, analysis_id: str) -> ContractAnalysisResult | None:
        tenant_id = TenantContext.get_current_tenant()
        row = self.repository.find_by_analysis_id(db, analysis_id=analysis_id, tenant_id=tenant_id)
        if not row:
            return None
        return self.repository.to_result(row)
