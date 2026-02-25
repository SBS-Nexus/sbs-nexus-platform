from __future__ import annotations
from typing import Optional
from fastapi import FastAPI, UploadFile, File, Header, HTTPException
from shared.tenant.context import TenantContext
from shared.db.session import get_session
from modules.hydraulikdoc.src.documents.services.document_processing import (
    HydraulikDocumentProcessor,
)
from modules.hydraulikdoc.src.documents.db_models import HydraulikDoc

app = FastAPI(title="SBS HydraulikDoc API")
_processor = HydraulikDocumentProcessor()


def _set_tenant(x_tenant_id: Optional[str]) -> None:
    if not x_tenant_id:
        raise HTTPException(status_code=400, detail="X-Tenant-ID header is required")
    TenantContext.set_current_tenant(x_tenant_id)


@app.post("/hydraulik/upload")
async def upload_document(
    x_tenant_id: Optional[str] = Header(default=None, alias="X-Tenant-ID"),
    uploaded_by: Optional[str] = Header(default=None, alias="X-User-ID"),
    file: UploadFile = File(...),
):
    _set_tenant(x_tenant_id)
    doc = _processor.process_upload(
        file_name=file.filename,
        mime_type=file.content_type or "application/octet-stream",
        uploaded_by=uploaded_by or "system",
    )
    return {
        "document_id": doc.id,
        "tenant_id": doc.tenant_id,
        "status": doc.status,
        "file_name": doc.file_name,
        "document_type": doc.document_type,
    }


@app.get("/hydraulik/{document_id}")
async def get_document(
    document_id: str,
    x_tenant_id: Optional[str] = Header(default=None, alias="X-Tenant-ID"),
):
    _set_tenant(x_tenant_id)
    tenant_id = TenantContext.get_current_tenant()
    with get_session() as session:
        doc: HydraulikDoc | None = (
            session.query(HydraulikDoc)
            .filter(
                HydraulikDoc.document_id == document_id,
                HydraulikDoc.tenant_id == tenant_id,
            )
            .first()
        )
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        return {
            "document_id": doc.document_id,
            "tenant_id": doc.tenant_id,
            "status": doc.status,
            "file_name": doc.file_name,
            "document_type": doc.document_type,
            "uploaded_at": doc.uploaded_at.isoformat() if doc.uploaded_at else None,
        }


@app.get("/hydraulik")
async def list_documents(
    x_tenant_id: Optional[str] = Header(default=None, alias="X-Tenant-ID"),
    limit: int = 50,
    offset: int = 0,
):
    _set_tenant(x_tenant_id)
    tenant_id = TenantContext.get_current_tenant()
    with get_session() as session:
        docs = (
            session.query(HydraulikDoc)
            .filter(HydraulikDoc.tenant_id == tenant_id)
            .order_by(HydraulikDoc.uploaded_at.desc())
            .limit(limit).offset(offset)
        )
        items = [
            {
                "document_id": d.document_id,
                "status": d.status,
                "file_name": d.file_name,
                "uploaded_at": d.uploaded_at.isoformat() if d.uploaded_at else None,
            }
            for d in docs
        ]
    return {"items": items, "limit": limit, "offset": offset}


@app.get("/health")
async def health():
    return {"status": "ok"}
