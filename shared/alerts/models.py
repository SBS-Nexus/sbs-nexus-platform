from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.dialects.postgresql import UUID
import uuid

from shared.db.session import Base  # an deine Base anpassen


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(String, index=True, nullable=False)
    alert_type = Column(String, index=True, nullable=False)
    severity = Column(String, nullable=False)
    message = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    source_module = Column(String, nullable=True)
    counterparty_name = Column(String, nullable=True)
    invoice_document_id = Column(String, nullable=True)
    contract_document_id = Column(String, nullable=True)
