import uuid
import datetime
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from database.database import get_db
from database.models import Document, Claim
from schemas.documents import DocumentUploadResponse, CompletenessCheckResponse
from agents.intake_agent.tools import validate_claim_fields

router = APIRouter(prefix="/documents", tags=["Document Management"])

@router.post("/upload", response_model=DocumentUploadResponse)
def upload_claim_document(
    claim_id: str = Form(...),
    document_type: str = Form(...),  # MEDICAL_BILL, CLINICAL_NOTE, RECEIPT, POLICY_DOC
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Uploads and associates a medical or policy document with a claim."""
    db_claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not db_claim:
        raise HTTPException(status_code=404, detail=f"Claim {claim_id} not found.")

    doc_id = f"DOC-{uuid.uuid4().hex[:8].upper()}"
    storage_path = f"./uploads/{doc_id}_{file.filename}"

    doc = Document(
        id=doc_id,
        claim_id=claim_id,
        document_name=file.filename,
        document_type=document_type,
        storage_path=storage_path,
        processed_status="PROCESSED"
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc

@router.post("/check-completeness", response_model=CompletenessCheckResponse)
def check_document_completeness(claim_id: str, db: Session = Depends(get_db)):
    """Verifies document completeness for a given claim submission."""
    db_claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not db_claim:
        raise HTTPException(status_code=404, detail=f"Claim {claim_id} not found.")

    docs = db.query(Document).filter(Document.claim_id == claim_id).all()
    doc_types = {d.document_type for d in docs}

    missing = []
    if "MEDICAL_BILL" not in doc_types:
        missing.append("MEDICAL_BILL")
    if "CLINICAL_NOTE" not in doc_types:
        missing.append("CLINICAL_NOTE")

    is_complete = len(missing) == 0
    confidence = 1.0 if is_complete else 0.6

    return CompletenessCheckResponse(
        is_complete=is_complete,
        missing_fields=missing,
        confidence_score=confidence,
        recommendations=["Please upload missing clinical notes or billing receipts."] if missing else ["Documents complete."]
    )
