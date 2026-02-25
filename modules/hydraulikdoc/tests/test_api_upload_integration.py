from fastapi.testclient import TestClient
from main import platform as app
from shared.document_model import DocumentType


class TestHydraulikUploadAPI:
    def setup_method(self):
        self.client = TestClient(app)

    def test_upload_hydraulik_document_endpoint(self):
        files = {"file": ("schema.pdf", b"dummy content", "application/pdf")}
        headers = {"X-Tenant-ID": "tenant-hydraulik-test", "X-User-ID": "user-456"}
        resp = self.client.post("/api/v1/hydraulik/hydraulik/upload", files=files, headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["tenant_id"] == "tenant-hydraulik-test"
        assert data["file_name"] == "schema.pdf"
        assert data["document_type"] == DocumentType.HYDRAULIK_DOC
