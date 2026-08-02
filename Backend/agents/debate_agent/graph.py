from typing import Dict, Any
from agents.debate_agent.tools import evaluate_argument_strength, summarize_debate_transcript

def pro_approval_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Internal step 1: Generates Pro-Approval arguments."""
    clauses = state.get("policy_clauses", [])
    precedents = state.get("precedent_cases", [])
    rate = state.get("historical_approval_rate", 0.5)

    pro_args = [
        f"Policy provides coverage under active clause provisions ({len(clauses)} clauses verified).",
        f"Historical precedents demonstrate a {int(rate*100)}% approval rate for similar diagnostic presentations."
    ]
    return {"pro_arguments": pro_args}

def pro_denial_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Internal step 2: Generates Pro-Denial / Restriction arguments."""
    mismatches = state.get("code_mismatches", [])
    exclusions = state.get("exclusion_triggers", [])
    unusual = state.get("unusual_charges", [])

    con_args = []
    if mismatches:
        con_args.extend(mismatches)
    if exclusions:
        con_args.extend(exclusions)
    if unusual:
        con_args.extend(unusual)

    if not con_args:
        con_args.append("No medical coding mismatches or policy exclusion triggers found.")

    return {"con_arguments": con_args}

def reconcile_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Internal step 3: Reconciles Pro and Con arguments into a final synthesis."""
    pro_args = state.get("pro_arguments", [])
    con_args = state.get("con_arguments", [])
    mismatches = state.get("code_mismatches", [])

    pro_score = evaluate_argument_strength.invoke({"arguments": pro_args, "evidence_count": len(state.get("policy_clauses", []))})
    con_score = evaluate_argument_strength.invoke({"arguments": con_args, "evidence_count": len(mismatches)})

    if mismatches:
        recommendation = "PARTIAL_APPROVE" if pro_score > con_score else "DENY"
        resolution = f"Resolved via debate: Code mismatches detected ({len(mismatches)}). Recommend {recommendation} with itemized fee schedule restrictions."
    else:
        recommendation = "APPROVE"
        resolution = "Resolved via debate: Pro-approval evidence outweighs denial factors. Recommend APPROVE."

    transcript = summarize_debate_transcript.invoke({
        "pro_args": pro_args,
        "con_args": con_args,
        "resolution": resolution
    })

    return {
        "pro_arguments": pro_args,
        "con_arguments": con_args,
        "conflict_resolution": resolution,
        "reconciliation_recommendation": recommendation,
        "confidence_delta": round(abs(pro_score - con_score), 2),
        "debate_transcript": transcript,
        "last_completed_agent": "debate_agent",
        "status": "DEBATE_RECONCILED"
    }

def debate_agent_subgraph(state: Dict[str, Any]) -> Dict[str, Any]:
    """Full internal workflow execution wrapper for Debate Agent."""
    step1 = pro_approval_node(state)
    state.update(step1)

    step2 = pro_denial_node(state)
    state.update(step2)

    step3 = reconcile_node(state)
    return step3
