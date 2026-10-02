from pydantic import BaseModel, Field, model_validator
from typing import Optional, List, Dict, Any, Literal

class HumanReviewActionRequest(BaseModel):
    action: Literal["APPROVE", "OVERRIDE", "SEND_BACK"] = Field(
        ...,
        description="The adjudicator action to perform."
    )
    adjudicator_notes: str = Field(
        ...,
        min_length=1,
        description="Notes from the adjudicator. Required for OVERRIDE and SEND_BACK."
    )
    modified_payout: Optional[float] = Field(
        None,
        ge=0,
        description="Modified payout amount. Must be >= 0. Only valid for OVERRIDE."
    )
    decision_type: Optional[Literal["APPROVE", "PARTIAL_APPROVE", "DENY"]] = Field(
        None,
        description="Override the decision type. Only valid for OVERRIDE."
    )

    @model_validator(mode="after")
    def _validate_action_fields(self) -> "HumanReviewActionRequest":
        if self.action == "OVERRIDE":
            # At least one of modified_payout or decision_type must be provided
            if self.modified_payout is None and self.decision_type is None:
                raise ValueError(
                    "OVERRIDE requires at least one of 'modified_payout' or 'decision_type'."
                )
        return self


class CaseQueueItemResponse(BaseModel):
    claim_id: str
    claim_number: str
    policy_number: str
    status: str
    complexity_score: float
    total_claimed_amount: float
    compliance_flags: List[str]
    created_at: str

class ExplanationResponse(BaseModel):
    claim_id: str
    summary: str
    policy_basis: List[str]
    medical_basis: List[str]
    citations: List[str]
    frequently_asked_questions: List[Dict[str, str]]

class QAChatRequest(BaseModel):
    claim_id: str
    user_question: str

class QAChatResponse(BaseModel):
    claim_id: str
    question: str
    answer: str
    sources: List[str]


class OpsUserResponse(BaseModel):
    id: str
    full_name: str
    email: str
    role: Literal["staff", "admin"]
    claims_acted_on: int
