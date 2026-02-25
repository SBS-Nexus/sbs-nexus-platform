from fastapi.testclient import TestClient
from main import platform as app


class TestInvoiceUploadAPI:
    def setup_method(self):
        self.client = TestClient(app)

    def test_upload_invoice_endpoint(self):
        files = {"file": ("test.pdf", b"dummy content", "application/pdf")}
        headers = {"X-Tenant-ID": "tenant-api-test", "X-User-ID": "user-123"}
        resp = self.client.post("/api/v1/rechnungen/invoices/upload", files=files, headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["tenant_id"] == "tenant-api-test"
        assert data["document_type"] == "invoice"
        assert data["file_name"] == "test.pdf"
