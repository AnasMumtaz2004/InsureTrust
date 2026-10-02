from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from database.database import get_db
from database.models import Claim, ChatMessage, User
from database.enums import Role
from schemas.claims import ClaimSubmissionRequest, ClaimResponse, ClaimDetailResponse
from services.claim_service import ClaimService
from graph.main_graph import claims_graph
from config import settings
from api.deps import get_current_user, assert_claim_access

try:
    from langchain_core.messages import HumanMessage
except ImportError:
    HumanMessage = None

router = APIRouter(prefix="/claims", tags=["Claims Adjudication"])

@router.post("/submit", response_model=ClaimResponse, status_code=status.HTTP_201_CREATED)
def submit_claim(
    req: ClaimSubmissionRequest, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Submits an incoming insurance claim and triggers the multi-agent graph execution."""
    req_dict = req.dict()
    
    if current_user.role == Role.CUSTOMER.value:
        req_dict["claimant_id"] = current_user.id
    elif not req_dict.get("claimant_id"):
        req_dict["claimant_id"] = current_user.id

    service = ClaimService(db)
    result = service.submit_and_process_claim(req_dict)

    db_claim = db.query(Claim).filter(Claim.id == result["claim_id"]).first()
    if not db_claim:
        raise HTTPException(status_code=500, detail="Failed to persist claim submission.")
    return db_claim

@router.get("", response_model=List[ClaimResponse])
def list_claims(
    limit: int = Query(50, ge=1, le=200), 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Lists submitted claims."""
    query = db.query(Claim)
    if current_user.role == Role.CUSTOMER.value:
        query = query.filter(Claim.claimant_id == current_user.id)
    
    claims = query.order_by(Claim.created_at.desc()).limit(limit).all()
    return claims


@router.post("/{claim_id}/chat")
def claim_chat(
    claim_id: str, 
    payload: dict, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail=f"Claim {claim_id} not found.")
        
    assert_claim_access(current_user, claim)

    message = payload.get("message", "") or ""
    if not message:
        raise HTTPException(status_code=400, detail="A message is required.")

    import uuid
    user_msg_id = f"MSG-{uuid.uuid4().hex[:8].upper()}"
    db.add(ChatMessage(id=user_msg_id, claim_id=claim_id, role="user", content=message))
    db.commit()

    try:
        from services.llm_service import get_chat_llm
        llm = get_chat_llm()
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"Failed to load llm: {e}")
        answer = "I can help summarize your claim and explain next steps. Please ask a specific question about coverage, status, or required documents."
    else:
        prompt = (
            "You are a helpful insurance assistant for policyholders. "
            f"The claim number is {claim.claim_number}. "
            f"Current status is {claim.status}. "
            f"Answer the user's message clearly and briefly. "
            f"User message: {message}"
        )
        try:
            answer = llm.invoke([HumanMessage(content=prompt)]).content
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Failed to invoke llm: {e}")
            answer = "I can help summarize your claim and explain next steps. Please ask a specific question about coverage, status, or required documents."

    ast_msg_id = f"MSG-{uuid.uuid4().hex[:8].upper()}"
    db.add(ChatMessage(id=ast_msg_id, claim_id=claim_id, role="assistant", content=answer))
    db.commit()

    return {"reply": answer}

@router.get("/{claim_id}", response_model=ClaimDetailResponse)
def get_claim_details(
    claim_id: str, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieves full claim details including complete LangGraph snapshot state."""
    db_claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not db_claim:
        raise HTTPException(status_code=404, detail=f"Claim {claim_id} not found.")
        
    assert_claim_access(current_user, db_claim)

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
