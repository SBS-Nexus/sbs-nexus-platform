from fastapi.testclient import TestClient
from main import platform as app
from shared.document_model import DocumentType


class TestAuftragsUploadAPI:
    def setup_method(self):
        self.client = TestClient(app)

    def test_upload_auftrag_endpoint(self):
        files = {"file": ("auftrag.pdf", b"dummy content", "application/pdf")}
        headers = {"X-Tenant-ID": "tenant-auftrag-test", "X-User-ID": "user-789"}
        resp = self.client.post("/api/v1/auftraege/auftraege/upload", files=files, headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["tenant_id"] == "tenant-auftrag-test"
        assert data["file_name"] == "auftrag.pdf"
        assert data["document_type"] == DocumentType.AUFTRAG
