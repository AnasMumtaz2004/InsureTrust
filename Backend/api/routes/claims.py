from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.database import get_db
from database.models import Claim, ChatMessage
from schemas.claims import ClaimSubmissionRequest, ClaimResponse, ClaimDetailResponse
from services.claim_service import ClaimService
from graph.main_graph import claims_graph
from config import settings

try:
    from langchain_core.messages import HumanMessage
    from langchain_groq import ChatGroq
except ImportError:
    HumanMessage = None
    ChatGroq = None

router = APIRouter(prefix="/claims", tags=["Claims Adjudication"])


def _build_groq_llm():
    if ChatGroq is None or HumanMessage is None:
        raise RuntimeError("Groq integration is unavailable")
    if not settings.GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY is not configured")
    return ChatGroq(model="llama-3.1-8b-instant", groq_api_key=settings.GROQ_API_KEY, temperature=0.2)

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


@router.post("/{claim_id}/chat")
def claim_chat(claim_id: str, payload: dict, db: Session = Depends(get_db)):
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail=f"Claim {claim_id} not found.")

    message = payload.get("message", "") or ""
    if not message:
        raise HTTPException(status_code=400, detail="A message is required.")

    try:
        llm = _build_groq_llm()
    except RuntimeError:
        answer = "I can help summarize your claim and explain next steps. Please ask a specific question about coverage, status, or required documents."
    else:
        prompt = (
            "You are a helpful insurance assistant for policyholders. "
            f"The claim number is {claim.claim_number}. "
            f"Current status is {claim.status}. "
            f"Answer the user's message clearly and briefly. "
            f"User message: {message}"
        )
        answer = llm.invoke([HumanMessage(content=prompt)]).content

    db.add(ChatMessage(claim_id=claim_id, role="user", content=message))
    db.add(ChatMessage(claim_id=claim_id, role="assistant", content=answer))
    db.commit()

    return {"reply": answer}

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
