from agents.policy_interpretation_agent.tools import check_exclusion_triggers
from agents.orchestration_agent.tools import detect_conflict
from agents.debate_agent.graph import reconcile_node
from agents.decision_drafting_agent.graph import decision_drafting_node


def test_exclusion_triggers_scan_clause_content():
    clauses = [{
        "clause_title": "General Exclusions",
        "content": "This policy excludes diagnosis code J45.9 when diagnosed prior to policy inception.",
    }]

    exclusions = check_exclusion_triggers.invoke({
        "clauses": clauses,
        "diagnosis_codes": ["J45.9"],
    })

    assert exclusions
    assert "pre-existing" in exclusions[0].lower() or "exclusion" in exclusions[0].lower()


def test_detect_conflict_ignores_exclusion_trigger_strings():
    conflicts = detect_conflict.invoke({
        "coverage_status": "EXCLUDED",
        "code_mismatches": [],
        "exclusion_triggers": ["Pre-existing condition requires review"],
        "unusual_charges": [],
    })

    assert conflicts == ["Policy interpretation flagged EXCLUDED coverage status."]


def test_reconcile_node_denies_when_excluded_without_mismatches():
    state = {
        "policy_clauses": [{"id": "POL-1", "clause_title": "Pre-existing Conditions"}],
        "coverage_status": "EXCLUDED",
        "code_mismatches": [],
        "exclusion_triggers": ["Pre-existing condition requires review"],
        "unusual_charges": [],
        "pro_arguments": ["Policy supports coverage."],
        "con_arguments": ["Coverage is excluded by policy."],
    }

    result = reconcile_node(state)

    assert result["reconciliation_recommendation"] == "DENY"


def test_decision_rationale_mentions_right_to_request_for_denial():
    state = {
        "claim_id": "CLM-100",
        "claimed_amount": 2500,
        "allowed_total": 0,
        "reconciliation_recommendation": "DENY",
        "coverage_status": "EXCLUDED",
        "code_mismatches": ["Mismatch"],
        "policy_clauses": [{"id": "POL-1", "clause_title": "Exclusions"}],
        "precedent_cases": [],
        "conflict_resolution": "Coverage excluded.",
    }

    result = decision_drafting_node(state)

    assert "right to request" in result["rationale"].lower()
