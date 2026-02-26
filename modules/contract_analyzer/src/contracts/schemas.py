from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field


class ContractAnalysisRequest(BaseModel):
    contract_id: str = Field(min_length=1, max_length=128)
    counterparty_name: str | None = Field(default=None, max_length=256)
    contract_text: str = Field(min_length=50, max_length=100_000)


class ClauseHit(BaseModel):
    clause_type: str
    risk_level: str
    evidence: str


class ContractAnalysisResult(BaseModel):
    analysis_id: str
    tenant_id: str
    contract_id: str
    risk_score: int
    risk_tags: list[str]
    clause_hits: list[ClauseHit]
    created_at: datetime


class ContractAnalysisListItem(BaseModel):
    analysis_id: str
    contract_id: str
    risk_score: int
    risk_tags: list[str]
    created_at: datetime
