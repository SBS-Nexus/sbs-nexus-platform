"""Exercise the frozen legacy baseline on a disposable PostgreSQL database."""
import os
from pathlib import Path

import pytest
import sqlalchemy as sa
from alembic import command
from alembic.config import Config


def test_legacy_upgrade_preserves_existing_rows():
    url = os.environ.get("MIGRATION_TEST_DATABASE_URL")
    if not url:
        pytest.skip("requires an explicitly configured disposable migration database")
    parsed = sa.engine.make_url(url)
    if (parsed.get_backend_name() != "postgresql"
            or parsed.host not in {"localhost", "127.0.0.1", "::1"}
            or parsed.database not in {"nexus_ci", "sbs_nexus_ci"}):
        raise RuntimeError("Migration test requires an allowlisted local CI database")

    engine = sa.create_engine(url)
    try:
        with engine.begin() as connection:
            if sa.inspect(connection).get_table_names():
                raise RuntimeError("Migration test requires an empty disposable database")
            # ec247f9a356a deliberately stamps an existing legacy schema. It is
            # not a fresh-install migration; preserve that historical contract.
            connection.execute(sa.text("""
                CREATE TABLE invoices (
                    id SERIAL PRIMARY KEY,
                    document_id VARCHAR(64) UNIQUE NOT NULL,
                    tenant_id VARCHAR(128) NOT NULL,
                    document_type VARCHAR(32) NOT NULL,
                    file_name VARCHAR(512), mime_type VARCHAR(128),
                    uploaded_by VARCHAR(128), uploaded_at TIMESTAMP NOT NULL,
                    processed_at TIMESTAMP,
                    source_system VARCHAR(128) NOT NULL,
                    status VARCHAR(32) NOT NULL
                )
            """))
            connection.execute(sa.text("""
                INSERT INTO invoices
                    (document_id, tenant_id, document_type, uploaded_at, source_system, status)
                VALUES ('synthetic-migration', 'synthetic-tenant', 'invoice',
                        '2026-01-01', 'ci', 'uploaded')
            """))

        config = Config(str(Path(__file__).resolve().parents[1] / "alembic.ini"))
        # Escape ConfigParser interpolation, including percent-encoded passwords.
        config.set_main_option("sqlalchemy.url", url.replace("%", "%%"))
        command.upgrade(config, "head")
        assert "due_date" in {c["name"] for c in sa.inspect(engine).get_columns("invoices")}
        with engine.connect() as connection:
            assert connection.scalar(sa.text("SELECT document_id FROM invoices")) == "synthetic-migration"
            assert connection.scalar(sa.text("SELECT version_num FROM alembic_version")) == "4144765e814c"

        command.downgrade(config, "ec247f9a356a")
        assert "due_date" not in {c["name"] for c in sa.inspect(engine).get_columns("invoices")}
        command.upgrade(config, "head")
        with engine.connect() as connection:
            assert connection.scalar(sa.text("SELECT count(*) FROM invoices")) == 1
            assert connection.scalar(sa.text("SELECT tenant_id FROM invoices")) == "synthetic-tenant"
    finally:
        engine.dispose()
