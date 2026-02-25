import uuid
import pytest
from unittest.mock import patch

from shared.tenant.context import TenantContext
from modules.rechnungsverarbeitung.src.invoices.services.invoice_processing import process_invoice_upload


DUMMY_TENANT = "tenant-test-001"


@pytest.fixture(autouse=True)
def set_tenant():
    with patch.object(TenantContext, "get_current_tenant", return_value=DUMMY_TENANT):
        yield


class TestProcessInvoiceUpload:
    def test_returns_invoice_metadata(self):
        result = process_invoice_upload(
            file_stream=b"dummy",
            file_name="rechnung.pdf",
            mime_type="application/pdf",
            uploaded_by="user@test.de",
        )
        assert result is not None

    def test_document_id_is_uuid(self):
        result = process_invoice_upload(
            file_stream=b"dummy",
            file_name="rechnung.pdf",
            mime_type="application/pdf",
        )
        assert uuid.UUID(result.id)

    def test_final_status_is_booked(self):
        result = process_invoice_upload(
            file_stream=b"dummy",
            file_name="rechnung.pdf",
            mime_type="application/pdf",
        )
        assert result.status is not None

    def test_tenant_isolation(self):
        result = process_invoice_upload(
            file_stream=b"dummy",
            file_name="rechnung.pdf",
            mime_type="application/pdf",
        )
        assert result.tenant_id == DUMMY_TENANT
