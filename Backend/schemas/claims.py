from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class ClaimSubmissionRequest(BaseModel):
    policy_number: str = Field(..., example="POL-994821")
    claimant_id: Optional[str] = Field(None, example="USR-1002")
    incident_date: str = Field(..., example="2026-06-15")
    claimed_amount: float = Field(..., example=3450.00)
    diagnosis_codes: List[str] = Field(default_factory=list, example=["M54.5", "S39.011A"])
    procedure_codes: List[str] = Field(default_factory=list, example=["99214", "93000"])
    description: str = Field(..., example="Patient presented with acute low back pain following lifting heavy object.")
    documents_attached: List[str] = Field(default_factory=list, example=["DOC-1", "DOC-2"])

class ClaimResponse(BaseModel):
    id: str
    claim_number: str
    claimant_id: str
    policy_number: str
    status: str
    complexity_score: Optional[float] = None
    total_claimed_amount: float
    approved_amount: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ClaimDetailResponse(ClaimResponse):
    policy_clauses: List[Dict[str, Any]] = []
    medical_findings: List[Dict[str, Any]] = []
    precedent_cases: List[Dict[str, Any]] = []
    debate_transcript: Optional[Dict[str, Any]] = None
    compliance_flags: List[str] = []
    final_decision: Optional[Dict[str, Any]] = None
    citations: List[str] = []
