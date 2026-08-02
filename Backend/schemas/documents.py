from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class DocumentUploadResponse(BaseModel):
    id: str
    claim_id: str
    document_name: str
    document_type: str
    processed_status: str
    uploaded_at: datetime

    class Config:
        from_attributes = True

class CompletenessCheckResponse(BaseModel):
    is_complete: bool
    missing_fields: list[str] = []
    confidence_score: float
    recommendations: list[str] = []
