# Debate/Reconciliation Agent (`debate_agent`)

## Purpose
The Debate/Reconciliation Agent hosts an internal 3-node adversarial reasoning process (`pro_approval_node` -> `pro_denial_node` -> `reconcile_node`) whenever policy coverage and medical coding findings exhibit conflicting signals.

## Internal Subgraph Architecture
1. **`pro_approval_node`**: Formulates arguments in favor of claim approval based on policy clauses and precedents.
2. **`pro_denial_node`**: Formulates arguments in favor of claim denial/restriction based on CPT/ICD mismatches and exclusions.
3. **`reconcile_node`**: Scores argument weights, synthesizes a balanced recommendation, and generates a structured `debate_transcript`.

## Shared Graph State Slice
- **Reads**: `policy_clauses`, `precedent_cases`, `code_mismatches`, `exclusion_triggers`, `unusual_charges`.
- **Writes**: `pro_arguments`, `con_arguments`, `conflict_resolution`, `reconciliation_recommendation`, `confidence_delta`, `debate_transcript`.

## Owned Tools
- `evaluate_argument_strength`: Scores argument weights based on evidence density.
- `summarize_debate_transcript`: Generates formatted transcript object.

## Known Edge Cases & Limitations
- If code mismatches exist alongside strong policy coverage, defaults to `PARTIAL_APPROVE` with allowed fee caps.

## Example Trace
```json
// Input State:
{
  "code_mismatches": ["CPT 93000 lacks medical necessity..."],
  "policy_clauses": [{"clause_title": "Outpatient Coverage"}]
}

// Node Output:
{
  "reconciliation_recommendation": "PARTIAL_APPROVE",
  "conflict_resolution": "Resolved via debate: Code mismatches detected. Recommend PARTIAL_APPROVE...",
  "confidence_delta": 0.35
}
```
