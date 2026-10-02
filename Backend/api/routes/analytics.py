from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.database import get_db
from database.models import Claim, Decision, AuditLog, User
from database.enums import ClaimStatus, Role, TERMINAL_CLAIM_STATUSES
from api.deps import require_role

router = APIRouter(prefix="/analytics", tags=["Analytics & KPIs"])

@router.get("/kpis")
def get_platform_kpis(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(Role.STAFF, Role.ADMIN))
):
    """Returns top-level platform operational metrics (adjudication velocity, approval rate, human override rate)."""
    total_claims = db.query(Claim).count()
    approved_claims = db.query(Claim).filter(Claim.status.in_([
        ClaimStatus.APPROVED.value,
        ClaimStatus.PARTIAL_APPROVED.value,
    ])).count()
    partial_approved_claims = db.query(Claim).filter(
        Claim.status == ClaimStatus.PARTIAL_APPROVED.value
    ).count()
    denied_claims = db.query(Claim).filter(Claim.status == ClaimStatus.DENIED.value).count()
    pending_claims = db.query(Claim).filter(Claim.status.in_([
        ClaimStatus.PENDING_APPROVAL.value,
        ClaimStatus.IN_REVIEW.value,
    ])).count()
    failed_claims = db.query(Claim).filter(
        Claim.status == ClaimStatus.PROCESSING_FAILED.value
    ).count()
    sent_back_claims = db.query(Claim).filter(Claim.status == ClaimStatus.SENT_BACK.value).count()
    overridden_claims = db.query(Decision).filter(Decision.human_overridden == True).count()
    completed_decisions = db.query(Decision).filter(
        Decision.compliance_status != "PENDING_REVIEW"
    ).count()
    completed_times = db.query(Claim.created_at, Claim.completed_at).filter(
        Claim.status.in_([status.value for status in TERMINAL_CLAIM_STATUSES]),
        Claim.completed_at.isnot(None),
    ).all()
    average_processing_time = (
        round(sum((completed - created).total_seconds() for created, completed in completed_times)
              / len(completed_times), 2)
        if completed_times else None
    )

    approval_rate = round(approved_claims / total_claims, 2) if total_claims > 0 else 0.0
    override_rate = round(overridden_claims / completed_decisions, 2) if completed_decisions > 0 else 0.0

    return {
        "total_claims_processed": total_claims,
        "approved_claims": approved_claims,
        "partial_approved_claims": partial_approved_claims,
        "denied_claims": denied_claims,
        "pending_human_review": pending_claims,
        "failed_claims": failed_claims,
        "sent_back_claims": sent_back_claims,
        "human_overridden_claims": overridden_claims,
        "automated_approval_rate": approval_rate,
        "human_override_rate": override_rate,
        "average_processing_time_seconds": average_processing_time,
    }


@router.get("/audit-logs")
def get_audit_logs(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(Role.STAFF, Role.ADMIN))
):
    logs = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(25).all()
    return [
        {
            "id": log.id,
            "action": log.action,
            "agent_name": log.agent_name,
            "claim_id": log.claim_id,
            "timestamp": log.timestamp.isoformat(),
        }
        for log in logs
    ]
