# Compliance & Guardrail Agent (`compliance_guardrail_agent`)

## Purpose
The Compliance & Guardrail Agent acts as the safety and legal audit node, evaluating draft decisions against regulatory mandates, legal notification requirements, and human-in-the-loop threshold rules.

## Shared Graph State Slice
- **Reads**: `claimed_amount`, `complexity_score`, `draft_decision`, `decision_type`, `rationale`.
- **Writes**: `compliance_passed`, `compliance_flags`, `human_review_required`, `human_review_reason`, `final_decision`, `status`.

## Owned Tools
- `check_statutory_mandates`: Verifies statutory disclaimer and consumer appeal rights presence.
- `evaluate_human_review_threshold`: Assesses whether dollar amounts (>= $5,000) or high complexity (>= 7.0) require manual human approval.

## Known Edge Cases & Limitations
- If `human_review_required` is `true`, graph execution pauses using LangGraph checkpointer interrupts until an adjudicator posts an approval via the API.

## Example Trace
```json
// Input State:
{
  "claimed_amount": 6200.00,
  "complexity_score": 7.4,
  "draft_decision": {"decision_type": "PARTIAL_APPROVE"}
}

// Node Output:
{
  "compliance_passed": true,
  "human_review_required": true,
  "compliance_flags": [
    "Claim amount $6,200.00 exceeds auto-approval threshold ($5,000.00).",
    "Complexity score 7.4 exceeds human review threshold (7.0)."
  ],
  "status": "PAUSED_FOR_HUMAN_REVIEW"
}
```
