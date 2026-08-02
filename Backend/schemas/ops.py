from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class HumanReviewActionRequest(BaseModel):
    action: str = Field(..., example="APPROVE")  # "APPROVE", "OVERRIDE", "SEND_BACK"
    adjudicator_notes: str = Field(..., example="Verified manual pre-authorization override.")
    modified_payout: Optional[float] = Field(None, example=3200.00)
    override_reason: Optional[str] = Field(None, example="Special medical director exception granted.")

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
