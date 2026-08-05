import os
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.database import get_db
from database.models import Claim, ChatMessage
from schemas.ops import ExplanationResponse, QAChatRequest, QAChatResponse
from graph.main_graph import claims_graph
from config import settings

try:
    from langchain_core.messages import HumanMessage
    from langchain_groq import ChatGroq
except ImportError:
    HumanMessage = None
    ChatGroq = None

router = APIRouter(prefix="/explanation", tags=["Claimant Explanation & Q&A"])


def _build_groq_llm():
    if ChatGroq is None or HumanMessage is None:
        raise RuntimeError("Groq integration is unavailable")
    if not settings.GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY is not configured")
    return ChatGroq(model="llama-3.1-8b-instant", groq_api_key=settings.GROQ_API_KEY, temperature=0.2)

@router.get("/{claim_id}", response_model=ExplanationResponse)
def get_claimant_explanation(claim_id: str, db: Session = Depends(get_db)):
    """Provides a claimant-friendly explanation of the adjudication decision."""
    db_claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not db_claim:
        raise HTTPException(status_code=404, detail=f"Claim {claim_id} not found.")

    thread_config = {"configurable": {"thread_id": claim_id}}
    state = claims_graph.get_state(thread_config).values or {}

    final_dec = state.get("final_decision") or state.get("draft_decision") or {}
    policy_basis = [c.get("clause_title", "Policy Clause") for c in state.get("policy_clauses", [])]
    medical_basis = state.get("code_mismatches", ["Medical codes validated against clinical guidelines."])

    summary = (
        f"Your claim #{db_claim.claim_number} for ${db_claim.total_claimed_amount:,.2f} has been evaluated. "
        f"The outcome is: {db_claim.status}. Approved payout amount: ${db_claim.approved_amount:,.2f}. "
        f"Rationale: {final_dec.get('rationale', 'Adjudicated per standard policy coverage limits.')}"
    )

    faqs = [
        {"question": "How was my payout calculated?", "answer": f"Your payout was calculated based on fee schedules and covered policy provisions ($ {db_claim.approved_amount:,.2f})."},
        {"question": "Can I appeal this finding?", "answer": "Yes. You may submit additional clinical notes or request an administrative review within 30 days."}
    ]

    return ExplanationResponse(
        claim_id=claim_id,
        summary=summary,
        policy_basis=policy_basis,
        medical_basis=medical_basis,
        citations=state.get("citations", []),
        frequently_asked_questions=faqs
    )

@router.post("/chat", response_model=QAChatResponse)
def ask_explanation_question(req: QAChatRequest, db: Session = Depends(get_db)):
    """Interactive Q&A chat endpoint answering claimant questions about their specific decision."""
    db_claim = db.query(Claim).filter(Claim.id == req.claim_id).first()
    if not db_claim:
        raise HTTPException(status_code=404, detail=f"Claim {req.claim_id} not found.")

    try:
        llm = _build_groq_llm()
    except RuntimeError:
        answer = (
            f"Your claim {db_claim.claim_number} was reviewed against policy terms and billing standards. "
            f"The current approved amount is ${db_claim.approved_amount:,.2f}."
        )
    else:
        context = (
            f"Claim number: {db_claim.claim_number}\n"
            f"Status: {db_claim.status}\n"
            f"Total claimed amount: ${db_claim.total_claimed_amount:,.2f}\n"
            f"Approved amount: ${db_claim.approved_amount:,.2f}\n"
            f"Policy number: {db_claim.policy_number}\n"
        )
        prompt = (
            "You are a concise insurance claims explanation assistant. "
            "Answer the user's question about the claim in plain language. "
            f"Use this claim context:\n{context}\n"
            f"User question: {req.user_question}"
        )
        answer = llm.invoke([HumanMessage(content=prompt)]).content

    db.add(ChatMessage(claim_id=req.claim_id, role="user", content=req.user_question))
    db.add(ChatMessage(claim_id=req.claim_id, role="assistant", content=answer))
    db.commit()

    return QAChatResponse(
        claim_id=req.claim_id,
        question=req.user_question,
        answer=answer,
        sources=["Policy Terms & Conditions", "Adjudication Decision Audit Trail"],
    )
