from enum import Enum


class ClaimStatus(str, Enum):
    SUBMITTED = "SUBMITTED"
    IN_REVIEW = "IN_REVIEW"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    PARTIAL_APPROVED = "PARTIAL_APPROVED"
    DENIED = "DENIED"
    OVERRIDDEN = "OVERRIDDEN"
    SENT_BACK = "SENT_BACK"
    PROCESSING_FAILED = "PROCESSING_FAILED"


TERMINAL_CLAIM_STATUSES = {
    ClaimStatus.APPROVED,
    ClaimStatus.PARTIAL_APPROVED,
    ClaimStatus.DENIED,
    ClaimStatus.OVERRIDDEN,
    ClaimStatus.SENT_BACK,
}


def map_decision_to_status(decision_type: str) -> ClaimStatus:
    decision_statuses = {
        "APPROVE": ClaimStatus.APPROVED,
        "PARTIAL_APPROVE": ClaimStatus.PARTIAL_APPROVED,
        "DENY": ClaimStatus.DENIED,
    }
    return decision_statuses.get(str(decision_type).upper(), ClaimStatus.PROCESSING_FAILED)


class Role(str, Enum):
    CUSTOMER = "customer"
    STAFF = "staff"
    ADMIN = "admin"
