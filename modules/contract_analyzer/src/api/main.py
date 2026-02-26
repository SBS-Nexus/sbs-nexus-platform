from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, FastAPI, Header, HTTPException
from sqlalchemy.orm import Session

from modules.contract_analyzer.src.contracts.schemas import ContractAnalysisRequest, ContractAnalysisResult
from modules.contract_analyzer.src.contracts.services.contract_analysis import ContractAnalysisService
from shared.db.session import get_session
from shared.tenant.context import TenantContext


router = APIRouter(prefix="/contracts", tags=["contract-analyzer"])
service = ContractAnalysisService()


def _set_tenant_from_header(x_tenant_id: Optional[str]) -> None:
    if not x_tenant_id:
        raise HTTPException(status_code=400, detail="X-Tenant-ID header is required")
    TenantContext.set_current_tenant(x_tenant_id)


@router.post("/analyze", response_model=ContractAnalysisResult)
def analyze_contract(
    payload: ContractAnalysisRequest,
    x_tenant_id: Optional[str] = Header(default=None, alias="X-Tenant-ID"),
    db: Session = Depends(get_session),
) -> ContractAnalysisResult:
    _set_tenant_from_header(x_tenant_id)
    return service.analyze_and_store(db, payload)


@router.get("/analyses/{analysis_id}", response_model=ContractAnalysisResult)
def get_contract_analysis(
    analysis_id: str,
    x_tenant_id: Optional[str] = Header(default=None, alias="X-Tenant-ID"),
    db: Session = Depends(get_session),
) -> ContractAnalysisResult:
    _set_tenant_from_header(x_tenant_id)
    result = service.get_analysis(db, analysis_id)
    if not result:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return result


app = FastAPI(title="Contract Analyzer API")
app.include_router(router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
