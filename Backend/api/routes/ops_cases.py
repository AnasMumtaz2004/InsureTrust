from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, distinct
from sqlalchemy.orm import Session
from database.database import get_db
from database.models import Claim, DebateTranscript, AuditLog, User, Decision
from database.enums import ClaimStatus, Role
from schemas.ops import CaseQueueItemResponse, OpsUserResponse
from graph.main_graph import claims_graph
from api.deps import require_role

router = APIRouter(prefix="/ops/cases", tags=["Back-Office Operations Queue"])
users_router = APIRouter(prefix="/ops", tags=["Back-Office Operations"])


@users_router.get("/users", response_model=List[OpsUserResponse])
def get_operations_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(Role.STAFF, Role.ADMIN)),
):
    """List staff users and the number of distinct claims each has acted on."""
    action_counts = dict(
        db.query(
            Decision.approved_by,
            func.count(distinct(Decision.claim_id)),
        )
        .filter(Decision.approved_by.isnot(None), Decision.approved_by != "AUTO_SYSTEM")
        .group_by(Decision.approved_by)
        .all()
    )
    users = (
        db.query(User)
        .filter(User.role.in_([Role.STAFF.value, Role.ADMIN.value]))
        .order_by(User.full_name.asc())
        .all()
    )
    return [
        OpsUserResponse(
            id=user.id,
            full_name=user.full_name,
            email=user.email,
            role=user.role,
            claims_acted_on=action_counts.get(user.id, 0),
        )
        for user in users
    ]

@router.get("/queue", response_model=List[CaseQueueItemResponse])
def get_operations_queue(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(Role.STAFF, Role.ADMIN))
):
    """Returns back-office queue of cases requiring human review or oversight."""
    pending_claims = db.query(Claim).filter(
        Claim.status.in_([
            ClaimStatus.PENDING_APPROVAL.value,
            ClaimStatus.IN_REVIEW.value,
            ClaimStatus.SENT_BACK.value,
            ClaimStatus.PROCESSING_FAILED.value,
        ])
    ).order_by(Claim.created_at.desc()).all()

    items = []
    for c in pending_claims:
        thread_config = {"configurable": {"thread_id": c.id}}
        state = claims_graph.get_state(thread_config).values or {}
        items.append(CaseQueueItemResponse(
            claim_id=c.id,
            claim_number=c.claim_number,
            policy_number=c.policy_number,
            status=c.status,
            complexity_score=c.complexity_score or 0.0,
            total_claimed_amount=c.total_claimed_amount,
            compliance_flags=state.get("compliance_flags", []),
            created_at=c.created_at.isoformat()
        ))
    return items

@router.get("/{claim_id}/graph-state")
def inspect_claim_graph_state(
    claim_id: str, 
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(Role.STAFF, Role.ADMIN))
):
    """Inspects full live LangGraph execution state for debugging and auditing."""
    thread_config = {"configurable": {"thread_id": claim_id}}
    state_snapshot = claims_graph.get_state(thread_config)
    if not state_snapshot.values:
        raise HTTPException(status_code=404, detail=f"No active or stored graph execution found for claim {claim_id}")

    return {
        "claim_id": claim_id,
        "next_node": state_snapshot.next,
        "values": state_snapshot.values,
        "metadata": state_snapshot.metadata
    }

@router.get("/{claim_id}/debate-transcript")
def get_debate_transcript(
    claim_id: str, 
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(Role.STAFF, Role.ADMIN))
):
    """Retrieves structured pro/con debate transcript for cases that triggered the Debate Agent."""
    transcript = db.query(DebateTranscript).filter(DebateTranscript.claim_id == claim_id).first()
    if not transcript:
        # Fallback to check graph state
        thread_config = {"configurable": {"thread_id": claim_id}}
        state = claims_graph.get_state(thread_config).values or {}
        dt = state.get("debate_transcript")
        if not dt:
            raise HTTPException(status_code=404, detail=f"No debate transcript recorded for claim {claim_id}")
        return dt

    return {
        "claim_id": claim_id,
        "pro_approval_arguments": transcript.pro_approval_arguments,
        "pro_denial_arguments": transcript.pro_denial_arguments,
        "reconciliation_summary": transcript.reconciliation_summary,
        "confidence_delta": transcript.confidence_delta
    }

@router.get("/{claim_id}/audit-trail")
def get_claim_audit_trail(
    claim_id: str, 
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(Role.STAFF, Role.ADMIN))
):
    """Retrieves step-by-step immutable audit log trail for a claim."""
    logs = db.query(AuditLog).filter(AuditLog.claim_id == claim_id).order_by(AuditLog.timestamp.asc()).all()
    return logs
