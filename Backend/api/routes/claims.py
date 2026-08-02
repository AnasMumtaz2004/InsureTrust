from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.database import get_db
from database.models import Claim
from schemas.claims import ClaimSubmissionRequest, ClaimResponse, ClaimDetailResponse
from services.claim_service import ClaimService
from graph.main_graph import claims_graph

router = APIRouter(prefix="/claims", tags=["Claims Adjudication"])

@router.post("/submit", response_model=ClaimResponse, status_code=status.HTTP_201_CREATED)
def submit_claim(req: ClaimSubmissionRequest, db: Session = Depends(get_db)):
    """Submits an incoming insurance claim and triggers the multi-agent graph execution."""
    service = ClaimService(db)
    result = service.submit_and_process_claim(req.dict())

    db_claim = db.query(Claim).filter(Claim.id == result["claim_id"]).first()
    if not db_claim:
        raise HTTPException(status_code=500, detail="Failed to persist claim submission.")
    return db_claim

@router.get("", response_model=List[ClaimResponse])
def list_claims(limit: int = 50, db: Session = Depends(get_db)):
    """Lists submitted claims."""
    claims = db.query(Claim).order_by(Claim.created_at.desc()).limit(limit).all()
    return claims

@router.get("/{claim_id}", response_model=ClaimDetailResponse)
def get_claim_details(claim_id: str, db: Session = Depends(get_db)):
    """Retrieves full claim details including complete LangGraph snapshot state."""
    db_claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not db_claim:
        raise HTTPException(status_code=404, detail=f"Claim {claim_id} not found.")

    # Retrieve LangGraph thread state
    thread_config = {"configurable": {"thread_id": claim_id}}
    state_values = claims_graph.get_state(thread_config).values or {}

    response = ClaimDetailResponse(
        id=db_claim.id,
        claim_number=db_claim.claim_number,
        claimant_id=db_claim.claimant_id,
        policy_number=db_claim.policy_number,
        status=db_claim.status,
        complexity_score=db_claim.complexity_score,
        total_claimed_amount=db_claim.total_claimed_amount,
        approved_amount=db_claim.approved_amount,
        created_at=db_claim.created_at,
        updated_at=db_claim.updated_at,
        policy_clauses=state_values.get("policy_clauses", []),
        medical_findings=state_values.get("medical_findings", []),
        precedent_cases=state_values.get("precedent_cases", []),
        debate_transcript=state_values.get("debate_transcript"),
        compliance_flags=state_values.get("compliance_flags", []),
        final_decision=state_values.get("final_decision") or state_values.get("draft_decision"),
        citations=state_values.get("citations", [])
    )
    return response
