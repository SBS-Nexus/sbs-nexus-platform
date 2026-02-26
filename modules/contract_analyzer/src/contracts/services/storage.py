from __future__ import annotations

import json
from sqlalchemy.orm import Session

from modules.contract_analyzer.src.contracts.db_models import ContractAnalysis
from modules.contract_analyzer.src.contracts.schemas import ClauseHit, ContractAnalysisResult


class ContractAnalysisRepository:
    @staticmethod
    def save(
        db: Session,
        *,
        result: ContractAnalysisResult,
        counterparty_name: str | None,
        content_fingerprint: str,
    ) -> ContractAnalysis:
        row = ContractAnalysis(
            analysis_id=result.analysis_id,
            tenant_id=result.tenant_id,
            contract_id=result.contract_id,
            counterparty_name=counterparty_name,
            content_fingerprint=content_fingerprint,
            risk_score=result.risk_score,
            risk_tags_json=json.dumps(result.risk_tags),
            clause_hits_json=json.dumps([hit.model_dump() for hit in result.clause_hits]),
            created_at=result.created_at.replace(tzinfo=None),
        )
        db.add(row)
        db.flush()
        return row

    @staticmethod
    def find_by_analysis_id(db: Session, *, analysis_id: str, tenant_id: str) -> ContractAnalysis | None:
        return (
            db.query(ContractAnalysis)
            .filter(
                ContractAnalysis.analysis_id == analysis_id,
                ContractAnalysis.tenant_id == tenant_id,
            )
            .first()
        )

    @staticmethod
    def to_result(row: ContractAnalysis) -> ContractAnalysisResult:
        return ContractAnalysisResult(
            analysis_id=row.analysis_id,
            tenant_id=row.tenant_id,
            contract_id=row.contract_id,
            risk_score=row.risk_score,
            risk_tags=json.loads(row.risk_tags_json),
            clause_hits=[ClauseHit.model_validate(hit) for hit in json.loads(row.clause_hits_json)],
            created_at=row.created_at,
        )
