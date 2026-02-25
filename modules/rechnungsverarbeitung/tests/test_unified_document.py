from datetime import timezone
from shared.document_model import (
    UnifiedDocumentMetadata,
    DocumentType,
    DocumentStatus,
    DataClassification,
)


class TestUnifiedDocumentMetadata:
    def test_create_sets_correct_type(self):
        doc = UnifiedDocumentMetadata.create(
            document_id="doc-001",
            tenant_id="tenant-a",
            document_type=DocumentType.INVOICE,
            file_name="test.pdf",
            mime_type="application/pdf",
        )
        assert doc.document_type == DocumentType.INVOICE

    def test_create_sets_retention(self):
        doc = UnifiedDocumentMetadata.create(
            document_id="doc-002",
            tenant_id="tenant-a",
            document_type=DocumentType.INVOICE,
            file_name="test.pdf",
            mime_type="application/pdf",
        )
        assert doc.retention_until is not None
        delta = doc.retention_until - doc.uploaded_at
        assert delta.days >= 3650  # >= 10 Jahre

    def test_soft_delete(self):
        doc = UnifiedDocumentMetadata.create(
            document_id="doc-003",
            tenant_id="tenant-a",
            document_type=DocumentType.INVOICE,
            file_name="test.pdf",
            mime_type="application/pdf",
        )
        doc.soft_delete()
        assert doc.status == DocumentStatus.DELETED
        assert doc.deleted_at is not None
        assert doc.deleted_at.tzinfo is not None  # timezone-aware

    def test_tenant_isolation(self):
        doc_a = UnifiedDocumentMetadata.create(
            document_id="doc-a",
            tenant_id="tenant-a",
            document_type=DocumentType.INVOICE,
            file_name="a.pdf",
            mime_type="application/pdf",
        )
        doc_b = UnifiedDocumentMetadata.create(
            document_id="doc-b",
            tenant_id="tenant-b",
            document_type=DocumentType.INVOICE,
            file_name="b.pdf",
            mime_type="application/pdf",
        )
        assert doc_a.tenant_id != doc_b.tenant_id
