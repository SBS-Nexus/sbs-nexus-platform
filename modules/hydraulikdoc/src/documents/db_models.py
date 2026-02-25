from __future__ import annotations
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Integer
from shared.db.session import Base


class HydraulikDoc(Base):
    __tablename__ = "hydraulik_documents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(String, unique=True, nullable=False, index=True)
    tenant_id = Column(String, nullable=False, index=True)
    document_type = Column(String, default="hydraulik_doc")
    status = Column(String, default="uploaded")
    file_name = Column(String)
    mime_type = Column(String)
    uploaded_by = Column(String, default="system")
    uploaded_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    processed_at = Column(DateTime(timezone=True), nullable=True)
    source_system = Column(String, default="sbs-hydraulikdoc")
    retention_until = Column(DateTime(timezone=True), nullable=True)
