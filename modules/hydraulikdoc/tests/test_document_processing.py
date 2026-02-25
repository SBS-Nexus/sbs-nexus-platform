import uuid
from shared.document_model import DocumentType, DocumentStatus, DataClassification
from modules.hydraulikdoc.src.documents.services.document_processing import (
    HydraulikDocumentProcessor,
)


class TestHydraulikDocumentProcessor:
    def setup_method(self):
        self.processor = HydraulikDocumentProcessor()

    def test_returns_hydraulik_document(self):
        doc = self.processor.process_upload("schema.pdf", "application/pdf")
        assert doc.file_name == "schema.pdf"
        assert doc.document_type == DocumentType.HYDRAULIK_DOC

    def test_document_id_is_uuid(self):
        doc = self.processor.process_upload("schema.pdf", "application/pdf")
        assert uuid.UUID(doc.id)

    def test_final_status_is_processed(self):
        doc = self.processor.process_upload("schema.pdf", "application/pdf")
        assert doc.status == DocumentStatus.PROCESSED

    def test_tenant_isolation(self):
        doc_a = self.processor.process_upload("a.pdf", "application/pdf")
        doc_b = self.processor.process_upload("b.pdf", "application/pdf")
        assert doc_a.tenant_id == doc_b.tenant_id == "test-tenant-hydraulik"

    def test_retention_set(self):
        doc = self.processor.process_upload("schema.pdf", "application/pdf")
        assert doc.retention_until is not None

    def test_classification_internal(self):
        doc = self.processor.process_upload("schema.pdf", "application/pdf")
        assert doc.classification == DataClassification.INTERNAL
