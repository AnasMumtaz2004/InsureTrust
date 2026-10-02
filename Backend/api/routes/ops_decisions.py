from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.database import get_db
from database.models import User
from database.enums import Role
from schemas.ops import HumanReviewActionRequest
from services.claim_service import ClaimService
from services.audit_service import AuditService
from api.deps import require_role

router = APIRouter(prefix="/ops/decisions", tags=["Human-in-the-Loop Adjudicator Actions"])

_NOT_AWAITING_MSG = "Claim is not awaiting human review"


def _handle_decision(
    db: Session,
    current_user: User,
    claim_id: str,
    req: HumanReviewActionRequest,
):
    service = ClaimService(db)
    audit = AuditService(db)
    try:
        result = service.resume_human_review(
            claim_id=claim_id,
            action=req.action,
            notes=req.adjudicator_notes,
            actor_id=current_user.id,
            modified_payout=req.modified_payout,
            decision_type=req.decision_type,
        )
        # Log successful action
        audit.log_step(
            claim_id=claim_id,
            agent_name=f"user:{current_user.id}",
            action=f"HUMAN_{req.action}",
            snapshot={
                "notes": req.adjudicator_notes,
                "modified_payout": req.modified_payout,
                "decision_type": req.decision_type,
            },
        )
        return result
    except HTTPException:
        raise
    except ValueError as e:
        msg = str(e)
        if _NOT_AWAITING_MSG in msg:
            raise HTTPException(status_code=409, detail=msg)
        if "No checkpoint found" in msg:
            raise HTTPException(status_code=404, detail=msg)
        raise HTTPException(status_code=409, detail=msg)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to perform action on claim {claim_id}: {str(e)}",
        )


@router.post("/{claim_id}/action")
def perform_human_adjudicator_action(
    claim_id: str,
    req: HumanReviewActionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(Role.STAFF, Role.ADMIN)),
):
    """Approve, Override, or Send Back a paused claim execution in LangGraph."""
    result = _handle_decision(db=db, current_user=current_user, claim_id=claim_id, req=req)
    return {
        "message": f"Successfully performed '{req.action}' on claim {claim_id}.",
        "claim_id": claim_id,
        "status": result["status"],
    }


@router.post("/{claim_id}/approve")
def approve_claim(
    claim_id: str,
    notes: str = "Approved by human adjudicator.",
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(Role.STAFF, Role.ADMIN)),
):
    """Fast shortcut endpoint for human approval."""
    req = HumanReviewActionRequest(action="APPROVE", adjudicator_notes=notes)
    result = _handle_decision(db, current_user, claim_id, req)
    return {"message": "Claim approved.", "claim_id": claim_id, "status": result["status"]}


@router.post("/{claim_id}/override")
def override_claim(
    claim_id: str,
    reason: str,
    modified_payout: float = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(Role.STAFF, Role.ADMIN)),
):
    """Fast shortcut endpoint for human override with modified payout."""
    req = HumanReviewActionRequest(
        action="OVERRIDE",
        adjudicator_notes=reason,
        modified_payout=modified_payout,
        # Ensure at least one override field is present for schema validation
        decision_type="APPROVE" if modified_payout is None else None,
    )
    result = _handle_decision(db, current_user, claim_id, req)
    return {"message": "Claim decision overridden.", "claim_id": claim_id, "status": result["status"]}
