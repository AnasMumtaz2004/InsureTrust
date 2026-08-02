# Decision Drafting Agent (`decision_drafting_agent`)

## Purpose
The Decision Drafting Agent synthesizes policy findings, medical audits, precedent cases, and debate resolutions into a formal decision letter featuring itemized payout calculations and legal citations.

## Shared Graph State Slice
- **Reads**: `claim_id`, `claimed_amount`, `allowed_total`, `reconciliation_recommendation`, `policy_clauses`, `precedent_cases`, `conflict_resolution`.
- **Writes**: `draft_decision`, `decision_type`, `approved_amount`, `rationale`, `citations`, `itemized_payout`.

## Owned Tools
- `format_legal_citations`: Formats explicit policy and precedent citation references.
- `compute_final_payout_schedule`: Calculates itemized financial payouts and deductible deductions.

## Known Edge Cases & Limitations
- All draft decisions are submitted to `compliance_guardrail_agent` before finalization.

## Example Trace
```json
// Input State:
{
  "claim_id": "CLM-99120",
  "claimed_amount": 3450.00,
  "allowed_total": 2800.00,
  "reconciliation_recommendation": "PARTIAL_APPROVE"
}

// Node Output:
{
  "decision_type": "PARTIAL_APPROVE",
  "approved_amount": 2800.00,
  "rationale": "Based on automated multi-agent analysis for Claim CLM-99120...",
  "citations": ["Policy Clause Ref [POL-GENERAL-COV-02]: Outpatient Coverage"]
}
```
