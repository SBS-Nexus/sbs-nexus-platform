"""Exercise the frozen legacy baseline on a disposable PostgreSQL database."""
import os
from pathlib import Path

import pytest
import sqlalchemy as sa
from alembic import command
from alembic.config import Config


def validated_test_url(value, environment):
    parsed = sa.engine.make_url(value)
    if (parsed.drivername != "postgresql+psycopg"
            or parsed.host not in {"localhost", "127.0.0.1", "::1"}
            or not parsed.username
            or parsed.database not in {"nexus_ci", "sbs_nexus_ci"}
            or parsed.query
            or any(key.startswith("PG") and value for key, value in environment.items())):
        raise RuntimeError("Migration test requires an allowlisted local CI database")
    return parsed.set(host="127.0.0.1" if parsed.host == "localhost" else parsed.host,
                      port=parsed.port or 5432)


def require_empty_database(connection):
    occupied = connection.scalar(sa.text("""
        SELECT EXISTS (
            SELECT 1 FROM pg_namespace
            WHERE nspname NOT IN ('public', 'information_schema')
              AND left(nspname, 3) <> 'pg_'
        ) OR EXISTS (
            SELECT 1 FROM pg_class c
            JOIN pg_namespace n ON n.oid = c.relnamespace
            WHERE n.nspname <> 'information_schema'
              AND left(n.nspname, 3) <> 'pg_'
        )
    """))
    if occupied:
        raise RuntimeError("Migration test requires an empty disposable database")


@pytest.mark.parametrize("suffix", [
    "?host=example.invalid", "?hostaddr=192.0.2.12", "?dbname=not_ci",
    "?service=production", "?options=-csearch_path%3Dcustomer", "?plugin=custom",
])
def test_connection_query_overrides_are_rejected(suffix):
    with pytest.raises(RuntimeError):
        validated_test_url("postgresql+psycopg://ci@localhost/nexus_ci" + suffix, {})


@pytest.mark.parametrize("key", ["PGHOST", "PGHOSTADDR", "PGDATABASE", "PGPORT",
                                 "PGSERVICE", "PGSERVICEFILE", "PGOPTIONS"])
def test_environment_connection_overrides_are_rejected(key):
    with pytest.raises(RuntimeError):
        validated_test_url("postgresql+psycopg://ci@localhost/nexus_ci", {key: "override"})


def test_connection_target_is_explicit_loopback():
    url = validated_test_url("postgresql+psycopg://ci@localhost:55487/nexus_ci", {})
    assert url.host == "127.0.0.1"
    assert url.port == 55487
    assert not url.query


def test_legacy_upgrade_preserves_existing_rows():
    value = os.environ.get("MIGRATION_TEST_DATABASE_URL")
    if not value:
        pytest.skip("requires an explicitly configured disposable migration database")
    url = validated_test_url(value, os.environ)

    engine = sa.create_engine(url)
    try:
        with engine.begin() as connection:
            require_empty_database(connection)
            # Prove the guard also sees views and objects outside public. These
            # probes run only after the empty-database gate has succeeded.
            connection.execute(sa.text("CREATE VIEW public.ci_guard_view AS SELECT 1 AS value"))
            with pytest.raises(RuntimeError):
                require_empty_database(connection)
            connection.execute(sa.text("DROP VIEW public.ci_guard_view"))
            for schema in ("ci_guard_schema", "pgcustomer"):
                connection.execute(sa.text(f"CREATE SCHEMA {schema}"))
                with pytest.raises(RuntimeError):
                    require_empty_database(connection)
                connection.execute(sa.text(f"CREATE TABLE {schema}.sentinel (id INTEGER)"))
                with pytest.raises(RuntimeError):
                    require_empty_database(connection)
                connection.execute(sa.text(f"DROP TABLE {schema}.sentinel"))
                connection.execute(sa.text(f"DROP SCHEMA {schema}"))
            require_empty_database(connection)
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
        config.set_main_option("sqlalchemy.url", url.render_as_string(hide_password=False).replace("%", "%%"))
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
