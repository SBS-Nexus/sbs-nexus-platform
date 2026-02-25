from __future__ import annotations
import uuid
from shared.document_model import DocumentStatus
from modules.auftragsai.src.auftraege.models import AuftragsDocument


class AuftragsProcessor:
    """
    Verarbeitet hochgeladene Auftragsdokumente.
    Gleiche Service-Architektur wie Invoice- und HydraulikProcessor.
    """

    def process_upload(
        self,
        file_name: str,
        mime_type: str,
        uploaded_by: str = "system",
    ) -> AuftragsDocument:
        document_id = str(uuid.uuid4())
        doc = AuftragsDocument.for_new_upload(
            document_id=document_id,
            file_name=file_name,
            mime_type=mime_type,
            uploaded_by=uploaded_by,
        )
        doc.status = DocumentStatus.PROCESSED
        return doc
