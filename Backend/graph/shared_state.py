from typing import TypedDict, List, Dict, Any, Optional

class ClaimAdjudicationState(TypedDict, total=False):
    """Global claim state schema shared across the entire multi-agent graph execution."""

    # Claim core identifiers & input payload
    claim_id: str
    policy_number: str
    claimant_id: str
    product_line: str
    incident_date: str
    claimed_amount: float
    diagnosis_codes: List[str]
    procedure_codes: List[str]
    description: str

    # Agent 1: Intake & Classification state
    is_complete: bool
    missing_fields: List[str]
    complexity_score: float
    is_complex: bool

    # Agent 2: Policy Interpretation state
    policy_clauses: List[Dict[str, Any]]
    coverage_status: str
    exclusion_triggers: List[str]
    policy_interpretation_notes: str

    # Agent 3: Medical/Billing state
    medical_findings: List[Dict[str, Any]]
    code_mismatches: List[str]
    unusual_charges: List[str]
    allowed_total: float
    billing_status: str

    # Agent 4: Precedent RAG state
    precedent_cases: List[Dict[str, Any]]
    historical_approval_rate: float
    precedent_summary: str

    # Agent 5: Debate state
    pro_arguments: List[str]
    con_arguments: List[str]
    conflict_resolution: str
    reconciliation_recommendation: str
    confidence_delta: float
    debate_transcript: Optional[Dict[str, Any]]

    # Agent 6: Decision Drafting state
    draft_decision: Dict[str, Any]
    decision_type: str
    approved_amount: float
    rationale: str
    citations: List[str]
    itemized_payout: Dict[str, Any]

    # Agent 7: Compliance & Guardrail state
    compliance_passed: bool
    compliance_flags: List[str]
    human_review_required: bool
    human_review_reason: Optional[str]
    final_decision: Optional[Dict[str, Any]]

    # Agent 8: Orchestration Agent state (Single Routing Authority)
    last_completed_agent: str
    next_agent: str
    workflow_path: List[str]
    escalation_required: bool
    escalation_reason: Optional[str]
    workflow_reasoning: str
    agent_outputs_so_far: List[Dict[str, Any]]

    # System Graph Tracking
    status: str
    error: Optional[str]

    # Human review input fields (set by ClaimService.resume_human_review)
    human_approval_action: Optional[str]      # "APPROVE" | "OVERRIDE" | "SEND_BACK"
    human_adjudicator_notes: Optional[str]
    human_modified_payout: Optional[float]    # override payout (>= 0)
    human_decision_type: Optional[str]        # override decision type if different from draft
    human_actor_id: Optional[str]             # user id of the adjudicator
