import uuid
import datetime
import os
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from database.database import get_db
from database.models import Document, Claim, User
from schemas.documents import DocumentUploadResponse, CompletenessCheckResponse
from api.deps import get_current_user, assert_claim_access

router = APIRouter(prefix="/documents", tags=["Document Management"])

@router.post("/upload", response_model=DocumentUploadResponse)
def upload_claim_document(
    claim_id: str = Form(...),
    document_type: str = Form(...),  # MEDICAL_BILL, CLINICAL_NOTE, RECEIPT, POLICY_DOC
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Uploads and associates a medical or policy document with a claim."""
    db_claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not db_claim:
        raise HTTPException(status_code=404, detail=f"Claim {claim_id} not found.")
        
    assert_claim_access(current_user, db_claim)

    from config import settings
    
    ext_map = {
        "application/pdf": ".pdf",
        "image/jpeg": ".jpg",
        "image/png": ".png"
    }
    
    if file.content_type not in settings.uploads.allowed_types:
        raise HTTPException(status_code=415, detail="Unsupported file type")
        
    ext = ext_map.get(file.content_type, "")

    doc_id = f"DOC-{uuid.uuid4().hex[:8].upper()}"
    
    upload_dir = settings.uploads.dir
    os.makedirs(upload_dir, exist_ok=True)
    storage_path = os.path.join(upload_dir, f"{doc_id}{ext}")
    
    max_bytes = settings.uploads.max_mb * 1024 * 1024
    bytes_written = 0
    
    try:
        with open(storage_path, "wb") as out_file:
            while chunk := file.file.read(8192):
                bytes_written += len(chunk)
                if bytes_written > max_bytes:
                    out_file.close()
                    os.remove(storage_path)
                    raise HTTPException(status_code=413, detail="File too large")
                out_file.write(chunk)
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail="Failed to save file")
        
    doc = Document(
        id=doc_id,
        claim_id=claim_id,
        document_name=os.path.basename(file.filename),
        document_type=document_type,
        storage_path=storage_path,
        processed_status="UPLOADED"
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc

@router.post("/check-completeness", response_model=CompletenessCheckResponse)
def check_document_completeness(
    claim_id: str, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Verifies document completeness for a given claim submission."""
    db_claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not db_claim:
        raise HTTPException(status_code=404, detail=f"Claim {claim_id} not found.")
        
    assert_claim_access(current_user, db_claim)

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
