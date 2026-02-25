from __future__ import annotations
import uuid
from shared.document_model import DocumentStatus
from modules.hydraulikdoc.src.documents.models import HydraulikDocument


class HydraulikDocumentProcessor:
    """
    Verarbeitet hochgeladene Hydraulik-Dokumente.
    Gleiche Service-Architektur wie InvoiceProcessor.
    """

    def process_upload(
        self,
        file_name: str,
        mime_type: str,
        uploaded_by: str = "system",
    ) -> HydraulikDocument:
        document_id = str(uuid.uuid4())
        doc = HydraulikDocument.for_new_upload(
            document_id=document_id,
            file_name=file_name,
            mime_type=mime_type,
            uploaded_by=uploaded_by,
        )
        doc.status = DocumentStatus.PROCESSED
        return doc
