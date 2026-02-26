from __future__ import annotations

import hashlib
import re
import uuid
from datetime import datetime, timezone

from modules.contract_analyzer.src.contracts.schemas import ClauseHit, ContractAnalysisResult


CLAUSE_PATTERNS: dict[str, tuple[str, re.Pattern[str], int]] = {
    "automatic_renewal": (
        "medium",
        re.compile(r"(automatische\s+verl[aä]ngerung|automatic\s+renewal)", re.IGNORECASE),
        20,
    ),
    "unlimited_liability": (
        "high",
        re.compile(r"(unbeschr[aä]nkte\s+haftung|unlimited\s+liability)", re.IGNORECASE),
        40,
    ),
    "short_termination": (
        "high",
        re.compile(r"(k[üu]ndigungsfrist\s+von\s+weniger\s+als\s+30\s+tagen|termination\s+notice\s+under\s+30\s+days)", re.IGNORECASE),
        30,
    ),
    "exclusive_jurisdiction": (
        "medium",
        re.compile(r"(ausschlie[sß]licher\s+gerichtsstand|exclusive\s+jurisdiction)", re.IGNORECASE),
        15,
    ),
}


class ContractAnalyzerService:
    source_module = "contract_analyzer"

    def analyze_contract(
        self,
        *,
        tenant_id: str,
        contract_id: str,
        contract_text: str,
        counterparty_name: str | None = None,
    ) -> ContractAnalysisResult:
        clause_hits: list[ClauseHit] = []
        risk_score = 0

        for clause_type, (risk_level, pattern, score) in CLAUSE_PATTERNS.items():
            match = pattern.search(contract_text)
            if not match:
                continue

            clause_hits.append(
                ClauseHit(
                    clause_type=clause_type,
                    risk_level=risk_level,
                    evidence=f"pattern:{clause_type}",
                )
            )
            risk_score += score

        risk_score = min(risk_score, 100)
        risk_tags = sorted({hit.clause_type for hit in clause_hits})

        return ContractAnalysisResult(
            analysis_id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            contract_id=contract_id,
            risk_score=risk_score,
            risk_tags=risk_tags,
            clause_hits=clause_hits,
            created_at=datetime.now(timezone.utc),
        )

    @staticmethod
    def fingerprint_content(contract_text: str) -> str:
        return hashlib.sha256(contract_text.encode("utf-8")).hexdigest()
