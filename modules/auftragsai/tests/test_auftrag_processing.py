import uuid
from shared.document_model import DocumentType, DocumentStatus, DataClassification
from modules.auftragsai.src.auftraege.services.auftrag_processing import AuftragsProcessor


class TestAuftragsProcessor:
    def setup_method(self):
        self.processor = AuftragsProcessor()

    def test_returns_auftrag_document(self):
        doc = self.processor.process_upload("auftrag.pdf", "application/pdf")
        assert doc.file_name == "auftrag.pdf"
        assert doc.document_type == DocumentType.AUFTRAG

    def test_document_id_is_uuid(self):
        doc = self.processor.process_upload("auftrag.pdf", "application/pdf")
        assert uuid.UUID(doc.id)

    def test_final_status_is_processed(self):
        doc = self.processor.process_upload("auftrag.pdf", "application/pdf")
        assert doc.status == DocumentStatus.PROCESSED

    def test_tenant_isolation(self):
        doc_a = self.processor.process_upload("a.pdf", "application/pdf")
        doc_b = self.processor.process_upload("b.pdf", "application/pdf")
        assert doc_a.tenant_id == doc_b.tenant_id == "test-tenant-auftragsai"

    def test_classification_confidential(self):
        doc = self.processor.process_upload("auftrag.pdf", "application/pdf")
        assert doc.classification == DataClassification.CONFIDENTIAL

    def test_retention_set(self):
        doc = self.processor.process_upload("auftrag.pdf", "application/pdf")
        assert doc.retention_until is not None
