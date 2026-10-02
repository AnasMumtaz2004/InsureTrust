from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.database import get_db
from database.models import Claim, ChatMessage, User
from schemas.ops import ExplanationResponse, QAChatRequest, QAChatResponse
from graph.main_graph import claims_graph
from config import settings
from api.deps import get_current_user, assert_claim_access

try:
    from langchain_core.messages import HumanMessage
except ImportError:
    HumanMessage = None

router = APIRouter(prefix="/explanation", tags=["Claimant Explanation & Q&A"])

@router.get("/{claim_id}", response_model=ExplanationResponse)
def get_claimant_explanation(
    claim_id: str, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Provides a claimant-friendly explanation of the adjudication decision."""
    db_claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not db_claim:
        raise HTTPException(status_code=404, detail=f"Claim {claim_id} not found.")
        
    assert_claim_access(current_user, db_claim)

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
def ask_explanation_question(
    req: QAChatRequest, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Interactive Q&A chat endpoint answering claimant questions about their specific decision."""
    db_claim = db.query(Claim).filter(Claim.id == req.claim_id).first()
    if not db_claim:
        raise HTTPException(status_code=404, detail=f"Claim {req.claim_id} not found.")
        
    assert_claim_access(current_user, db_claim)

    import uuid
    user_msg_id = f"MSG-{uuid.uuid4().hex[:8].upper()}"
    db.add(ChatMessage(id=user_msg_id, claim_id=req.claim_id, role="user", content=req.user_question))
    db.commit()

    try:
        from services.llm_service import get_chat_llm
        llm = get_chat_llm()
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"Failed to load llm: {e}")
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
        try:
            answer = llm.invoke([HumanMessage(content=prompt)]).content
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Failed to invoke llm: {e}")
            answer = (
                f"Your claim {db_claim.claim_number} was reviewed against policy terms and billing standards. "
                f"The current approved amount is ${db_claim.approved_amount:,.2f}."
            )

    ast_msg_id = f"MSG-{uuid.uuid4().hex[:8].upper()}"
    db.add(ChatMessage(id=ast_msg_id, claim_id=req.claim_id, role="assistant", content=answer))
    db.commit()

    return QAChatResponse(
        claim_id=req.claim_id,
        question=req.user_question,
        answer=answer,
        sources=["Policy Terms & Conditions", "Adjudication Decision Audit Trail"],
    )
