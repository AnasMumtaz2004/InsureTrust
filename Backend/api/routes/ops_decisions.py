from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.database import get_db
from schemas.ops import HumanReviewActionRequest
from services.claim_service import ClaimService

router = APIRouter(prefix="/ops/decisions", tags=["Human-in-the-Loop Adjudicator Actions"])

@router.post("/{claim_id}/action")
def perform_human_adjudicator_action(claim_id: str, req: HumanReviewActionRequest, db: Session = Depends(get_db)):
    """Approve, Override, or Send Back a paused claim execution in LangGraph."""
    service = ClaimService(db)
    try:
        result = service.resume_human_review(
            claim_id=claim_id,
            action=req.action,
            notes=req.adjudicator_notes,
            modified_payout=req.modified_payout
        )
        return {
            "message": f"Successfully performed '{req.action}' on claim {claim_id}.",
            "claim_id": claim_id,
            "status": result["status"]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to perform action on claim {claim_id}: {str(e)}")

@router.post("/{claim_id}/approve")
def approve_claim(claim_id: str, notes: str = "Approved by human adjudicator.", db: Session = Depends(get_db)):
    """Fast shortcut endpoint for human approval."""
    service = ClaimService(db)
    res = service.resume_human_review(claim_id, action="APPROVE", notes=notes)
    return {"message": "Claim approved.", "claim_id": claim_id, "status": res["status"]}

@router.post("/{claim_id}/override")
def override_claim(claim_id: str, reason: str, modified_payout: float = None, db: Session = Depends(get_db)):
    """Fast shortcut endpoint for human override with modified payout."""
    service = ClaimService(db)
    res = service.resume_human_review(claim_id, action="OVERRIDE", notes=reason, modified_payout=modified_payout)
    return {"message": "Claim decision overridden.", "claim_id": claim_id, "status": res["status"]}
