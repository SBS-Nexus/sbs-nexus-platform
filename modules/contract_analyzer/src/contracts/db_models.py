from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from shared.db.session import Base


class ContractAnalysis(Base):
    __tablename__ = "contract_analyses"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    analysis_id: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    tenant_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    contract_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    counterparty_name: Mapped[str | None] = mapped_column(String(256), nullable=True)
    content_fingerprint: Mapped[str] = mapped_column(String(128), nullable=False)
    risk_score: Mapped[int] = mapped_column(Integer, nullable=False)
    risk_tags_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    clause_hits_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
