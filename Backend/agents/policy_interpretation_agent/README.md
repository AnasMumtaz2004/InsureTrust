# Policy Interpretation Agent (`policy_interpretation_agent`)

## Purpose
The Policy Interpretation Agent consumes agent-agnostic RAG infrastructure to retrieve relevant policy clauses and exclusions, matching them against claim diagnoses and procedure codes.

## Shared Graph State Slice
- **Reads**: `description`, `diagnosis_codes`, `procedure_codes`, `policy_number`, `product_line`.
- **Writes**: `policy_clauses`, `coverage_status`, `exclusion_triggers`, `policy_interpretation_notes`.

## Owned Tools
- `retrieve_policy_clauses`: Consumes `rag/retrievers/policy_retriever.py` to search vector stores.
- `check_exclusion_triggers`: Evaluates clause wording against diagnostic codes for waiting period / pre-existing condition exclusions.

## Known Edge Cases & Limitations
- Requires pre-indexed policy documents in vector store; falls back to default policy clause templates if vector store is uninitialized.

## Example Trace
```json
// Input State:
{
  "description": "Patient back pain treatment",
  "diagnosis_codes": ["M54.5"]
}

// Node Output:
{
  "coverage_status": "COVERED",
  "policy_clauses": [
    {
      "clause_title": "Outpatient Diagnostic Services Coverage",
      "content": "Outpatient laboratory procedures are covered at 80% coinsurance..."
    }
  ],
  "exclusion_triggers": []
}
```
