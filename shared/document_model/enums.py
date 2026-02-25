from enum import Enum


class DocumentType(str, Enum):
    INVOICE = "invoice"
    HYDRAULIK_DOC = "hydraulik_doc"
    AUFTRAG = "auftrag"
    CONTRACT = "contract"
    UNKNOWN = "unknown"


class DocumentStatus(str, Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    PROCESSED = "processed"
    BOOKED = "booked"
    ARCHIVED = "archived"
    DELETED = "deleted"
    ERROR = "error"


class DataClassification(str, Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"  # DSGVO-relevante Dokumente
